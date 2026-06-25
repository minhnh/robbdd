# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from bdd_dsl.models.namespace import NS_MM_ROS
from rdflib import RDF, Graph, Literal, URIRef
from bdd_dsl.models.urirefs import (
    URI_AGN_PRED_HAS_AGN,
    URI_AGN_PRED_HAS_AGN_MODEL,
    URI_AGN_PRED_OF_AGN,
    URI_AGN_TYPE_AGN,
    URI_AGN_TYPE_AGN_MODEL,
    URI_AGN_TYPE_MOD_AGN,
    URI_BDD_PRED_ELEMS,
    URI_BDD_TYPE_CONST_SET,
    URI_BDD_TYPE_SCENE_AGN,
    URI_BDD_TYPE_SCENE_OBJ,
    URI_BDD_TYPE_SCENE_WS,
    URI_BDD_TYPE_SET,
    URI_ENV_PRED_HAS_OBJ,
    URI_ENV_PRED_HAS_OBJ_MODEL,
    URI_ENV_PRED_HAS_WS,
    URI_ENV_PRED_OF_OBJ,
    URI_ENV_PRED_OF_WS,
    URI_ENV_TYPE_MOD_OBJ,
    URI_ENV_TYPE_OBJ,
    URI_ENV_TYPE_OBJ_MODEL,
    URI_ENV_TYPE_WS,
    URI_ENV_TYPE_WS_OBJ,
    URI_ENV_TYPE_WS_WS,
    URI_EXEC_PRED_PATH,
    URI_EXEC_TYPE_RES_PATH,
    URI_EXEC_TYPE_SYS_RES,
)
from robbdd.classes.scene import (
    Agent,
    AgentSet,
    ElementModel,
    Object,
    ObjectSet,
    SceneModel,
    SceneSet,
    WorkspaceComposition,
    WorkspaceSet,
)
from robbdd.rdf.common import add_py_module_attr


def add_model_spec(graph: Graph, elem_model: ElementModel):
    model_spec_type = elem_model.model_spec.__class__.__name__
    if "PyModuleAttr" in model_spec_type:
        add_py_module_attr(graph=graph, node_uri=elem_model.uri, py_model=elem_model.model_spec)
        return

    if "SystemPath" in model_spec_type:
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_RES_PATH))
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_SYS_RES))
        path_l = Literal(elem_model.model_spec.path)
        graph.add(triple=(elem_model.uri, URI_EXEC_PRED_PATH, path_l))
        return

    if "RosPath" in model_spec_type:
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_RES_PATH))
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_SYS_RES))
        graph.add(triple=(elem_model.uri, RDF.type, NS_MM_ROS["Package"]))
        pkg_name_l = Literal(elem_model.model_spec.pkg)
        graph.add(triple=(elem_model.uri, NS_MM_ROS["package-name"], pkg_name_l))
        path_l = Literal(elem_model.model_spec.path)
        graph.add(triple=(elem_model.uri, URI_EXEC_PRED_PATH, path_l))
        return

    raise ValueError(f"Unhandled model specification type: {model_spec_type}")


def add_obj_model(graph: Graph, obj: Object):
    graph.add(triple=(obj.uri, RDF.type, URI_ENV_TYPE_OBJ))

    if obj.models is None or len(obj.models) == 0:
        return

    graph.add(triple=(obj.modelled_uri, RDF.type, URI_ENV_TYPE_MOD_OBJ))
    graph.add(triple=(obj.modelled_uri, URI_ENV_PRED_OF_OBJ, obj.uri))

    for obj_model in obj.models:
        graph.add(triple=(obj.modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, obj_model.uri))
        graph.add(triple=(obj_model.uri, RDF.type, URI_ENV_TYPE_OBJ_MODEL))
        add_model_spec(graph=graph, elem_model=obj_model)


def add_agn_model(graph: Graph, agn: Agent):
    graph.add(triple=(agn.uri, RDF.type, URI_AGN_TYPE_AGN))

    if agn.models is None or len(agn.models) == 0:
        return

    graph.add(triple=(agn.modelled_uri, RDF.type, URI_AGN_TYPE_MOD_AGN))
    graph.add(triple=(agn.modelled_uri, URI_AGN_PRED_OF_AGN, agn.uri))

    for agn_model in agn.models:
        graph.add(triple=(agn.modelled_uri, URI_AGN_PRED_HAS_AGN_MODEL, agn_model.uri))
        graph.add(triple=(agn_model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
        add_model_spec(graph=graph, elem_model=agn_model)


def _add_scene_set_common(graph: Graph, scene_set: SceneSet, set_uris: set[URIRef]) -> bool:
    if scene_set.uri in set_uris:
        return False
    set_uris.add(scene_set.uri)

    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    graph.bind(prefix=scene_set.ns_prefix, namespace=scene_set.namespace)

    return True


def add_obj_set(
    graph: Graph, obj_set: ObjectSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
) -> None:
    if not _add_scene_set_common(graph=graph, scene_set=obj_set, set_uris=set_uris):
        return

    for obj in obj_set.objects:
        add_obj_model(graph=graph, obj=obj)
        graph.add(triple=(obj_set.uri, URI_BDD_PRED_ELEMS, obj.uri))
        if scn_comp_uri is not None:
            graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_OBJ, obj.uri))


def add_ws_set(
    graph: Graph, ws_set: WorkspaceSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
) -> None:
    if not _add_scene_set_common(graph=graph, scene_set=ws_set, set_uris=set_uris):
        return

    for ws in ws_set.workspaces:
        graph.add(triple=(ws.uri, RDF.type, URI_ENV_TYPE_WS))
        graph.add(triple=(ws_set.uri, URI_BDD_PRED_ELEMS, ws.uri))
        if scn_comp_uri is not None:
            graph.add(triple=(scn_comp_uri, URI_ENV_PRED_HAS_WS, ws.uri))


def add_agn_set(
    graph: Graph, agn_set: AgentSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
) -> None:
    if not _add_scene_set_common(graph=graph, scene_set=agn_set, set_uris=set_uris):
        return

    for agn in agn_set.agents:
        add_agn_model(graph=graph, agn=agn)
        graph.add(triple=(agn_set.uri, URI_BDD_PRED_ELEMS, agn.uri))
        if scn_comp_uri is not None:
            graph.add(triple=(scn_comp_uri, URI_AGN_PRED_HAS_AGN, agn.uri))


def add_scene_set(
    graph: Graph, scene_set: SceneSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
):
    if isinstance(scene_set, ObjectSet):
        add_obj_set(graph=graph, obj_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    elif isinstance(scene_set, WorkspaceSet):
        add_ws_set(graph=graph, ws_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    elif isinstance(scene_set, AgentSet):
        add_agn_set(graph=graph, agn_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    else:
        raise ValueError(f"Unhandled SceneSet type: {type(scene_set)}")


def add_ws_comp(
    graph: Graph,
    scene: SceneModel,
    ws_comp: WorkspaceComposition,
    set_uris: set[URIRef],
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
        assert isinstance(obj.parent, ObjectSet), f"parent of obj not an object set: {obj.parent}"
        if obj.parent.uri not in set_uris:
            add_obj_set(graph=graph, obj_set=obj.parent, set_uris=set_uris)
            graph.add(triple=(scene.scene_obj_uri, URI_ENV_PRED_HAS_OBJ, obj.uri))
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_OBJ, obj.uri))

    for ws in ws_comp.workspaces:
        assert isinstance(ws.parent, WorkspaceSet), f"parent of ws not a workspace set: {ws.parent}"
        if ws.parent.uri not in set_uris:
            add_ws_set(graph=graph, ws_set=ws.parent, set_uris=set_uris)
            graph.add(triple=(scene.scene_ws_uri, URI_ENV_PRED_HAS_WS, ws.uri))
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_WS, ws.uri))

    for child_comp in ws_comp.ws_comps:
        graph.add(triple=(ws_comp.uri, URI_ENV_PRED_HAS_WS, child_comp.ws.uri))
        add_ws_comp(
            graph=graph, scene=scene, ws_comp=child_comp, set_uris=set_uris, ws_comp_set=ws_comp_set
        )


def add_scene_model(
    graph: Graph, scene: SceneModel, set_uris: set[URIRef]
) -> tuple[bool, bool, bool]:
    """Add elements of a scene model to the graph and returns whether the scene has objects, workspaces, and/or agents"""
    graph.bind(prefix=scene.ns_prefix, namespace=scene.namespace)

    for obj_set in scene.obj_sets:
        add_obj_set(
            graph=graph,
            obj_set=obj_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_obj_uri,
        )

    for ws_set in scene.ws_sets:
        add_ws_set(
            graph=graph,
            ws_set=ws_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_ws_uri,
        )

    for agn_set in scene.agn_sets:
        add_agn_set(
            graph=graph,
            agn_set=agn_set,
            set_uris=set_uris,
            scn_comp_uri=scene.scene_agn_uri,
        )

    for ws_comp in scene.ws_comps:
        add_ws_comp(graph=graph, scene=scene, ws_comp=ws_comp, set_uris=set_uris, ws_comp_set=None)

    scene_has_obj = (
        graph.value(subject=scene.scene_obj_uri, predicate=URI_ENV_PRED_HAS_OBJ) is not None
    )
    scene_has_ws = (
        graph.value(subject=scene.scene_ws_uri, predicate=URI_ENV_PRED_HAS_WS) is not None
    )
    scene_has_agn = (
        graph.value(subject=scene.scene_agn_uri, predicate=URI_AGN_PRED_HAS_AGN) is not None
    )
    if scene_has_obj:
        graph.add(triple=(scene.scene_obj_uri, RDF.type, URI_BDD_TYPE_SCENE_OBJ))
    if scene_has_ws:
        graph.add(triple=(scene.scene_ws_uri, RDF.type, URI_BDD_TYPE_SCENE_WS))
    if scene_has_agn > 0:
        graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SCENE_AGN))
    return scene_has_obj, scene_has_ws, scene_has_agn


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
