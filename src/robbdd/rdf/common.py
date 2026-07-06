# SPDX-License-Identifier: MPL-2.0
from typing import Any
from rdf_utils.models.python import (
    URI_PY_PRED_ATTR_NAME,
    URI_PY_PRED_MODULE_NAME,
    URI_PY_TYPE_MODULE_ATTR,
)
from rdflib import RDF, Graph, URIRef, Node, BNode, Literal
from rdflib.collection import Collection
from scene_dsl.classes.common import parse_py_module_attr


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


def add_py_module_attr(graph: Graph, node_uri: URIRef, py_model: Any):
    module_name, attr_name = parse_py_module_attr(model=py_model)
    graph.add(triple=(node_uri, RDF.type, URI_PY_TYPE_MODULE_ATTR))
    graph.add(triple=(node_uri, URI_PY_PRED_MODULE_NAME, Literal(module_name)))
    graph.add(triple=(node_uri, URI_PY_PRED_ATTR_NAME, Literal(attr_name)))
