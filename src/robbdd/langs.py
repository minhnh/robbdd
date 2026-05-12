# SPDX-License-Identifier: MPL-2.0
from os.path import abspath, dirname, join
from textx import get_children_of_type, get_model, metamodel_from_file, textx_isinstance
import textx.scoping.providers as scoping_providers
from robbdd.classes.bddx import ScenarioExecution
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


__CWD = abspath(dirname(__file__))


def iter_fluent_refs(root_model):
    for template in get_children_of_type(ScenarioTemplate, root_model):
        template_name = getattr(template, "name", None)
        if not template_name:
            continue

        for fluent in get_children_of_type(HoldsExpr, template):
            fluent_name = getattr(fluent, "name", None)
            if fluent_name:
                yield f"{template_name}.{fluent_name}", fluent

    for variant in get_children_of_type(ScenarioVariant, root_model):
        variant_name = getattr(variant, "name", None)
        if not variant_name:
            continue

        for fluent in get_children_of_type(HoldsExpr, variant):
            fluent_name = getattr(fluent, "name", None)
            if fluent_name:
                yield f"{variant_name}.{fluent_name}", fluent


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
            for fqn, fluent in iter_fluent_refs(candidate_model):
                if fqn == obj_ref.obj_name and textx_isinstance(fluent, obj_ref.cls):
                    return fluent

        return None


def scene_metamodel():
    mm_scene = metamodel_from_file(
        join(__CWD, "grammars", "scene.tx"),
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
        join(__CWD, "grammars", "bdd.tx"),
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
    mm_bddx = metamodel_from_file(join(__CWD, "grammars", "bddx.tx"), classes=[ScenarioExecution])
    mm_bddx.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
            "HoldsExprRef.fluent": HoldsExprRefScopeProvider(),
        }
    )
    return mm_bddx
