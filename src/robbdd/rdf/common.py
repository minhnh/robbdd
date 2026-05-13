# SPDX-License-Identifier: MPL-2.0
from typing import Any
from rdflib import Graph, URIRef, Node, BNode, Literal
from rdflib.collection import Collection


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
