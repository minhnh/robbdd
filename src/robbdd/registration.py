import sys
from os.path import abspath, basename, dirname, exists, join, splitext
from urllib.error import HTTPError
from rdflib.plugin import PluginException
from textx import (
    LanguageDesc,
    GeneratorDesc,
    get_children_of_type,
    get_model,
    metamodel_from_file,
    textx_isinstance,
)
import textx.scoping.providers as scoping_providers
from rdf_utils.naming import get_valid_filename
from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import load_template_from_file, prepare_jinja2_template_data
from robbdd.classes.bdd import (
    AfterEvent,
    BeforeEvent,
    Behaviour,
    CartesianProductVariation,
    Clause,
    Combination,
    ExplicitSet,
    Permutation,
    DuringEvent,
    Event,
    ExistsExpr,
    FluentAndExpr,
    FluentLogicExpr,
    FluentNotExpr,
    FluentOrExpr,
    ForAllExpr,
    GivenExpr,
    GivenWhenThenExpr,
    HoldsExpr,
    ScenarioSetVariable,
    ScenarioVariable,
    ScenarioVariant,
    TableVariation,
    Task,
    TaskVariation,
    ThenExpr,
    TimeConstraint,
    UserStory,
    ScenarioTemplate,
    VariableBase,
    WhenBehaviourClause,
    WhenExpr,
)
from robbdd.classes.common import SetBase
from robbdd.classes.scene import (
    Agent,
    AgentSet,
    Object,
    ObjectSet,
    SceneModel,
    Workspace,
    WorkspaceComposition,
    WorkspaceSet,
)
from robbdd.graph import create_bdd_model_graph, create_scene_model_graph


CWD = abspath(dirname(__file__))
__GRAPH_FORMAT_EXT = {"json-ld": "json", "ttl": "ttl", "xml": "xml"}


def _iter_fluent_refs(root_model):
    for template in get_children_of_type("ScenarioTemplate", root_model):
        template_name = getattr(template, "name", None)
        if not template_name:
            continue

        for fluent in get_children_of_type("HoldsExpr", template):
            fluent_name = getattr(fluent, "name", None)
            if fluent_name:
                yield f"{template_name}.{fluent_name}", fluent


class HoldsExprRefScopeProvider:
    def __init__(self):
        self._import_loader = scoping_providers.FQNImportURI()

    def __call__(self, obj, attr, obj_ref):
        model = get_model(obj)
        self._import_loader.load_models(model)

        candidate_models = [model]
        if hasattr(model, "_tx_model_repository"):
            candidate_models.extend(model._tx_model_repository.local_models)

        for candidate_model in candidate_models:
            for fqn, fluent in _iter_fluent_refs(candidate_model):
                if fqn == obj_ref.obj_name and textx_isinstance(fluent, obj_ref.cls):
                    return fluent

        return None


def scene_metamodel():
    mm_scene = metamodel_from_file(
        join(CWD, "grammars", "scene.tx"),
        classes=[
            Object,
            Workspace,
            Agent,
            ObjectSet,
            WorkspaceSet,
            AgentSet,
            WorkspaceComposition,
            SceneModel,
        ],
    )
    mm_scene.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )
    return mm_scene


def bdd_metamodel():
    mm_bdd = metamodel_from_file(
        join(CWD, "grammars", "bdd.tx"),
        classes=[
            UserStory,
            ScenarioVariant,
            ScenarioTemplate,
            Behaviour,
            Event,
            Task,
            VariableBase,
            SetBase,
            ExplicitSet,
            Combination,
            Permutation,
            ScenarioVariable,
            ScenarioSetVariable,
            TaskVariation,
            TableVariation,
            CartesianProductVariation,
            WhenBehaviourClause,
            ForAllExpr,
            GivenExpr,
            WhenExpr,
            ThenExpr,
            GivenWhenThenExpr,
            Clause,
            ExistsExpr,
            FluentLogicExpr,
            HoldsExpr,
            FluentAndExpr,
            FluentOrExpr,
            FluentNotExpr,
            TimeConstraint,
            BeforeEvent,
            AfterEvent,
            DuringEvent,
        ],
    )
    mm_bdd.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )
    return mm_bdd


def bddx_metamodel():
    mm_bddx = metamodel_from_file(join(CWD, "grammars", "bddx.tx"))
    mm_bddx.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
            "HoldsExprRef.fluent": HoldsExprRefScopeProvider(),
        }
    )
    return mm_bddx


scene_lang = LanguageDesc(
    "robbdd-scene",
    pattern="*.scene",
    description="Language for describing robotic scenes",
    metamodel=scene_metamodel,
)
bdd_lang = LanguageDesc(
    "robbdd",
    pattern="*.bdd",
    description="Behaviour-Driven Development language",
    metamodel=bdd_metamodel,
)
bddx_lang = LanguageDesc(
    "robbdd-exec",
    pattern="*.bddx",
    description="DSL for describing BDD execution",
    metamodel=bddx_metamodel,
)


def __parse_rdflib_serial_args(**kwargs):
    g_format = kwargs.get("format", "json-ld")
    assert (
        g_format in __GRAPH_FORMAT_EXT
    ), f"file extension not handled for graph format '{g_format}', try {list(__GRAPH_FORMAT_EXT.keys())}"

    ser_kwargs = {"format": g_format}
    if g_format == "json-ld":
        if "nocompact" in kwargs:
            ser_kwargs["auto_compact"] = False
        else:
            ser_kwargs["auto_compact"] = True
    return ser_kwargs


def bdd_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    g = create_bdd_model_graph(model=model)
    try:
        print(g.serialize(**ser_kwargs))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def bdd_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    filename = kwargs.get("filename", basename(model._tx_filename))
    if filename is None:
        filename = "graph"
    full_filename = f"{splitext(filename)[0]}.{__GRAPH_FORMAT_EXT[g_format]}"
    full_output_path = join("" if output_path is None else output_path, full_filename)
    if exists(full_output_path) and not overwrite:
        print(f"not overwriting existing file '{full_output_path}'")
        return

    g = create_bdd_model_graph(model=model)
    with open(full_output_path, "w") as outfile:
        outfile.write(g.serialize(**ser_kwargs))
    print(f"... wrote {full_output_path}")


def gherkin_gen(metamodel, model, output_path, overwrite, debug):
    g = create_bdd_model_graph(model=model)

    # resolver for caching remote models
    install_resolver()

    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    processed_bdd_data = prepare_jinja2_template_data(us_loader, g)
    feature_template = load_template_from_file(join(CWD, "templates", "robbdd.feature.jinja"))
    for us_data in processed_bdd_data:
        us_name = us_data["name"]
        feature_content = feature_template.render(data=us_data)
        feature_filename = f"{get_valid_filename(us_name)}.feature"
        filepath = join("" if output_path is None else output_path, feature_filename)
        with open(filepath, mode="w", encoding="utf-8") as of:
            of.write(feature_content)
        print(f"... wrote {filepath}")


def scene_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    g = create_scene_model_graph(model=model)
    try:
        print(g.serialize(**ser_kwargs))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def scene_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    filename = kwargs.get("filename", basename(model._tx_filename))
    if filename is None:
        filename = "graph"
    full_filename = f"{splitext(filename)[0]}.{__GRAPH_FORMAT_EXT[g_format]}"
    full_output_path = join("" if output_path is None else output_path, full_filename)
    if exists(full_output_path) and not overwrite:
        print(f"not overwriting existing file '{full_output_path}'")
        return

    g = create_scene_model_graph(model=model)
    with open(full_output_path, "w") as outfile:
        outfile.write(g.serialize(**ser_kwargs))
    print(f"... wrote {full_output_path}")


robbdd_console_gen = GeneratorDesc(
    language="robbdd",
    target="console",
    description="Print a representation of RobBDD model graph to the console, default format is JSON-LD",
    generator=bdd_graph_gen_console,
)
robbdd_graph_gen = GeneratorDesc(
    language="robbdd",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD model graph, default format is JSON-LD",
    generator=bdd_graph_gen,
)
robbdd_gherkin_gen = GeneratorDesc(
    language="robbdd",
    target="gherkin",
    description="Generate Gherkin feature files from RobBDD models",
    generator=gherkin_gen,
)
robbdd_scene_console_gen = GeneratorDesc(
    language="robbdd-scene",
    target="console",
    description="Print a representation of RobBDD scene model graph to the console, default format is JSON-LD",
    generator=scene_graph_gen_console,
)
robbdd_scene_graph_gen = GeneratorDesc(
    language="robbdd-scene",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD scene model graph, default format is JSON-LD",
    generator=scene_graph_gen,
)
