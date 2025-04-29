# SPDX-License-Identifier: MPL-2.0
from uuid import UUID, uuid4
from rdflib import Namespace


class UserStory(object):
    def __init__(self, parent, ns, name, role, feature, benefit, scenarios):
        self.parent = parent
        self.name = name
        self.role = role
        self.feature = feature
        self.benefit = benefit
        self.scenarios = scenarios

        self.ns = ns
        _ns_obj = Namespace(ns.uri)
        self.uri = _ns_obj[self.name]


class ScenarioTemplate(object):
    def __init__(
        self,
        parent,
        ns,
        name,
        variables,
        gwt_expr,
    ):
        self.parent = parent
        self.name = name
        self.variables = variables
        self.gwt_expr = gwt_expr

        self.ns = ns
        self.ns_obj = Namespace(self.ns.uri)
        self.uri = self.ns_obj[self.name]

        # generate Scenario & Scene URIs
        self.scenario_uri = self.ns_obj[f"{self.name}-scenario"]
        self.given_uri = self.ns_obj[f"{self.name}-scenario-given"]
        self.when_uri = self.ns_obj[f"{self.name}-scenario-when"]
        self.then_uri = self.ns_obj[f"{self.name}-scenario-then"]
        self.scene_uri = self.ns_obj[f"{self.name}-scene"]


class Clause(object):
    def __init__(self, parent) -> None:
        self.parent = parent


class FluentLogicExpr(Clause):
    uuid: UUID

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.uuid = uuid4()


class FluentAndExpr(FluentLogicExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, first, rest) -> None:
        super().__init__(parent)
        self.first = first
        self.rest = rest

        self.expressions = [self.first]
        for expr in self.rest:
            self.expressions.append(expr)


class FluentOrExpr(FluentLogicExpr):
    expressions: list[FluentLogicExpr]

    def __init__(self, parent, first, rest) -> None:
        super().__init__(parent)
        self.first = first
        self.rest = rest

        self.expressions = [self.first]
        for expr in self.rest:
            self.expressions.append(expr)


class FluentNotExpr(FluentLogicExpr):
    expr: FluentLogicExpr

    def __init__(self, parent, expr) -> None:
        super().__init__(parent)
        self.expr = expr


class HoldsExpr(FluentLogicExpr):
    def __init__(self, parent, predicate, tc) -> None:
        super().__init__(parent)
        self.predicate = predicate
        self.tc = tc
