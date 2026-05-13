# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdflib import RDF, Graph, URIRef
from bdd_dsl.models.urirefs import (
    URI_AGN_PRED_HAS_AGN,
    URI_AGN_TYPE_AGN,
    URI_BDD_PRED_ELEMS,
    URI_BDD_TYPE_CONST_SET,
    URI_BDD_TYPE_SCENE_AGN,
    URI_BDD_TYPE_SCENE_OBJ,
    URI_BDD_TYPE_SCENE_WS,
    URI_BDD_TYPE_SET,
    URI_ENV_PRED_HAS_OBJ,
    URI_ENV_PRED_HAS_WS,
    URI_ENV_PRED_OF_WS,
    URI_ENV_TYPE_OBJ,
    URI_ENV_TYPE_WS,
    URI_ENV_TYPE_WS_OBJ,
    URI_ENV_TYPE_WS_WS,
)
from robbdd.classes.scene import Agent, Object, SceneModel, Workspace, WorkspaceComposition


def add_scene_set(
    graph: Graph, scn_comp_uri: URIRef, scn_set_uri: URIRef, set_elems: list, set_uris: set[URIRef]
):
    if scn_set_uri in set_uris:
        return

    graph.add(triple=(scn_set_uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(scn_set_uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    for elem in set_elems:
        if isinstance(elem, Object):
            graph.add(triple=(elem.uri, RDF.type, URI_ENV_TYPE_OBJ))
            graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_OBJ, elem.uri))
        elif isinstance(elem, Workspace):
            graph.add(triple=(elem.uri, RDF.type, URI_ENV_TYPE_WS))
            graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_WS, elem.uri))
        elif isinstance(elem, Agent):
            graph.add(triple=(elem.uri, RDF.type, URI_AGN_TYPE_AGN))
            graph.add(triple=(scn_comp_uri, URI_AGN_PRED_HAS_AGN, elem.uri))
        else:
            raise ValueError(f"unhandled elem type: {elem}")

        graph.add(triple=(scn_set_uri, URI_BDD_PRED_ELEMS, elem.uri))

    set_uris.add(scn_set_uri)


def add_ws_comp(
    graph: Graph,
    scene: SceneModel,
    ws_comp: WorkspaceComposition,
    ws_comp_set: Optional[set[URIRef]],
):
    if ws_comp_set is None:
        ws_comp_set = set()
    if ws_comp.uri in ws_comp_set:
        raise RuntimeError(f"add_ws_comp: loop detected at ws composition '{ws_comp.uri}'")
    ws_comp_set.add(ws_comp.uri)

    graph.add(triple=(scene.scene_ws_uri, URI_ENV_PRED_HAS_WS, ws_comp.ws.uri))
    graph.add(triple=(ws_comp.ws.uri, RDF.type, URI_ENV_TYPE_WS))

    graph.add(triple=(ws_comp.uri, URI_ENV_PRED_OF_WS, ws_comp.ws.uri))
    if len(ws_comp.objects) > 0:
        graph.add(triple=(ws_comp.uri, RDF.type, URI_ENV_TYPE_WS_OBJ))
    if len(ws_comp.workspaces) > 0 or len(ws_comp.ws_comps):
        graph.add(triple=(ws_comp.uri, RDF.type, URI_ENV_TYPE_WS_WS))

    for obj in ws_comp.objects:
        graph.add(triple=(obj.uri, RDF.type, URI_ENV_TYPE_OBJ))
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_OBJ, obj.uri))
        graph.add(triple=(scene.scene_obj_uri, URI_ENV_PRED_HAS_OBJ, obj.uri))

    for ws in ws_comp.workspaces:
        graph.add(triple=(ws.uri, RDF.type, URI_ENV_TYPE_WS))
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_WS, ws.uri))
        graph.add(triple=(scene.scene_ws_uri, URI_ENV_PRED_HAS_WS, ws.uri))

    for child_comp in ws_comp.ws_comps:
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_WS, child_comp.ws.uri))
        add_ws_comp(graph=graph, scene=scene, ws_comp=child_comp, ws_comp_set=ws_comp_set)


def add_scene_model(graph: Graph, scene: SceneModel, set_uris: set[URIRef]):
    graph.bind(prefix=scene.ns_prefix, namespace=scene.namespace)

    graph.add(triple=(scene.scene_obj_uri, RDF.type, URI_BDD_TYPE_SCENE_OBJ))
    for obj_set in scene.obj_sets:
        add_scene_set(
            graph=graph,
            scn_comp_uri=scene.scene_obj_uri,
            scn_set_uri=obj_set.uri,
            set_elems=obj_set.objects,
            set_uris=set_uris,
        )
        graph.bind(prefix=obj_set.ns_prefix, namespace=obj_set.namespace)

    graph.add(triple=(scene.scene_ws_uri, RDF.type, URI_BDD_TYPE_SCENE_WS))
    for ws_set in scene.ws_sets:
        add_scene_set(
            graph=graph,
            scn_comp_uri=scene.scene_ws_uri,
            scn_set_uri=ws_set.uri,
            set_elems=ws_set.workspaces,
            set_uris=set_uris,
        )
        graph.bind(prefix=ws_set.ns_prefix, namespace=ws_set.namespace)

    graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SCENE_AGN))
    for agn_set in scene.agn_sets:
        add_scene_set(
            graph=graph,
            scn_comp_uri=scene.scene_agn_uri,
            scn_set_uri=agn_set.uri,
            set_elems=agn_set.agents,
            set_uris=set_uris,
        )
        graph.bind(prefix=agn_set.ns_prefix, namespace=agn_set.namespace)

    for ws_comp in scene.ws_comps:
        add_ws_comp(graph=graph, scene=scene, ws_comp=ws_comp, ws_comp_set=None)


def create_scene_model_graph(model: Any, g: Optional[Graph] = None) -> Graph:
    if g is None:
        g = Graph()

    scene_models = getattr(model, "scene_models", None)
    assert scene_models is not None and isinstance(
        scene_models, list
    ), "no 'scene_models' attr of type 'list' in model"
    set_uris = set()
    for scn in scene_models:
        add_scene_model(graph=g, scene=scn, set_uris=set_uris)
    return g
