# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdflib import RDF, Graph, Literal, URIRef, Namespace
from bdd_dsl.models.namespace import NS_MM_EXEC, NS_MM_ROS
from bdd_dsl.models.urirefs import (
    URI_AGN_PRED_HAS_AGN,
    URI_AGN_PRED_HAS_AGN_MODEL,
    URI_AGN_PRED_OF_AGN,
    URI_AGN_TYPE_AGN,
    URI_AGN_TYPE_AGN_MODEL,
    URI_AGN_TYPE_MOD_AGN,
    URI_BDD_PRED_ELEMS,
    URI_BDD_PRED_OF_SCENE,
    URI_BDD_TYPE_CONST_SET,
    URI_BDD_TYPE_SCENE,
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
    ModelledAgent,
    ModelledAgentSet,
    ModelledObject,
    ModelledObjectSet,
    ModelledScene,
    Object,
    ObjectSet,
    SceneModel,
    SceneSet,
    SimilarAgentSet,
    SimilarObjectSet,
    WorkspaceComposition,
    WorkspaceSet,
)
from robbdd.rdf.common import add_py_module_attr


URI_EXEC_TYPE_SCENE_REAL = NS_MM_EXEC["SceneRealization"]
URI_EXEC_PRED_HAS_MODELLED_OBJ = NS_MM_EXEC["has-modelled-object"]
URI_EXEC_PRED_HAS_MODELLED_AGN = NS_MM_EXEC["has-modelled-agent"]

NS_XML = Namespace("https://www.w3.org/TR/2006/REC-xml11-20060816#")
NS_URDF = Namespace("https://wiki.ros.org/urdf/XML/")
NS_MJCF = Namespace("https://mujoco.readthedocs.io/en/stable/XMLreference.html#")
NS_USD = Namespace("https://openusd.org/release/spec.html#")

URI_XML_DOCUMENT = NS_XML["document"]
URI_URDF_ROBOT = NS_URDF["robot"]
URI_MJCF_MUJOCO = NS_MJCF["mujoco"]
URI_USD_STAGE = NS_USD["stage"]


def _bind_model_kind_namespaces(graph: Graph) -> None:
    graph.bind(prefix="xml", namespace=NS_XML)
    graph.bind(prefix="urdf", namespace=NS_URDF)
    graph.bind(prefix="mjcf", namespace=NS_MJCF)
    graph.bind(prefix="usd", namespace=NS_USD)


def add_model_spec(graph: Graph, elem_model: ElementModel) -> None:
    model_spec_type = elem_model.model_spec.__class__.__name__
    if "PyModuleAttr" in model_spec_type:
        add_py_module_attr(graph=graph, node_uri=elem_model.uri, py_model=elem_model.model_spec)
    elif "SystemPath" in model_spec_type:
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_RES_PATH))
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_SYS_RES))
        path_l = Literal(elem_model.model_spec.path)
        graph.add(triple=(elem_model.uri, URI_EXEC_PRED_PATH, path_l))
    elif "RosPath" in model_spec_type:
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_RES_PATH))
        graph.add(triple=(elem_model.uri, RDF.type, URI_EXEC_TYPE_SYS_RES))
        graph.add(triple=(elem_model.uri, RDF.type, NS_MM_ROS["Package"]))
        pkg_name_l = Literal(elem_model.model_spec.pkg)
        graph.add(triple=(elem_model.uri, NS_MM_ROS["package-name"], pkg_name_l))
        path_l = Literal(elem_model.model_spec.path)
        graph.add(triple=(elem_model.uri, URI_EXEC_PRED_PATH, path_l))
    else:
        raise ValueError(f"Unhandled model specification type: {model_spec_type}")

    if elem_model.model_kind == "urdf":
        graph.add(triple=(elem_model.uri, RDF.type, URI_XML_DOCUMENT))
        graph.add(triple=(elem_model.uri, RDF.type, URI_URDF_ROBOT))
    elif elem_model.model_kind == "mjcf":
        graph.add(triple=(elem_model.uri, RDF.type, URI_XML_DOCUMENT))
        graph.add(triple=(elem_model.uri, RDF.type, URI_MJCF_MUJOCO))
    elif elem_model.model_kind == "usd":
        graph.add(triple=(elem_model.uri, RDF.type, URI_USD_STAGE))
    elif elem_model.model_kind is not None:
        raise ValueError(f"Unhandled model kind: {elem_model.model_kind}")


def add_obj(graph: Graph, obj: Object) -> None:
    graph.add(triple=(obj.uri, RDF.type, URI_ENV_TYPE_OBJ))


def add_agn(graph: Graph, agn: Agent) -> None:
    graph.add(triple=(agn.uri, RDF.type, URI_AGN_TYPE_AGN))


def _ensure_unique_scene_models(
    elem_model: ElementModel, modelled_scene: ModelledScene, seen_model_uris: set[URIRef]
):
    if elem_model.uri in seen_model_uris:
        raise ValueError(
            f"Duplicate model URI '{elem_model.uri}' in modelled scene '{modelled_scene.uri}'. "
            "Use unique model names within a modelled scene."
        )
    seen_model_uris.add(elem_model.uri)


def add_modelled_obj(
    graph: Graph,
    modelled_scene: ModelledScene,
    obj_model: ModelledObject,
    seen_model_uris: set[URIRef],
) -> None:
    graph.add(triple=(obj_model.modelled_uri, RDF.type, URI_ENV_TYPE_MOD_OBJ))
    graph.add(triple=(obj_model.modelled_uri, URI_ENV_PRED_OF_OBJ, obj_model.obj.uri))
    graph.add(triple=(modelled_scene.uri, URI_EXEC_PRED_HAS_MODELLED_OBJ, obj_model.modelled_uri))
    for model in obj_model.models:
        _ensure_unique_scene_models(
            elem_model=model, modelled_scene=modelled_scene, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(obj_model.modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, model.uri))
        graph.add(triple=(model.uri, RDF.type, URI_ENV_TYPE_OBJ_MODEL))
        add_model_spec(graph=graph, elem_model=model)


def add_modelled_agn(
    graph: Graph,
    modelled_scene: ModelledScene,
    agn_model: ModelledAgent,
    seen_model_uris: set[URIRef],
) -> None:
    graph.add(triple=(agn_model.modelled_uri, RDF.type, URI_AGN_TYPE_MOD_AGN))
    graph.add(triple=(agn_model.modelled_uri, URI_AGN_PRED_OF_AGN, agn_model.agn.uri))
    graph.add(triple=(modelled_scene.uri, URI_EXEC_PRED_HAS_MODELLED_AGN, agn_model.modelled_uri))
    for model in agn_model.models:
        _ensure_unique_scene_models(
            elem_model=model, modelled_scene=modelled_scene, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(agn_model.modelled_uri, URI_AGN_PRED_HAS_AGN_MODEL, model.uri))
        graph.add(triple=(model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
        add_model_spec(graph=graph, elem_model=model)


def add_modelled_obj_set(
    graph: Graph,
    modelled_scene: ModelledScene,
    obj_model_set: ModelledObjectSet,
    seen_model_uris: set[URIRef],
) -> None:
    for model in obj_model_set.models:
        _ensure_unique_scene_models(
            elem_model=model, modelled_scene=modelled_scene, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(model.uri, RDF.type, URI_ENV_TYPE_OBJ_MODEL))
        add_model_spec(graph=graph, elem_model=model)

        for index, obj in enumerate(obj_model_set.obj_set.objects):
            modelled_uri = obj_model_set.modelled_uri(index=index)
            graph.add(triple=(modelled_uri, RDF.type, URI_ENV_TYPE_MOD_OBJ))
            graph.add(triple=(modelled_uri, URI_ENV_PRED_OF_OBJ, obj.uri))
            graph.add(triple=(modelled_scene.uri, URI_EXEC_PRED_HAS_MODELLED_OBJ, modelled_uri))
            graph.add(triple=(modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, model.uri))


def add_modelled_agn_set(
    graph: Graph,
    modelled_scene: ModelledScene,
    agn_model_set: ModelledAgentSet,
    seen_model_uris: set[URIRef],
) -> None:
    for model in agn_model_set.models:
        _ensure_unique_scene_models(
            elem_model=model, modelled_scene=modelled_scene, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
        add_model_spec(graph=graph, elem_model=model)

        for index, agn in enumerate(agn_model_set.agn_set.agents):
            modelled_uri = agn_model_set.modelled_uri(index=index)
            graph.add(triple=(modelled_uri, RDF.type, URI_AGN_TYPE_MOD_AGN))
            graph.add(triple=(modelled_uri, URI_AGN_PRED_OF_AGN, agn.uri))
            graph.add(triple=(modelled_scene.uri, URI_EXEC_PRED_HAS_MODELLED_AGN, modelled_uri))
            graph.add(triple=(modelled_uri, URI_AGN_PRED_HAS_AGN_MODEL, model.uri))


def _add_scene_set_common(graph: Graph, scene_set: SceneSet, set_uris: set[URIRef]) -> bool:
    if scene_set.uri in set_uris:
        return False
    set_uris.add(scene_set.uri)

    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(scene_set.uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    graph.bind(prefix=scene_set.ns_prefix, namespace=scene_set.namespace)

    return True


def add_obj_set(
    graph: Graph,
    obj_set: ObjectSet | SimilarObjectSet,
    set_uris: set[URIRef],
    scn_comp_uri: Optional[URIRef] = None,
) -> None:
    if not _add_scene_set_common(graph=graph, scene_set=obj_set, set_uris=set_uris):
        return

    for obj in obj_set.objects:
        add_obj(graph=graph, obj=obj)
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
    graph: Graph,
    agn_set: AgentSet | SimilarAgentSet,
    set_uris: set[URIRef],
    scn_comp_uri: Optional[URIRef] = None,
) -> None:
    if not _add_scene_set_common(graph=graph, scene_set=agn_set, set_uris=set_uris):
        return

    for agn in agn_set.agents:
        add_agn(graph=graph, agn=agn)
        graph.add(triple=(agn_set.uri, URI_BDD_PRED_ELEMS, agn.uri))
        if scn_comp_uri is not None:
            graph.add(triple=(scn_comp_uri, URI_AGN_PRED_HAS_AGN, agn.uri))


def add_scene_set(
    graph: Graph, scene_set: SceneSet, set_uris: set[URIRef], scn_comp_uri: Optional[URIRef] = None
):
    if isinstance(scene_set, (ObjectSet, SimilarObjectSet)):
        add_obj_set(graph=graph, obj_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    elif isinstance(scene_set, WorkspaceSet):
        add_ws_set(graph=graph, ws_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    elif isinstance(scene_set, (AgentSet, SimilarAgentSet)):
        add_agn_set(graph=graph, agn_set=scene_set, set_uris=set_uris, scn_comp_uri=scn_comp_uri)
    else:
        raise ValueError(f"Unhandled SceneSet type: {type(scene_set)}")


def add_ws_comp(
    graph: Graph,
    scene: SceneModel,
    ws_comp: WorkspaceComposition,
    set_uris: set[URIRef],
    ws_comp_set: Optional[set[URIRef]],
) -> None:
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
    graph.bind(prefix=scene.ns_prefix, namespace=scene.namespace)
    graph.add(triple=(scene.uri, RDF.type, URI_BDD_TYPE_SCENE))

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
    if scene_has_agn:
        graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SCENE_AGN))
    return scene_has_obj, scene_has_ws, scene_has_agn


def add_modelled_scene(graph: Graph, modelled_scene: ModelledScene) -> None:
    graph.bind(prefix=modelled_scene.ns_prefix, namespace=modelled_scene.namespace)
    graph.add(triple=(modelled_scene.uri, RDF.type, URI_EXEC_TYPE_SCENE_REAL))
    graph.add(triple=(modelled_scene.uri, URI_BDD_PRED_OF_SCENE, modelled_scene.scene.uri))

    seen_model_uris = set()

    for obj_model in modelled_scene.modelled_objs:
        add_modelled_obj(
            graph=graph,
            modelled_scene=modelled_scene,
            obj_model=obj_model,
            seen_model_uris=seen_model_uris,
        )

    for obj_model_set in modelled_scene.modelled_obj_sets:
        add_modelled_obj_set(
            graph=graph,
            modelled_scene=modelled_scene,
            obj_model_set=obj_model_set,
            seen_model_uris=seen_model_uris,
        )

    for agn_model in modelled_scene.modelled_agns:
        add_modelled_agn(
            graph=graph,
            modelled_scene=modelled_scene,
            agn_model=agn_model,
            seen_model_uris=seen_model_uris,
        )

    for agn_model_set in modelled_scene.modelled_agn_sets:
        add_modelled_agn_set(
            graph=graph,
            modelled_scene=modelled_scene,
            agn_model_set=agn_model_set,
            seen_model_uris=seen_model_uris,
        )


def create_scene_model_graph(model: Any, g: Optional[Graph] = None) -> Graph:
    if g is None:
        g = Graph()

    _bind_model_kind_namespaces(graph=g)

    scene_models = getattr(model, "scene_models", None)
    assert scene_models is not None and isinstance(
        scene_models, list
    ), "no 'scene_models' attr of type 'list' in model"
    set_uris = set()
    for scn in scene_models:
        add_scene_model(graph=g, scene=scn, set_uris=set_uris)

    modelled_scenes = getattr(model, "modelled_scenes", None)
    assert modelled_scenes is not None and isinstance(
        modelled_scenes, list
    ), "no 'modelled_scenes' attr of type 'list' in model"
    for modelled_scene in modelled_scenes:
        add_modelled_scene(graph=g, modelled_scene=modelled_scene)

    return g
