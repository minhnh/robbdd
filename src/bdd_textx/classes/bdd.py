# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid4
from rdflib import Namespace, URIRef


class IHasNamespace(object):
    @property
    def namespace(self) -> Namespace:
        raise NotImplementedError(
            f"'namespace' property not implemented for '{self.__class__.__name__}'"
        )


class IHasNamespaceDeclare(IHasNamespace):
    uri: URIRef
    _ns_obj: Namespace

    def __init__(self, **kwargs) -> None:
        self.ns = kwargs.get("ns", None)
        assert self.ns is not None

        self.name = kwargs.get("name", None)
        assert self.name is not None

        self._ns_obj = Namespace(self.ns.uri)
        self.uri = self._ns_obj[self.name]

    @property
    def namespace(self) -> Namespace:
        return self._ns_obj


class IHasUUID:
    uuid: UUID

    def __init__(self) -> None:
        self.uuid = uuid4()

    @property
    def uri(self) -> URIRef:
        raise NotImplementedError(f"'uri' property not implemented for '{self.__class__.__name__}'")


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
        if self._uri is not None:
            return self._uri

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
        if self._uri is not None:
            return self._uri
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
        if self._uri is not None:
            return self._uri
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
        if self._uri is not None:
            return self._uri

        self._uri = self.namespace[f"exists-{self.uuid}"]
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
        if self._uri is not None:
            return self._uri

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


class UserStory(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name, role, feature, benefit, scenarios):
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.role = role
        self.feature = feature
        self.benefit = benefit
        self.scenarios = scenarios


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
