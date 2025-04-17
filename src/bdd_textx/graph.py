# SPDX-License-Identifier: MPL-2.0
from rdflib import Graph, RDF
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_OF_SCENARIO,
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
from bdd_textx.classes.bdd import ScenarioTemplate, UserStory


def add_gwt_expr_to_graph(graph: Graph, gwt_expr: object):
    pass


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
    add_gwt_expr_to_graph(graph=graph, gwt_expr=tmpl.gwt_expr)


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
