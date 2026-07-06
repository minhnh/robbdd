# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generator, Optional
from rdflib import Namespace, URIRef
from scene_dsl.classes.common import (
    IHasNamespace,
    IHasNamespaceDeclare,
    IHasParent,
    IHasUUID,
    SetBase,
)
from scene_dsl.classes.scene import SceneModel


class Behaviour(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(parent=parent, ns=ns, name=name)


class Event(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(parent=parent, ns=ns, name=name)


class Task(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(parent=parent, ns=ns, name=name)


class ExplicitSet(SetBase, IHasNamespaceDeclare):
    def __init__(self, parent, ns, name, elems, **kwargs) -> None:
        super().__init__(parent=parent, name=name, ns=ns, **kwargs)
        self.elems = elems


class Combination(IHasUUID, IHasNamespace):
    length: int
    repeated: bool
    _uri: Optional[URIRef]

    def __init__(self, parent, length, repeated, from_set) -> None:
        super().__init__(parent=parent)
        self.length = length
        self.repeated = repeated
        self.from_set = from_set
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        # expect grandparent to be a TaskVariation
        assert self.parent is not None, f"Combination '{self.uri}' has None parent"
        assert isinstance(
            self.parent.parent, IHasNamespace
        ), f"grandparent of 'Combination' not instance of IHasNamespace: {self.parent.parent}"
        return self.parent.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"comb-{self.uuid}"]
        return self._uri


class Permutation(IHasUUID, IHasNamespace):
    length: int
    _uri: Optional[URIRef]

    def __init__(self, parent, length, from_set) -> None:
        super().__init__(parent=parent)
        self.length = length
        self.from_set = from_set
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        # expect grandparent to be a TaskVariation
        assert self.parent is not None, f"Permutation '{self.uri}' has None parent"
        assert isinstance(
            self.parent.parent, IHasNamespace
        ), f"grandparent of 'Permutation' not instance of IHasNamespace: {self.parent.parent}"
        return self.parent.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"perm-{self.uuid}"]
        return self._uri


class VariableBase(IHasParent):
    _uri: Optional[URIRef]

    def __init__(self, name, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = name
        self._uri = None

    @property
    def uri(self) -> URIRef:
        """URIRef corresponding to the variable's name.

        Inherits namespace from parent. This needs to be a property since textX doesn't/may not call
        the the constructor of parent classes before the creation of this class, resulting in the
        'ns' property not being available.
        """
        if self._uri is None:
            assert isinstance(
                self.parent, IHasNamespace
            ), f"parent of variable '{self.name}' not an instance of 'IHasNamespace': {self.parent}"
            self._uri = self.parent.namespace[f"var-{self.name}"]
        return self._uri


class ScenarioVariable(VariableBase):
    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent, name=name)


class ScenarioSetVariable(VariableBase, SetBase):
    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent, name=name)


class TimeConstraint(IHasNamespace):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of 'TimeConstraint' not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class BeforeEvent(TimeConstraint):
    event: Event
    horizon: Optional[Any]

    def __init__(self, parent, horizon, event) -> None:
        super().__init__(parent=parent)
        self.horizon = horizon
        self.event = event


class AfterEvent(TimeConstraint):
    event: Event
    horizon: Optional[Any]

    def __init__(self, parent, horizon, event) -> None:
        super().__init__(parent=parent)
        self.horizon = horizon
        self.event = event


class DuringEvent(TimeConstraint):
    start_event: Event
    end_event: Event

    def __init__(self, parent, start_event, end_event) -> None:
        super().__init__(parent=parent)
        self.start_event = start_event
        self.end_event = end_event


class Clause(IHasNamespace):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of 'Clause' not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class FluentLogicExpr(Clause):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)


class HoldsExpr(FluentLogicExpr):
    tc: TimeConstraint
    _uri: Optional[URIRef]

    def __init__(self, parent, name, predicate, tc) -> None:
        self.name = name
        self.predicate = predicate
        self.tc = tc
        self._uri = None
        super().__init__(parent=parent)

    def __str__(self) -> str:
        return f"<({self.__class__.__name__}) {self.uri}>"

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class IHasHoldsExpr(ABC):
    @abstractmethod
    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]: ...


class FluentAndExpr(FluentLogicExpr, IHasHoldsExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, expressions) -> None:
        super().__init__(parent=parent)
        self.expressions = expressions

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        for exp in self.expressions:
            if isinstance(exp, HoldsExpr):
                yield exp
            elif isinstance(exp, IHasHoldsExpr):
                yield from exp.get_holds_exprs()


class FluentOrExpr(FluentLogicExpr, IHasHoldsExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, expressions) -> None:
        super().__init__(parent=parent)
        self.expressions = expressions

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        for exp in self.expressions:
            if isinstance(exp, HoldsExpr):
                yield exp
            elif isinstance(exp, IHasHoldsExpr):
                yield from exp.get_holds_exprs()


class FluentNotExpr(FluentLogicExpr, IHasHoldsExpr):
    expr: FluentLogicExpr

    def __init__(self, parent, expr) -> None:
        super().__init__(parent=parent)
        self.expr = expr

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if isinstance(self.expr, HoldsExpr):
            yield self.expr
        elif isinstance(self.expr, IHasHoldsExpr):
            yield from self.expr.get_holds_exprs()


class ExistsExpr(Clause, IHasUUID, IHasHoldsExpr):
    var: ScenarioVariable
    fl_expr: FluentLogicExpr
    _uri: Optional[URIRef]

    def __init__(self, parent, var, in_set, fl_expr) -> None:
        super().__init__(parent=parent)
        self.var = var
        self.in_set = in_set
        self.fl_expr = fl_expr
        self._uri = None

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"exists-{self.uuid}"]
        return self._uri

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if isinstance(self.fl_expr, HoldsExpr):
            yield self.fl_expr
        elif isinstance(self.fl_expr, IHasHoldsExpr):
            yield from self.fl_expr.get_holds_exprs()


class WhenBehaviourClause(IHasUUID):
    behaviour: Behaviour
    duration: DuringEvent
    parent: WhenExpr
    _uri: Optional[URIRef]

    def __init__(self, parent, behaviour, duration, param_bhv) -> None:
        super().__init__(parent=parent)
        self.behaviour = behaviour
        self.duration = duration
        self.param_bhv = param_bhv
        self._uri = None

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.parent.namespace[f"when-bhv-{self.uuid}"]
        return self._uri


class ForAllExpr(IHasNamespace, IHasUUID):
    var: ScenarioVariable
    gwt_expr: GivenWhenThenExpr
    _uri: Optional[URIRef]

    def __init__(self, parent, var, in_set, gwt_expr) -> None:
        super().__init__(parent=parent)
        self.var = var
        self.in_set = in_set
        self.gwt_expr = gwt_expr
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        """Namespace object from parent.

        This needs to be a property since textX doesn't/may not call the the constructor of parent
        classes before the creation of this class, resulting in the 'ns' property not being available.
        """
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of ForAllExpr not an instance of 'IHasNamespace': {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"forall-{self.uuid}"]
        return self._uri


class GivenExpr(IHasNamespace, IHasHoldsExpr):
    given: Clause

    def __init__(self, parent, given) -> None:
        super().__init__(parent=parent)
        self.given = given

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of GivenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if isinstance(self.given, HoldsExpr):
            yield self.given
        elif isinstance(self.given, IHasHoldsExpr):
            yield from self.given.get_holds_exprs()


class WhenExpr(IHasNamespace):
    wbh_clause: WhenBehaviourClause

    def __init__(self, parent, when_events, when_bhv) -> None:
        super().__init__(parent=parent)
        self.when_events = when_events
        self.when_bhv = when_bhv

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of WhenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class ThenExpr(IHasNamespace, IHasHoldsExpr):
    then: Clause

    def __init__(self, parent, then) -> None:
        super().__init__(parent=parent)
        self.then = then

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of ThenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if isinstance(self.then, HoldsExpr):
            yield self.then
        elif isinstance(self.then, IHasHoldsExpr):
            yield from self.then.get_holds_exprs()


class GivenWhenThenExpr(IHasNamespace, IHasHoldsExpr):
    given_expr: Optional[GivenExpr]
    when_expr: Optional[WhenExpr]
    forall_expr: Optional[ForAllExpr]
    then_expr: Optional[ThenExpr]

    def __init__(self, parent, given_expr, when_expr, forall_expr, then_expr) -> None:
        super().__init__(parent=parent)
        self.given_expr = given_expr
        self.when_expr = when_expr
        self.forall_expr = forall_expr
        self.then_expr = then_expr

    @property
    def when_bhv(self) -> Optional[WhenBehaviourClause]:
        if self.forall_expr is not None:
            return self.forall_expr.gwt_expr.when_bhv

        if self.when_expr is not None:
            return self.when_expr.when_bhv

        return None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of GivenWhenThenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if self.given_expr is not None:
            yield from self.given_expr.get_holds_exprs()
        if self.forall_expr is not None:
            yield from self.forall_expr.gwt_expr.get_holds_exprs()
        if self.then_expr is not None:
            yield from self.then_expr.get_holds_exprs()


class ScenarioTemplate(IHasNamespaceDeclare):
    task: Task
    duration: DuringEvent
    variables: list[VariableBase]
    gwt_expr: GivenWhenThenExpr
    _holds_exprs_uris: set[URIRef]

    def __init__(
        self,
        parent,
        ns,
        name,
        task,
        duration,
        variables,
        gwt_expr,
    ):
        super().__init__(parent=parent, ns=ns, name=name)
        self.task = task
        self.duration = duration
        self.variables = variables
        self.gwt_expr = gwt_expr

        # generate Scenario & Scene URIs
        self.scenario_uri = self.namespace[f"{self.name}-scenario"]
        self.given_uri = self.namespace[f"{self.name}-scenario-given"]
        self.when_uri = self.namespace[f"{self.name}-scenario-when"]
        self.then_uri = self.namespace[f"{self.name}-scenario-then"]
        self.scene_uri = self.namespace[f"{self.name}-scene"]

        self._holds_exprs_uris = set()
        for h_expr in self.gwt_expr.get_holds_exprs():
            if h_expr.uri in self._holds_exprs_uris:
                raise ValueError(f"ScenarioTemplate: duplicate HoldsExpr URI: {h_expr.uri}")
            self._holds_exprs_uris.add(h_expr.uri)

    @property
    def when_bhv(self) -> WhenBehaviourClause:
        when_bhv = self.gwt_expr.when_bhv
        if when_bhv is None:
            raise ValueError(f"Template {self.uri}: no WhenBehaviourClause specified")
        return when_bhv

    def has_holds_expr(self, holds_expr_uri: URIRef) -> bool:
        return holds_expr_uri in self._holds_exprs_uris


class TaskVariation(IHasUUID, IHasNamespace):
    parent: ScenarioVariant

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of TaskVariation not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class TableVariation(TaskVariation):
    _uri: Optional[URIRef]

    def __init__(self, parent, header, rows) -> None:
        super().__init__(parent=parent)
        self.header = header
        self.rows = rows

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"tv-table-{self.uuid}"]
        return self._uri


class CartesianProductVariation(TaskVariation):
    _uri: Optional[URIRef]

    def __init__(self, parent, var_sets) -> None:
        super().__init__(parent=parent)
        self.var_sets = var_sets

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"tv-cart_prod-{self.uuid}"]
        return self._uri


class ScenarioVariant(IHasNamespace, IHasHoldsExpr):
    parent: UserStory
    template: ScenarioTemplate
    scene: SceneModel
    given_expr: Optional[GivenExpr]
    then_expr: Optional[ThenExpr]
    variation: TaskVariation
    _uri: Optional[URIRef]
    _holds_exprs_uris: Optional[set[URIRef]]

    def __init__(
        self, parent, name, template, scene, given_expr, when_events, then_expr, variation
    ) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.template = template
        self.scene = scene
        self.given_expr = given_expr
        self.then_expr = then_expr
        self.when_events = when_events
        self.variation = variation
        self._uri = None
        self._holds_exprs_uris = None

    def _load_holds_expr_uris(self):
        self._holds_exprs_uris = set()
        for h_expr in self.get_holds_exprs():
            if self.template.has_holds_expr(h_expr.uri):
                raise ValueError(
                    f"ScenarioVariant: duplicate HoldsExpr URI in template: {h_expr.uri}"
                )
            if h_expr.uri in self._holds_exprs_uris:
                raise ValueError(f"ScenarioVariant: duplicate HoldsExpr URIs: {h_expr.uri}")
            self._holds_exprs_uris.add(h_expr.uri)

    @property
    def namespace(self) -> Namespace:
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri

    def get_holds_exprs(self) -> Generator[HoldsExpr, None, None]:
        if self.given_expr is not None:
            yield from self.given_expr.get_holds_exprs()
        if self.then_expr is not None:
            yield from self.then_expr.get_holds_exprs()

    def has_holds_expr_uri(self, holds_expr_uri: URIRef) -> bool:
        if self._holds_exprs_uris is None:
            self._load_holds_expr_uris()
            assert self._holds_exprs_uris is not None

        return self.template.has_holds_expr(holds_expr_uri) or (
            holds_expr_uri in self._holds_exprs_uris
        )


class UserStory(IHasNamespaceDeclare):
    scenarios: list[ScenarioVariant]

    def __init__(self, parent, ns, name, role, feature, benefit, scenarios):
        super().__init__(parent=parent, ns=ns, name=name)
        self.role = role
        self.feature = feature
        self.benefit = benefit
        self.scenarios = scenarios
