# SPDX-License-Identifier: MPL-2.0
from typing import Any
from robbdd.classes.bdd import ScenarioVariant
from robbdd.classes.common import IHasNamespaceDeclare


class ScenarioExecution(IHasNamespaceDeclare):
    variants: list[ScenarioVariant]
    bhv_impl: Any
    fluent_impls: list[Any]

    def __init__(self, parent, ns, name, variants, bhv_impl, fluent_impls) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.variants = variants
        self.bhv_impl = bhv_impl
        self.fluent_impls = fluent_impls
