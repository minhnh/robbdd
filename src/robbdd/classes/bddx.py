# SPDX-License-Identifier: MPL-2.0
from typing import Any

from rdflib import Namespace, URIRef
from scene_dsl.classes.common import IHasNamespace, IHasNamespaceDeclare
from scene_dsl.classes.scene import Agent as ScnAgent
from scene_dsl.classes.scene import Object as ScnObject
from scene_dsl.classes.scene import Workspace as ScnWorkspace
from scene_dsl.classes.scenex import SceneInstance

from robbdd.classes.bdd import HoldsExpr, ScenarioVariant, VariableBase


class BehaviourImplementation(IHasNamespaceDeclare):
    bhv_spec: Any

    def __init__(self, parent, ns, name, bhv_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.bhv_spec = bhv_spec


class ObservationProvider(IHasNamespaceDeclare):
    provider_spec: Any

    def __init__(self, parent, ns, name, provider_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.provider_spec = provider_spec


class Observation(IHasNamespace):
    provider: ObservationProvider
    target: VariableBase | ScnObject | ScnAgent | ScnWorkspace | None

    def __init__(
        self,
        parent,
        name,
        provider,
        var_target,
        obj_target,
        agn_target,
        ws_target,
    ) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.provider = provider
        self.var_target: VariableBase | None = var_target
        self.obj_target: ScnObject | None = obj_target
        self.agn_target: ScnAgent | None = agn_target
        self.ws_target: ScnWorkspace | None = ws_target
        self.target = var_target or obj_target or agn_target or ws_target

    @property
    def namespace(self):
        if not isinstance(self.parent, IHasNamespace):
            raise TypeError(
                f"Observation.namespace: parent '{self.parent}' of '{self.name}' is not a IHasNamespace"
            )
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        return self.namespace[self.name]


class RosTrinaryTopicPolicy:
    def __init__(self, parent, topic_name) -> None:
        self.parent = parent
        self.topic_name: str = topic_name


class EvaluatedObservationPolicy(IHasNamespace):
    observations: list[Observation]
    _policy_name: str | None

    def __init__(
        self,
        parent,
        observations,
        time_extractor,
        entity_mapper,
        evaluator,
    ) -> None:
        self.parent = parent
        self.observations = observations
        self.time_extractor = time_extractor
        self.entity_mapper = entity_mapper
        self.evaluator = evaluator
        self._policy_name = None

    @property
    def namespace(self) -> Namespace:
        if not isinstance(self.parent, IHasNamespace):
            raise TypeError(
                f"EvaluatedObservationPolicy.namespace: parent '{self.parent}' is not a IHasNamespace"
            )
        return self.parent.namespace

    @property
    def policy_name(self) -> str:
        if self._policy_name is not None:
            return self._policy_name

        if not isinstance(self.parent, ObservationPolicy):
            raise TypeError(
                f"EvaluatedObservationPolicy.policy_name: parent '{self.parent}' is not an ObservationPolicy"
            )
        self._policy_name = self.parent.name
        return self._policy_name

    @property
    def time_extractor_uri(self):
        return self.namespace[f"{self.policy_name}/time-extractor"]

    @property
    def entity_mapper_uri(self):
        return self.namespace[f"{self.policy_name}/entity-mapper"]

    @property
    def evaluator_uri(self):
        return self.namespace[f"{self.policy_name}/evaluator"]


class LinearDistanceEvaluator:
    parent: EvaluatedObservationPolicy

    def __init__(self, parent, constraint) -> None:
        if not isinstance(parent, EvaluatedObservationPolicy):
            raise TypeError(
                f"parent of LinearDistanceEvaluator is not an EvaluatedObservationPolicy: {parent}"
            )
        self.parent = parent
        self.constraint = constraint
        self._coord_uri: URIRef | None = None
        self._constraint_uri: URIRef | None = None
        self._lower_uri: URIRef | None = None
        self._upper_uri: URIRef | None = None
        self._ref_val_uri: URIRef | None = None
        self._tol_uri: URIRef | None = None

    @property
    def coordinate_uri(self) -> URIRef:
        if self._coord_uri is not None:
            return self._coord_uri

        self._coord_uri = self.parent.namespace[f"{self.parent.policy_name}/evaluator/coordinate"]
        return self._coord_uri

    @property
    def constraint_uri(self) -> URIRef:
        if self._constraint_uri is not None:
            return self._constraint_uri

        self._constraint_uri = self.parent.namespace[
            f"{self.parent.policy_name}/evaluator/constraint"
        ]
        return self._constraint_uri

    @property
    def lower_uri(self) -> URIRef:
        if self._lower_uri is not None:
            return self._lower_uri

        self._lower_uri = self.parent.namespace[
            f"{self.parent.policy_name}/evaluator/constraint/lower-threshold"
        ]
        return self._lower_uri

    @property
    def upper_uri(self) -> URIRef:
        if self._upper_uri is not None:
            return self._upper_uri

        self._upper_uri = self.parent.namespace[
            f"{self.parent.policy_name}/evaluator/constraint/upper-threshold"
        ]
        return self._upper_uri

    @property
    def ref_value_uri(self) -> URIRef:
        if self._ref_val_uri is not None:
            return self._ref_val_uri

        self._ref_val_uri = self.parent.namespace[
            f"{self.parent.policy_name}/evaluator/constraint/reference-value"
        ]
        return self._ref_val_uri

    @property
    def tolerance_uri(self) -> URIRef:
        if self._tol_uri is not None:
            return self._tol_uri

        self._tol_uri = self.parent.namespace[
            f"{self.parent.policy_name}/evaluator/constraint/tolerance"
        ]
        return self._tol_uri


class ObservationPolicy(IHasNamespaceDeclare):
    fluent_ref: Any
    fluent: HoldsExpr
    policy_horizon: Any | None
    policy_spec: RosTrinaryTopicPolicy | EvaluatedObservationPolicy

    def __init__(
        self,
        parent,
        ns,
        name,
        fluent_ref,
        policy_horizon,
        policy_spec,
    ) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.fluent_ref = fluent_ref
        self.fluent = fluent_ref.fluent
        self.policy_horizon = policy_horizon
        self.policy_spec = policy_spec


class ScenarioExecution(IHasNamespaceDeclare):
    variant: ScenarioVariant
    scene_inst: SceneInstance
    bhv_impl: BehaviourImplementation
    obs_policies: list[ObservationPolicy]

    def __init__(self, parent, ns, name, variant, scene_inst, bhv_impl, obs_policies) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.variant = variant
        self.scene_inst = scene_inst
        self.bhv_impl = bhv_impl
        self.obs_policies = obs_policies
