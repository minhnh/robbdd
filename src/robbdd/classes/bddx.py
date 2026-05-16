# SPDX-License-Identifier: MPL-2.0
from typing import Any
from robbdd.classes.bdd import HoldsExpr, ScenarioVariant
from robbdd.classes.common import IHasNamespaceDeclare


class BehaviourImplementation(IHasNamespaceDeclare):
    bhv_spec: Any

    def __init__(self, parent, ns, name, bhv_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.bhv_spec = bhv_spec


class FluentImplementation(IHasNamespaceDeclare):
    fluent_ref: Any
    fl_spec: Any
    fluent: HoldsExpr

    def __init__(self, parent, ns, name, fluent_ref, fl_spec) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.fl_spec = fl_spec
        self.fluent_ref = fluent_ref
        self.fluent = fluent_ref.fluent


class ScenarioExecution(IHasNamespaceDeclare):
    variant: ScenarioVariant
    bhv_impl: BehaviourImplementation
    fluent_impls: list[FluentImplementation]

    def __init__(self, parent, ns, name, variant, bhv_impl, fluent_impls) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.variant = variant
        self.bhv_impl = bhv_impl
        self.fluent_impls = fluent_impls
