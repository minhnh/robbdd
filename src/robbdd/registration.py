import sys
from os.path import abspath, basename, dirname, exists, join, splitext
from urllib.error import HTTPError
from rdflib.plugin import PluginException
from textx import LanguageDesc, GeneratorDesc, metamodel_from_file
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
from robbdd.graph import create_bdd_model_graph


CWD = abspath(dirname(__file__))
__GRAPH_FORMAT_EXT = {"json-ld": "json", "ttl": "ttl", "xml": "xml"}


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


def graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    g_format = kwargs.get("format", "json-ld")

    g = create_bdd_model_graph(model=model)
    try:
        print(g.serialize(format=g_format))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    g_format = kwargs.get("format", "json-ld")
    assert (
        g_format in __GRAPH_FORMAT_EXT
    ), f"file extension not handled for graph format '{g_format}', try {list(__GRAPH_FORMAT_EXT.keys())}"

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
        outfile.write(g.serialize(format=g_format))
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


robbdd_console_gen = GeneratorDesc(
    language="robbdd",
    target="console",
    description="Print a representation of RobBDD model graph to the console, default format is JSON-LD",
    generator=graph_gen_console,
)
robbdd_graph_gen = GeneratorDesc(
    language="robbdd",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD model graph, default format is JSON-LD",
    generator=graph_gen,
)
robbdd_gherkin_gen = GeneratorDesc(
    language="robbdd",
    target="gherkin",
    description="Generate Gherkin feature files from RobBDD models",
    generator=gherkin_gen,
)
