# SPDX-License-Identifier: MPL-2.0
from typing import Any
from bdd_dsl.models.namespace import NS_MM_BDD
from rdflib import BNode, Graph, RDF, Literal, Namespace, Node, URIRef
from rdflib.collection import Collection
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_CLAUSE_OF,
    URI_BDD_PRED_HAS_CLAUSE,
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_OF_SCENARIO,
    URI_BDD_TYPE_FLUENT_CLAUSE,
    URI_BDD_TYPE_IS_HELD,
    URI_BDD_TYPE_LOCATED_AT,
    URI_BDD_TYPE_SCENARIO,
    URI_BDD_PRED_GIVEN,
    URI_BDD_PRED_WHEN,
    URI_BDD_PRED_THEN,
    URI_BDD_TYPE_GIVEN,
    URI_BDD_TYPE_WHEN,
    URI_BDD_TYPE_THEN,
    URI_BDD_TYPE_SCENARIO_TMPL,
    URI_BDD_TYPE_SCENE,
    URI_BDD_TYPE_SCENARIO_VARIABLE,
    URI_BDD_TYPE_US,
)
from bdd_textx.classes.bdd import HoldsExpr, ScenarioTemplate, UserStory


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


def get_fluent_clause_pred_type(clause: HoldsExpr) -> URIRef:
    pred_type_str = type(clause.predicate).__name__
    if "LocatedAtPred" in pred_type_str:
        return URI_BDD_TYPE_LOCATED_AT

    if "IsHeldPred" in pred_type_str:
        return URI_BDD_TYPE_IS_HELD

    if "HasConfigPred" in pred_type_str:
        return NS_MM_BDD["HasConfigPredicate"]

    if "IsSortedPred" in pred_type_str:
        return NS_MM_BDD["IsSortedPredicate"]

    raise ValueError(f"unhandled predicate type: {pred_type_str}")


def get_fluent_clause_uri(clause: HoldsExpr, parent_ns: Namespace) -> URIRef:
    id_str = f"fc-{type(clause.predicate).__name__}-{type(clause.tc).__name__}-{clause.uuid}"
    return parent_ns[id_str]


def add_clause_expr(
    graph: Graph, clause: Any, parent_ns: Namespace, clause_of_uri: URIRef, clause_col: Collection
):
    if isinstance(clause, HoldsExpr):
        uri = get_fluent_clause_uri(clause=clause, parent_ns=parent_ns)
        graph.add((uri, RDF.type, URI_BDD_TYPE_FLUENT_CLAUSE))
        graph.add((uri, RDF.type, get_fluent_clause_pred_type(clause=clause)))
        graph.add((uri, URI_BDD_PRED_CLAUSE_OF, clause_of_uri))
        clause_col.append(uri)
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


def add_tmpl_to_graph(graph: Graph, tmpl: ScenarioTemplate):
    graph.add(triple=(tmpl.uri, RDF.type, URI_BDD_TYPE_SCENARIO_TMPL))

    # scenario
    graph.add(triple=(tmpl.scenario_uri, RDF.type, URI_BDD_TYPE_SCENARIO))
    graph.add(triple=(tmpl.given_uri, RDF.type, URI_BDD_TYPE_GIVEN))
    graph.add(triple=(tmpl.when_uri, RDF.type, URI_BDD_TYPE_WHEN))
    graph.add(triple=(tmpl.then_uri, RDF.type, URI_BDD_TYPE_THEN))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_GIVEN, tmpl.given_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_WHEN, tmpl.when_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_THEN, tmpl.then_uri))
    # TODO(minhnh) of-task
    # TODO(minhnh) of-behaviour
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_OF_SCENARIO, tmpl.scenario_uri))

    # scene
    graph.add(triple=(tmpl.scene_uri, RDF.type, URI_BDD_TYPE_SCENE))
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_HAS_SCENE, tmpl.scene_uri))

    # variables
    for var in tmpl.variables:
        var_uri = tmpl.ns_obj[var.name]
        graph.add(triple=(var_uri, RDF.type, URI_BDD_TYPE_SCENARIO_VARIABLE))

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


def add_bdd_model_to_graph(graph: Graph, model: object):
    # TODO(minhnh) behaviours
    # TODO(minhnh) events
    # TODO(minhnh) tasks

    templates = getattr(model, "templates", None)
    assert templates is not None and isinstance(templates, list), "no list of user stories in model"
    for tmpl in templates:
        add_tmpl_to_graph(graph=graph, tmpl=tmpl)

    stories = getattr(model, "stories", None)
    assert stories is not None and isinstance(stories, list), "no list of user stories in model"
    for us in stories:
        add_us_to_graph(graph=graph, us=us)
