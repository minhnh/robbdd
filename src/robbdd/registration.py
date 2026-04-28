# SPDX-License-Identifier: MPL-2.0
import sys
from os import makedirs
from os.path import abspath, basename, dirname, exists, join, splitext
from typing import Any
from urllib.error import HTTPError
from rdflib.namespace import NamespaceManager
from rdflib.plugin import PluginException
from textx import LanguageDesc, GeneratorDesc, metamodel_from_file
import textx.scoping.providers as scoping_providers
from rdf_utils.naming import get_valid_filename, get_valid_var_name
from rdf_utils.resolver import install_resolver
from bdd_dsl.models.clauses import FluentClauseModel, WhenBehaviourModel
from bdd_dsl.models.user_story import ScenarioVariantModel, UserStoryLoader
from bdd_dsl.representation import (
    get_clause_role_rep,
    get_str_tc_after_event,
    get_str_tc_before_event,
    get_str_tc_during_events,
    get_tmpl_bhv_pickplace,
    get_tmpl_fc_config,
    get_tmpl_fc_is_held,
    get_tmpl_fc_located_at,
    get_tmpl_fc_move_safe,
    get_tmpl_fc_sorted,
    get_tmpl_fc_str_tmpl,
)
from bdd_dsl.behave import get_behave_annotation
from bdd_dsl.utils.jinja import load_template, prepare_jinja2_template_data
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
JINJA_TMPL_DIR = join(CWD, "templates")
__GRAPH_FORMAT_EXT = {"json-ld": "json", "ttl": "ttl", "xml": "xml"}
__DEFAULT_MODEL_GRAPH_FILENAME = "model_graph.json"

__FLUENT_TMPL_CREATORS = [
    get_tmpl_fc_located_at,
    get_tmpl_fc_is_held,
    get_tmpl_fc_move_safe,
    get_tmpl_fc_sorted,
    get_tmpl_fc_str_tmpl,
    get_tmpl_fc_config,
]
__TIME_STR_GENS = [
    get_str_tc_before_event,
    get_str_tc_after_event,
    get_str_tc_during_events,
]


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


def __write_output_file(file_path: str, content: str, overwrite: bool):
    if exists(file_path) and not overwrite:
        print(f"not overwriting existing file '{file_path}'")
        return

    with open(file_path, "w", encoding="utf-8") as outfile:
        outfile.write(content)
    print(f"... wrote {file_path}")


def __load_bdd_user_story_data(model):
    g = create_bdd_model_graph(model=model)

    install_resolver()
    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    return g, us_loader


def __get_template(model: Any, creators: list[Any], **kwargs: Any):
    for creator in creators:
        tmpl = creator(model=model, **kwargs)
        if tmpl is not None:
            return tmpl
    raise ValueError(f"no template creator matched model '{model.id}' with types {model.types}")


def __build_step_data(
    decorator: str,
    annotation: str,
    args: list[str],
    model_id,
    ns_manager,
    used_function_names: set[str] | None,
) -> dict[str, Any]:
    function_name = __get_unique_step_function_name(
        decorator=decorator,
        model_id=model_id,
        ns_manager=ns_manager,
        used_function_names=used_function_names,
    )
    return {
        "decorator": decorator,
        "annotation": annotation,
        "annotation_literal": repr(annotation),
        "args": args,
        "function_name": function_name,
    }


def __get_unique_step_function_name(decorator, model_id, ns_manager, used_function_names) -> str:
    short_id = model_id.n3(namespace_manager=ns_manager)
    base_name = get_valid_var_name(short_id).strip("_").lower()
    if base_name == "":
        base_name = "step"
    if base_name[0].isdigit():
        base_name = f"step_{base_name}"

    function_name = f"{decorator}_{base_name}"
    if function_name not in used_function_names:
        used_function_names.add(function_name)
        return function_name

    suffix = 2
    while f"{function_name}_{suffix}" in used_function_names:
        suffix += 1

    unique_name = f"{function_name}_{suffix}"
    used_function_names.add(unique_name)
    return unique_name


def __get_time_constraint_annotation(
    clause: FluentClauseModel, ns_manager: NamespaceManager
) -> str:
    for tc_gen in __TIME_STR_GENS:
        tc_annotation = tc_gen(model=clause, ns_manager=ns_manager)
        if tc_annotation is not None:
            return tc_annotation
    raise ValueError(f"no time constraint renderer matched clause '{clause.id}'")


def __get_fluent_step_data(
    scenario_variant: ScenarioVariantModel,
    clause: FluentClauseModel,
    ns_manager: NamespaceManager,
    used_function_names: set[str],
) -> dict[str, Any]:
    role = get_clause_role_rep(scenario_variant.scenario, clause).lower()
    clause_tmpl = __get_template(
        clause,
        __FLUENT_TMPL_CREATORS,
        ns_manager=ns_manager,
    )
    clause_annotation, clause_args = get_behave_annotation(clause_tmpl)
    tc_annotation = __get_time_constraint_annotation(clause=clause, ns_manager=ns_manager)
    annotation = f"{clause_annotation} {tc_annotation}"
    return __build_step_data(
        role,
        annotation,
        clause_args,
        clause.id,
        ns_manager,
        used_function_names,
    )


def __get_when_step_data(
    when_bhv: WhenBehaviourModel, ns_manager: NamespaceManager, used_function_names: set[str]
) -> dict[str, Any]:
    bhv_tmpl = get_tmpl_bhv_pickplace(model=when_bhv)
    if bhv_tmpl is None:
        raise ValueError(
            f"no behave step template for behaviour '{when_bhv.behaviour.id}' with types {when_bhv.behaviour.types}"
        )

    annotation, args = get_behave_annotation(bhv_tmpl)
    return __build_step_data(
        "when",
        annotation,
        args,
        when_bhv.behaviour.id,
        ns_manager,
        used_function_names,
    )


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
    g, us_loader = __load_bdd_user_story_data(model=model)

    processed_bdd_data = prepare_jinja2_template_data(us_loader, g)
    feature_template = load_template("robbdd.feature.jinja", JINJA_TMPL_DIR)
    for us_data in processed_bdd_data:
        us_name = us_data["name"]
        feature_content = feature_template.render(data=us_data)
        feature_filename = f"{get_valid_filename(us_name)}.feature"
        filepath = join("" if output_path is None else output_path, feature_filename)
        with open(filepath, mode="w", encoding="utf-8") as of:
            of.write(feature_content)
        print(f"... wrote {filepath}")


def behave_gen(metamodel, model, output_path, overwrite, debug):
    g, us_loader = __load_bdd_user_story_data(model=model)

    output_dir = "." if output_path is None else output_path
    makedirs(output_dir, exist_ok=True)
    steps_dir = join(output_dir, "steps")
    makedirs(steps_dir, exist_ok=True)

    gherkin_gen(
        metamodel=metamodel, model=model, output_path=output_dir, overwrite=overwrite, debug=debug
    )

    graph_content = g.serialize(format="json-ld", auto_compact=True)
    __write_output_file(
        file_path=join(output_dir, __DEFAULT_MODEL_GRAPH_FILENAME),
        content=graph_content,
        overwrite=overwrite,
    )

    scenario_variants = []
    for _, var_ids in us_loader.get_us_scenario_variants().items():
        for var_id in var_ids:
            scenario_variants.append(
                us_loader.load_scenario_variant(full_graph=g, variant_id=var_id)
            )

    env_template = load_template(
        "robbdd.behave.environment.py.jinja",
        JINJA_TMPL_DIR,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    steps_template = load_template(
        "robbdd.behave.steps.py.jinja",
        JINJA_TMPL_DIR,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    used_function_names = set()

    __write_output_file(
        file_path=join(output_dir, "environment.py"),
        content=env_template.render(model_graph_filename=__DEFAULT_MODEL_GRAPH_FILENAME),
        overwrite=overwrite,
    )
    __write_output_file(
        file_path=join(steps_dir, "generated_steps.py"),
        content=steps_template.render(
            scenario_variants=scenario_variants,
            get_fluent_step_data=lambda scenario_variant, clause: __get_fluent_step_data(
                scenario_variant,
                clause,
                g.namespace_manager,
                used_function_names,
            ),
            get_when_step_data=lambda when_bhv: __get_when_step_data(
                when_bhv,
                g.namespace_manager,
                used_function_names,
            ),
        ),
        overwrite=overwrite,
    )


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
robbdd_behave_gen = GeneratorDesc(
    language="robbdd",
    target="behave",
    description="Generate a behave package from RobBDD models",
    generator=behave_gen,
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
