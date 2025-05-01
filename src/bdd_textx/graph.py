# SPDX-License-Identifier: MPL-2.0
from typing import Any
from bdd_dsl.models.namespace import NS_MM_BDD
from rdf_utils.namespace import NS_MM_TIME
from rdflib import BNode, Graph, RDF, Literal, Namespace, Node, URIRef
from rdflib.collection import Collection
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_CLAUSE_OF,
    URI_BDD_PRED_HAS_AC,
    URI_BDD_PRED_HAS_CLAUSE,
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_HOLDS_AT,
    URI_BDD_PRED_OF_SCENARIO,
    URI_BDD_PRED_OF_TMPL,
    URI_BDD_PRED_REF_OBJ,
    URI_BDD_PRED_REF_WS,
    URI_BDD_TYPE_FLUENT_CLAUSE,
    URI_BDD_TYPE_IS_HELD,
    URI_BDD_TYPE_LOCATED_AT,
    URI_BDD_TYPE_SCENARIO,
    URI_BDD_PRED_GIVEN,
    URI_BDD_PRED_WHEN,
    URI_BDD_PRED_THEN,
    URI_BDD_TYPE_GIVEN,
    URI_BDD_TYPE_SCENARIO_VARIANT,
    URI_BDD_TYPE_WHEN,
    URI_BDD_TYPE_THEN,
    URI_BDD_TYPE_SCENARIO_TMPL,
    URI_BDD_TYPE_SCENE,
    URI_BDD_TYPE_US,
    URI_BHV_TYPE_BHV,
    URI_TASK_PRED_OF_TASK,
    URI_TASK_TYPE_TASK,
    URI_TIME_PRED_AFTER_EVT,
    URI_TIME_PRED_BEFORE_EVT,
    URI_TIME_TYPE_AFTER_EVT,
    URI_TIME_TYPE_BEFORE_EVT,
    URI_TIME_TYPE_DURING,
)
from bdd_textx.classes.bdd import (
    AfterEvent,
    BeforeEvent,
    Clause,
    DuringEvent,
    HoldsExpr,
    ScenarioSetVariable,
    ScenarioTemplate,
    TimeConstraint,
    UserStory,
    VariableBase,
)


def add_node_list_pred(
    graph: Graph, subject_uri: URIRef, pred_uri: URIRef, nodes: list[Node]
) -> Collection:
    b = BNode()
    c = Collection(graph=graph, uri=b, seq=nodes)
    graph.add((subject_uri, pred_uri, b))
    return c


def add_literal_list_pred(
    graph: Graph, subject_uri: URIRef, pred_uri: URIRef, values: list[Any]
) -> Collection:
    literals = []
    for val in values:
        literals.append(Literal(val))
    return add_node_list_pred(
        graph=graph, subject_uri=subject_uri, pred_uri=pred_uri, nodes=literals
    )


def add_fc_predicate(graph: Graph, clause: HoldsExpr, clause_uri: URIRef):
    pred_type_str = type(clause.predicate).__name__

    if "LocatedAtPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_LOCATED_AT))

        obj_var = getattr(clause.predicate, "object", None)
        assert (
            obj_var is not None and isinstance(obj_var, VariableBase)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        ws_var = getattr(clause.predicate, "workspace", None)
        assert (
            ws_var is not None and isinstance(ws_var, VariableBase)
        ), f"unexpected 'workspace' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {ws_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, ws_var.uri))
        return

    if "IsHeldPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_IS_HELD))
        return

    if "HasConfigPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["HasConfigPredicate"]))
        return

    if "IsSortedPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["IsSortedPredicate"]))

        obj_var = getattr(clause.predicate, "objects", None)
        assert (
            obj_var is not None and isinstance(obj_var, ScenarioSetVariable)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        ws_var = getattr(clause.predicate, "workspaces", None)
        assert (
            ws_var is not None and isinstance(ws_var, ScenarioSetVariable)
        ), f"unexpected 'workspaces' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {ws_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, ws_var.uri))
        return

    raise ValueError(f"unhandled predicate type: {pred_type_str}")


def add_fc_time_constraint(
    graph: Graph, tc: TimeConstraint, parent_ns: Namespace, clause_uri: URIRef
):
    tc_uri = tc.get_uri(ns=parent_ns, prefix=f"tc-{type(tc).__name__}")

    graph.add(triple=(tc_uri, RDF.type, NS_MM_TIME["TimeConstraint"]))
    graph.add(triple=(clause_uri, URI_BDD_PRED_HOLDS_AT, tc_uri))

    if isinstance(tc, BeforeEvent):
        graph.add(triple=(tc_uri, RDF.type, URI_TIME_TYPE_BEFORE_EVT))
        graph.add(triple=(tc_uri, URI_TIME_PRED_BEFORE_EVT, tc.event.uri))
        return

    if isinstance(tc, AfterEvent):
        graph.add(triple=(tc_uri, RDF.type, URI_TIME_TYPE_AFTER_EVT))
        graph.add(triple=(tc_uri, URI_TIME_PRED_AFTER_EVT, tc.event.uri))
        return

    if isinstance(tc, DuringEvent):
        graph.add(triple=(tc_uri, RDF.type, URI_TIME_TYPE_DURING))
        graph.add(triple=(tc_uri, URI_TIME_PRED_AFTER_EVT, tc.start_event.uri))
        graph.add(triple=(tc_uri, URI_TIME_PRED_BEFORE_EVT, tc.end_event.uri))
        return

    raise ValueError(f"unhandled time constraint type: {type(tc)}")


def add_clause_expr(
    graph: Graph,
    clause: Clause,
    parent_ns: Namespace,
    clause_of_uri: URIRef,
    clause_col: Collection,
):
    if isinstance(clause, HoldsExpr):
        prefix = f"fc-{type(clause.predicate).__name__}-{type(clause.tc).__name__}"
        fc_uri = clause.get_uri(ns=parent_ns, prefix=prefix)

        graph.add((fc_uri, RDF.type, URI_BDD_TYPE_FLUENT_CLAUSE))
        graph.add((fc_uri, URI_BDD_PRED_CLAUSE_OF, clause_of_uri))

        add_fc_predicate(graph=graph, clause=clause, clause_uri=fc_uri)
        add_fc_time_constraint(graph=graph, tc=clause.tc, clause_uri=fc_uri, parent_ns=parent_ns)

        clause_col.append(fc_uri)
    else:
        raise ValueError(f"clause expression of type '{type(clause)}' is not handled: {clause}")


def add_gwt_expr(
    graph: Graph,
    gwt_expr: Any,
    parent_ns: Namespace,
    parent_uri: URIRef,
    given_uri: URIRef,
    when_uri: URIRef,
    then_uri: URIRef,
):
    clause_col = add_node_list_pred(
        graph=graph, subject_uri=parent_uri, pred_uri=URI_BDD_PRED_HAS_CLAUSE, nodes=[]
    )

    if gwt_expr.given_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=gwt_expr.given_expr.given,
            parent_ns=parent_ns,
            clause_of_uri=given_uri,
            clause_col=clause_col,
        )

    if gwt_expr.forall_expr is not None:
        print(gwt_expr.forall_expr)
    elif gwt_expr.when_expr is not None:
        print(gwt_expr.when_expr)
    else:
        raise ValueError(
            f"Given-When-Then expression must either have a ForAll or WhenBehaviour expressions, parent: {parent_uri.n3()}"
        )

    if gwt_expr.then_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=gwt_expr.then_expr.then,
            parent_ns=parent_ns,
            clause_of_uri=then_uri,
            clause_col=clause_col,
        )


def add_scenario_tmpl(graph: Graph, tmpl: ScenarioTemplate):
    graph.add(triple=(tmpl.uri, RDF.type, URI_BDD_TYPE_SCENARIO_TMPL))

    # scenario
    graph.add(triple=(tmpl.scenario_uri, RDF.type, URI_BDD_TYPE_SCENARIO))
    graph.add(triple=(tmpl.given_uri, RDF.type, URI_BDD_TYPE_GIVEN))
    graph.add(triple=(tmpl.when_uri, RDF.type, URI_BDD_TYPE_WHEN))
    graph.add(triple=(tmpl.then_uri, RDF.type, URI_BDD_TYPE_THEN))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_GIVEN, tmpl.given_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_WHEN, tmpl.when_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_THEN, tmpl.then_uri))
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_OF_SCENARIO, tmpl.scenario_uri))

    # task
    graph.add(triple=(tmpl.scenario_uri, URI_TASK_PRED_OF_TASK, tmpl.task.uri))

    # scene
    graph.add(triple=(tmpl.scene_uri, RDF.type, URI_BDD_TYPE_SCENE))
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_HAS_SCENE, tmpl.scene_uri))

    # variables
    for var in tmpl.variables:
        graph.add(triple=(var.uri, RDF.type, NS_MM_BDD["ScenarioVariable"]))
        if isinstance(var, ScenarioSetVariable):
            graph.add(triple=(var.uri, RDF.type, NS_MM_BDD["Set"]))

    # clauses
    add_gwt_expr(
        graph=graph,
        gwt_expr=tmpl.gwt_expr,
        parent_ns=tmpl.ns_obj,
        parent_uri=tmpl.uri,
        given_uri=tmpl.given_uri,
        when_uri=tmpl.when_uri,
        then_uri=tmpl.then_uri,
    )


def add_us_to_graph(graph: Graph, us: UserStory):
    graph.add(triple=(us.uri, RDF.type, URI_BDD_TYPE_US))

    for scr_var in us.scenarios:
        var_uri = us.ns_obj[scr_var.name]
        graph.add((var_uri, RDF.type, URI_BDD_TYPE_SCENARIO_VARIANT))
        graph.add((var_uri, URI_BDD_PRED_OF_TMPL, scr_var.template.uri))
        graph.add((us.uri, URI_BDD_PRED_HAS_AC, var_uri))


def add_bdd_model_to_graph(graph: Graph, model: object):
    behaviours = getattr(model, "behaviours", None)
    assert behaviours is not None and isinstance(behaviours, list), "no list of behaviours in model"
    for bhv in behaviours:
        graph.add(triple=(bhv.uri, RDF.type, URI_BHV_TYPE_BHV))

    events = getattr(model, "events", None)
    assert events is not None and isinstance(events, list), "no list of events in model"
    for evt in events:
        graph.add(triple=(evt.uri, RDF.type, NS_MM_TIME["Event"]))

    tasks = getattr(model, "tasks", None)
    assert tasks is not None and isinstance(tasks, list), "no list of tasks in model"
    for task in tasks:
        graph.add(triple=(task.uri, RDF.type, URI_TASK_TYPE_TASK))

    templates = getattr(model, "templates", None)
    assert templates is not None and isinstance(
        templates, list
    ), "no list of scenario templates in model"
    for tmpl in templates:
        add_scenario_tmpl(graph=graph, tmpl=tmpl)

    stories = getattr(model, "stories", None)
    assert stories is not None and isinstance(stories, list), "no list of user stories in model"
    for us in stories:
        add_us_to_graph(graph=graph, us=us)
