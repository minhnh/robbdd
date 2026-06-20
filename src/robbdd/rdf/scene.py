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
from robbdd.classes.scene import (
    AgentSet,
    ObjectSet,
    SceneModel,
    SceneSet,
    WorkspaceComposition,
    WorkspaceSet,
)


def add_scene_set(
    graph: Graph, scene_set: SceneSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
):
    if scene_set.uri in set_uris:
        return

    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    graph.bind(prefix=scene_set.ns_prefix, namespace=scene_set.namespace)

    if isinstance(scene_set, ObjectSet):
        for obj in scene_set.objects:
            graph.add(triple=(obj.uri, RDF.type, URI_ENV_TYPE_OBJ))
            graph.add(triple=(scene_set.uri, URI_BDD_PRED_ELEMS, obj.uri))
            if scn_comp_uri is not None:
                graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_OBJ, obj.uri))
    elif isinstance(scene_set, WorkspaceSet):
        for ws in scene_set.workspaces:
            graph.add(triple=(ws.uri, RDF.type, URI_ENV_TYPE_WS))
            graph.add(triple=(scene_set.uri, URI_BDD_PRED_ELEMS, ws.uri))
            if scn_comp_uri is not None:
                graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_WS, ws.uri))
    elif isinstance(scene_set, AgentSet):
        for agn in scene_set.agents:
            graph.add(triple=(agn.uri, RDF.type, URI_AGN_TYPE_AGN))
            graph.add(triple=(scene_set.uri, URI_BDD_PRED_ELEMS, agn.uri))
            if scn_comp_uri is not None:
                graph.add(triple=(scn_comp_uri, URI_AGN_PRED_HAS_AGN, agn.uri))
    else:
        raise ValueError(f"Unhandled SceneSet type: {type(scene_set)}")

    set_uris.add(scene_set.uri)


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

    if len(scene.obj_sets) > 0:
        graph.add(triple=(scene.scene_obj_uri, RDF.type, URI_BDD_TYPE_SCENE_OBJ))
    if len(scene.ws_sets) > 0 or len(scene.ws_comps) > 0:
        graph.add(triple=(scene.scene_ws_uri, RDF.type, URI_BDD_TYPE_SCENE_WS))
    if len(scene.agn_sets) > 0:
        graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SCENE_AGN))

    for obj_set in scene.obj_sets:
        add_scene_set(
            graph=graph,
            scene_set=obj_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_obj_uri,
        )

    for ws_set in scene.ws_sets:
        add_scene_set(
            graph=graph,
            scene_set=ws_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_ws_uri,
        )

    for agn_set in scene.agn_sets:
        add_scene_set(
            graph=graph,
            scene_set=agn_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_agn_uri,
        )

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
