# SPDX-License-Identifier: MPL-2.0
from typing import Optional
from uuid import UUID, uuid4
from rdflib import Namespace, URIRef


class IHasNamespaceDeclare:
    uri: URIRef
    ns_obj: Namespace

    def __init__(self, ns, name) -> None:
        self.ns = ns
        self.name = name
        self.ns_obj = Namespace(self.ns.uri)
        self.uri = self.ns_obj[self.name]


class Behaviour(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns, name)
        self.parent = parent


class Event(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns, name)
        self.parent = parent


class Task(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name):
        super().__init__(ns, name)
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
        'ns' property not being available at runtime.
        """
        if self._uri is not None:
            return self._uri

        assert isinstance(
            self.parent, IHasNamespaceDeclare
        ), f"parent of variable '{self.name}' is not of type  IHasNamespaceDeclare: {self.parent}"

        self._uri = self.parent.ns_obj[self.name]
        return self._uri


class ScenarioVariable(VariableBase):
    def __init__(self, parent, name) -> None:
        super().__init__(parent, name)


class ScenarioSetVariable(VariableBase):
    def __init__(self, parent, name) -> None:
        super().__init__(parent, name)


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
        self.scenario_uri = self.ns_obj[f"{self.name}-scenario"]
        self.given_uri = self.ns_obj[f"{self.name}-scenario-given"]
        self.when_uri = self.ns_obj[f"{self.name}-scenario-when"]
        self.then_uri = self.ns_obj[f"{self.name}-scenario-then"]
        self.scene_uri = self.ns_obj[f"{self.name}-scene"]


class IHasUUID:
    uuid: UUID

    def __init__(self) -> None:
        self.uuid = uuid4()

    def get_uri(self, ns: Namespace, prefix: Optional[str] = None) -> URIRef:
        if prefix is None:
            return ns[str(self.uuid)]

        return ns[f"{prefix}-{self.uuid}"]


class TimeConstraint(IHasUUID):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent


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


class Clause(IHasUUID):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent


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

    def __init__(self, parent, predicate, tc) -> None:
        super().__init__(parent)
        self.predicate = predicate
        self.tc = tc
