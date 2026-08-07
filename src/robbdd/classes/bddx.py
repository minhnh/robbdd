# SPDX-License-Identifier: MPL-2.0
from typing import Any

from rdflib import URIRef
from scene_dsl.classes.common import IHasNamespace, IHasNamespaceDeclare
from scene_dsl.classes.scenex import SceneInstance

from robbdd.classes.bdd import HoldsExpr, ScenarioVariant


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
    target: Any | None

    def __init__(self, parent, name, provider, target=None) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.provider = provider
        self.target = target

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


class ObservationPolicy(IHasNamespaceDeclare):
    fluent_ref: Any
    observations: list[Observation]
    policy_spec: Any
    fluent: HoldsExpr
    policy_horizon: Any | None

    def __init__(
        self, parent, ns, name, fluent_ref, policy_horizon, observations, policy_spec
    ) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.observations = observations
        self.policy_spec = policy_spec
        self.fluent_ref = fluent_ref
        self.fluent = fluent_ref.fluent
        self.policy_horizon = policy_horizon


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
