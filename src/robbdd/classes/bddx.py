# SPDX-License-Identifier: MPL-2.0
from typing import Any
from robbdd.classes.bdd import HoldsExpr, ScenarioVariant
from robbdd.classes.common import IHasNamespaceDeclare


class BehaviourImplementation(IHasNamespaceDeclare):
    bhv_spec: Any

    def __init__(self, parent, ns, name, bhv_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.bhv_spec = bhv_spec


class ObservationPolicy(IHasNamespaceDeclare):
    fluent_ref: Any
    obs_spec: Any
    fluent: HoldsExpr

    def __init__(self, parent, ns, name, fluent_ref, obs_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.obs_spec = obs_spec
        self.fluent_ref = fluent_ref
        self.fluent = fluent_ref.fluent


class ScenarioExecution(IHasNamespaceDeclare):
    variant: ScenarioVariant
    bhv_impl: BehaviourImplementation
    obs_policies: list[ObservationPolicy]

    def __init__(self, parent, ns, name, variant, bhv_impl, obs_policies) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.variant = variant
        self.bhv_impl = bhv_impl
        self.obs_policies = obs_policies
