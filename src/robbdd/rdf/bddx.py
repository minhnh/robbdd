# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdflib import Graph, RDF
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_OF_VARIANT,
    URI_BDD_TYPE_SCENARIO_EXEC,
)
from robbdd.classes.bddx import ScenarioExecution


def add_scr_exec_to_graph(graph: Graph, scr_exec: ScenarioExecution):
    graph.add(triple=(scr_exec.uri, RDF.type, URI_BDD_TYPE_SCENARIO_EXEC))
    graph.add(triple=(scr_exec.uri, URI_BDD_PRED_OF_VARIANT, scr_exec.variant.uri))


def create_bddx_model_graph(model: Any, g: Optional[Graph] = None) -> Graph:
    if g is None:
        g = Graph()

    for scr_exec in model.scenario_execs:
        add_scr_exec_to_graph(graph=g, scr_exec=scr_exec)

    return g
