# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from typing import Optional
from rdflib import Namespace, URIRef
from bdd_textx.classes.common import IHasNamespace, IHasNamespaceDeclare, IHasUUID


class Behaviour(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns=ns, name=name)
        self.parent = parent


class Event(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns=ns, name=name)
        self.parent = parent


class Task(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns=ns, name=name)
        self.parent = parent


class VariableBase(object):
    _uri: Optional[URIRef]

    def __init__(self, parent, name) -> None:
        self.parent = parent
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
        super().__init__(parent, name)


class ScenarioSetVariable(VariableBase):
    def __init__(self, parent, name) -> None:
        super().__init__(parent, name)


class TimeConstraint(IHasUUID, IHasNamespace):
    _uri: Optional[URIRef]

    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of 'TimeConstraint' not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"tc-{self.__class__.__name__}-{self.uuid}"]
        return self._uri


class BeforeEvent(TimeConstraint):
    event: Event

    def __init__(self, parent, event) -> None:
        super().__init__(parent)
        self.event = event


class AfterEvent(TimeConstraint):
    event: Event

    def __init__(self, parent, event) -> None:
        super().__init__(parent)
        self.event = event


class DuringEvent(TimeConstraint):
    start_event: Event
    end_event: Event

    def __init__(self, parent, start_event, end_event) -> None:
        super().__init__(parent)
        self.start_event = start_event
        self.end_event = end_event


class Clause(IHasUUID, IHasNamespace):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of 'Clause' not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class FluentLogicExpr(Clause):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)


class FluentAndExpr(FluentLogicExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, first, rest) -> None:
        super().__init__(parent=parent)
        self.first = first
        self.rest = rest

        self.expressions = [self.first]
        for expr in self.rest:
            self.expressions.append(expr)


class FluentOrExpr(FluentLogicExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, first, rest) -> None:
        super().__init__(parent=parent)
        self.first = first
        self.rest = rest

        self.expressions = [self.first]
        for expr in self.rest:
            self.expressions.append(expr)


class FluentNotExpr(FluentLogicExpr):
    expr: FluentLogicExpr

    def __init__(self, parent, expr) -> None:
        super().__init__(parent=parent)
        self.expr = expr


class HoldsExpr(FluentLogicExpr):
    tc: TimeConstraint
    _uri: Optional[URIRef]

    def __init__(self, parent, predicate, tc) -> None:
        super().__init__(parent)
        self.predicate = predicate
        self.tc = tc
        self._uri = None

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[
                f"fc-{self.predicate.__class__.__name__}-{self.tc.__class__.__name__}-{self.uuid}"
            ]
        return self._uri


class ExistsExpr(Clause):
    var: ScenarioVariable
    fl_expr: FluentLogicExpr
    _uri: Optional[URIRef]

    def __init__(self, parent, var, in_set, fl_expr) -> None:
        super().__init__(parent)
        self.var = var
        self.in_set = in_set
        self.fl_expr = fl_expr
        self._uri = None

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[f"exists-{self.uuid}"]
        return self._uri


class WhenBehaviourClause(IHasUUID):
    behaviour: Behaviour
    parent: WhenExpr
    _uri: Optional[URIRef]

    def __init__(self, parent, behaviour, param_bhv) -> None:
        super().__init__()
        self.parent = parent
        self.behaviour = behaviour
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
        super().__init__()
        self.parent = parent
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


class GivenExpr(IHasNamespace):
    given: Clause

    def __init__(self, parent, given) -> None:
        super().__init__()
        self.parent = parent
        self.given = given

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of GivenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class WhenExpr(IHasNamespace):
    wbh_clause: WhenBehaviourClause

    def __init__(self, parent, when_events, when_bhv) -> None:
        super().__init__()
        self.parent = parent
        self.when_events = when_events
        self.when_bhv = when_bhv

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of WhenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class ThenExpr(IHasNamespace):
    then: Clause

    def __init__(self, parent, then) -> None:
        super().__init__()
        self.parent = parent
        self.then = then

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of ThenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class GivenWhenThenExpr(IHasNamespace):
    forall_expr: ForAllExpr
    given_expr: GivenExpr

    def __init__(self, parent, given_expr, when_expr, forall_expr, then_expr) -> None:
        super().__init__()
        self.parent = parent
        self.given_expr = given_expr
        self.when_expr = when_expr
        self.forall_expr = forall_expr
        self.then_expr = then_expr

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of GivenWhenThenExpr not instance of IHasNamespace: {self.parent}"
        return self.parent.namespace


class ScenarioTemplate(IHasNamespaceDeclare):
    task: Task
    variables: list[VariableBase]

    def __init__(
        self,
        parent,
        ns,
        name,
        task,
        variables,
        gwt_expr,
    ):
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.task = task
        self.variables = variables
        self.gwt_expr = gwt_expr

        # generate Scenario & Scene URIs
        self.scenario_uri = self.namespace[f"{self.name}-scenario"]
        self.given_uri = self.namespace[f"{self.name}-scenario-given"]
        self.when_uri = self.namespace[f"{self.name}-scenario-when"]
        self.then_uri = self.namespace[f"{self.name}-scenario-then"]
        self.scene_uri = self.namespace[f"{self.name}-scene"]


class TaskVariation(IHasUUID):
    parent: ScenarioVariant
    _uri: Optional[URIRef]

    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        self._uri = None

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.parent.namespace[f"tv-{self.uuid}"]
        return self._uri


class TableVariation(TaskVariation):
    def __init__(self, parent, header, rows) -> None:
        super().__init__(parent)
        self.header = header
        self.rows = rows


class ScenarioVariant(IHasNamespace):
    parent: UserStory
    template: ScenarioTemplate
    given_expr: GivenExpr
    then_expr: ThenExpr
    variation: TaskVariation
    _uri: Optional[URIRef]

    def __init__(
        self, parent, name, template, scene, given_expr, when_events, then_expr, variation
    ) -> None:
        super().__init__()
        self.parent = parent
        self.name = name
        self.template = template
        self.scene = scene
        self.given_expr = given_expr
        self.then_expr = then_expr
        self.when_events = when_events
        self.variation = variation
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class UserStory(IHasNamespaceDeclare):
    scenarios: list[ScenarioVariant]

    def __init__(self, parent, ns, name, role, feature, benefit, scenarios):
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.role = role
        self.feature = feature
        self.benefit = benefit
        self.scenarios = scenarios
