from os.path import abspath, dirname, join
from textx import LanguageDesc, GeneratorDesc, metamodel_from_file
import textx.scoping.providers as scoping_providers
from textxjinja import textx_jinja_generator
from bdd_textx.classes.bdd import (
    AfterEvent,
    BeforeEvent,
    Behaviour,
    CartesianProductVariation,
    Clause,
    Combination,
    Permutation,
    ConstantSet,
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
    SetBase,
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
from bdd_textx.classes.scene import Agent, Object, SceneModel, Workspace
from bdd_textx.graph import create_bdd_model_graph
from bdd_textx.generator.utils import prepare_context_data


CWD = abspath(dirname(__file__))


def scene_metamodel():
    mm_scene = metamodel_from_file(
        join(CWD, "grammars", "scene.tx"),
        classes=[Object, Workspace, Agent, SceneModel],
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
            ConstantSet,
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
    "scene-tx",
    pattern="*.scene",
    description="Language for describing robotic scenes",
    metamodel=scene_metamodel,
)
bdd_lang = LanguageDesc(
    "bdd-tx",
    pattern="*.bdd",
    description="Behaviour-Driven Development language",
    metamodel=bdd_metamodel,
)


def generator(metamodel, model, output_path, overwrite, debug):
    _ = create_bdd_model_graph(model=model)
    template_folder = join(CWD, "generator", "template")
    context = prepare_context_data(metamodel, model)
    textx_jinja_generator(template_folder, output_path, context, overwrite)


bddtx_jsonld_generator = GeneratorDesc(
    language="bdd-tx",
    target="json-ld",
    description="Generate JSON-LD from BDD models",
    generator=generator,
)
