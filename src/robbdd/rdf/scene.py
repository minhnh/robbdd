# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdflib import RDF, Graph, Literal, URIRef, Namespace
from rdf_utils.namespace import NS_MM_AGN
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
    GeometrySpec,
    ModelledAgent,
    ModelledAgentSet,
    ModelledObject,
    ModelledObjectSet,
    SceneInstance,
    EulerOrientationSpec,
    Frame,
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
from rdf_utils.namespace import NS_MM_GEOM, NS_MM_GEOM_COORD, NS_MM_GEOM_REL, NS_MM_QUDT
from rdf_utils.models.geometry import (
    URI_GEOM_PRED_ALPHA,
    URI_GEOM_PRED_AXES_SEQ,
    URI_GEOM_PRED_BETA,
    URI_GEOM_PRED_GAMMA,
    URI_GEOM_PRED_OF,
    URI_GEOM_PRED_OF_POSE,
    URI_GEOM_PRED_ORIGIN,
    URI_GEOM_PRED_SEEN_BY,
    URI_GEOM_PRED_WRT,
    URI_GEOM_PRED_X,
    URI_GEOM_PRED_Y,
    URI_GEOM_PRED_Z,
    URI_GEOM_TYPE_ANGLES_ABG,
    URI_GEOM_TYPE_EULER_ANGLES,
    URI_GEOM_TYPE_EXTRINSIC,
    URI_GEOM_TYPE_FRAME,
    URI_GEOM_TYPE_INTRINSIC,
    URI_GEOM_TYPE_POINT,
    URI_GEOM_TYPE_POSE,
    URI_GEOM_TYPE_POSE_COORD,
    URI_GEOM_TYPE_POSE_REF,
    URI_GEOM_TYPE_VECTOR_XYZ,
    URI_QUDT_TYPE_DEG,
    URI_QUDT_TYPE_RAD,
)


URI_EXEC_TYPE_SCENE_INST = NS_MM_EXEC["SceneInstance"]
URI_EXEC_PRED_HAS_MODELLED_OBJ = NS_MM_EXEC["has-modelled-object"]
URI_EXEC_PRED_HAS_MODELLED_AGN = NS_MM_EXEC["has-modelled-agent"]
URI_EXEC_PRED_HAS_FIXED_ATTACHMENT = NS_MM_EXEC["has-fixed-attachment"]
URI_GEOM_TYPE_SIMPLICIAL_COMPLEX = NS_MM_GEOM["SimplicialComplex"]
URI_GEOM_TYPE_GEOMETRY_MODEL = NS_MM_GEOM["GeometryModel"]
URI_GEOM_PRED_HAS_FRAME = NS_MM_GEOM["has-frame"]
URI_AGN_TYPE_ATTACHMENT_MODEL = NS_MM_AGN["AttachmentModel"]
NS_MM_KC = Namespace("https://comp-rob2b.github.io/metamodels/kinematic-chain/structural-entities#")
URI_KC_TYPE_KINEMATIC_CHAIN = NS_MM_KC["KinematicChain"]
URI_QUDT_PRED_UNIT = NS_MM_QUDT["unit"]

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
    graph.bind(prefix="geom", namespace=NS_MM_GEOM)
    graph.bind(prefix="geom-rel", namespace=NS_MM_GEOM_REL)
    graph.bind(prefix="geom-coord", namespace=NS_MM_GEOM_COORD)
    graph.bind(prefix="kc", namespace=NS_MM_KC)


def _add_frame(graph: Graph, frame: Frame) -> None:
    graph.add(triple=(frame.uri, RDF.type, URI_GEOM_TYPE_FRAME))
    graph.add(triple=(frame.uri, RDF.type, URI_GEOM_TYPE_SIMPLICIAL_COMPLEX))
    graph.add(triple=(frame.origin_uri, RDF.type, URI_GEOM_TYPE_POINT))
    graph.add(triple=(frame.uri, URI_GEOM_PRED_ORIGIN, frame.origin_uri))


def _add_geometry_model(
    graph: Graph,
    geom_spec: GeometrySpec,
    node_id: Optional[URIRef] = None,
    scene_geom: Optional[GeometrySpec] = None,
) -> None:
    if node_id is None:
        node_id = geom_spec.uri

    graph.add(triple=(node_id, RDF.type, URI_GEOM_TYPE_GEOMETRY_MODEL))

    for frame in [geom_spec.root, *geom_spec.frames]:
        _add_frame(graph=graph, frame=frame)
        graph.add(triple=(node_id, URI_GEOM_PRED_HAS_FRAME, frame.uri))

    _add_geom_spec_pose(graph=graph, geom_spec=geom_spec, scene_geom=scene_geom)


def _add_geom_spec_pose(
    graph: Graph, geom_spec: GeometrySpec, scene_geom: Optional[GeometrySpec]
) -> None:
    if geom_spec.pose is None:
        return

    pose = geom_spec.pose
    if geom_spec.pose.wrt is not None:
        wrt_frame = geom_spec.pose.wrt
    elif scene_geom is not None:
        wrt_frame = scene_geom.root
    else:
        raise ValueError(
            f"No reference frame specified and no default global pose for GeometrySpec {geom_spec.uri}"
        )

    if geom_spec.root.uri == wrt_frame.uri:
        raise ValueError(
            f"GeometrySpec {geom_spec.uri}: reference pose URI is the same with target pose: {wrt_frame.uri}"
        )

    pose_uri = geom_spec.pose_uri(wrt=wrt_frame)
    graph.add(triple=(pose_uri, RDF.type, URI_GEOM_TYPE_POSE))
    graph.add(triple=(pose_uri, URI_GEOM_PRED_OF, geom_spec.root.uri))
    graph.add(triple=(pose_uri, URI_GEOM_PRED_WRT, wrt_frame.uri))

    # Coordinate
    coord_uri = geom_spec.pose_coord_uri(wrt=wrt_frame)
    graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_POSE_REF))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_OF_POSE, pose_uri))
    graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_POSE_COORD))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_SEEN_BY, wrt_frame.uri))
    # Position Coords
    graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_VECTOR_XYZ))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_X, Literal(pose.x)))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_Y, Literal(pose.y)))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_Z, Literal(pose.z)))

    if isinstance(pose.orientation, EulerOrientationSpec):
        graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_EULER_ANGLES))

        graph.add(triple=(coord_uri, URI_GEOM_PRED_AXES_SEQ, Literal(pose.orientation.axes)))

        in_ex_type = (
            URI_GEOM_TYPE_EXTRINSIC if pose.orientation.extrinsic else URI_GEOM_TYPE_INTRINSIC
        )
        graph.add(triple=(coord_uri, RDF.type, in_ex_type))

        graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_ANGLES_ABG))
        graph.add(triple=(coord_uri, URI_GEOM_PRED_ALPHA, Literal(pose.orientation.alpha)))
        graph.add(triple=(coord_uri, URI_GEOM_PRED_BETA, Literal(pose.orientation.beta)))
        graph.add(triple=(coord_uri, URI_GEOM_PRED_GAMMA, Literal(pose.orientation.gamma)))

        unit_uri = URI_QUDT_TYPE_DEG if pose.orientation.unit == "deg" else URI_QUDT_TYPE_RAD
        graph.add(triple=(coord_uri, URI_QUDT_PRED_UNIT, unit_uri))
    else:
        raise ValueError(f"Unssuppored orientation: {pose.orientation}")


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
    elem_model: ElementModel, scene_inst: SceneInstance, seen_model_uris: set[URIRef]
):
    if elem_model.uri in seen_model_uris:
        raise ValueError(
            f"Duplicate model URI '{elem_model.uri}' in scene instance '{scene_inst.uri}'. "
            "Use unique model names within a scene instance."
        )
    seen_model_uris.add(elem_model.uri)


def add_modelled_obj(
    graph: Graph,
    scene_inst: SceneInstance,
    obj_model: ModelledObject,
    seen_model_uris: set[URIRef],
) -> None:
    graph.add(triple=(obj_model.modelled_uri, RDF.type, URI_ENV_TYPE_MOD_OBJ))
    graph.add(triple=(obj_model.modelled_uri, URI_ENV_PRED_OF_OBJ, obj_model.obj.uri))
    graph.add(triple=(scene_inst.uri, URI_EXEC_PRED_HAS_MODELLED_OBJ, obj_model.modelled_uri))
    obj_geom = obj_model.geometry
    if obj_geom is not None:
        graph.add(triple=(obj_model.modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, obj_geom.uri))
        _add_geometry_model(
            graph=graph, node_id=obj_geom.uri, geom_spec=obj_geom, scene_geom=scene_inst.geometry
        )

    for model in obj_model.models:
        _ensure_unique_scene_models(
            elem_model=model, scene_inst=scene_inst, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(obj_model.modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, model.uri))
        graph.add(triple=(model.uri, RDF.type, URI_ENV_TYPE_OBJ_MODEL))
        add_model_spec(graph=graph, elem_model=model)


def add_modelled_agn(
    graph: Graph,
    scene_inst: SceneInstance,
    agn_model: ModelledAgent,
    seen_model_uris: set[URIRef],
) -> None:
    graph.add(triple=(agn_model.modelled_uri, RDF.type, URI_AGN_TYPE_MOD_AGN))
    graph.add(triple=(agn_model.modelled_uri, URI_AGN_PRED_OF_AGN, agn_model.agn.uri))
    graph.add(triple=(scene_inst.uri, URI_EXEC_PRED_HAS_MODELLED_AGN, agn_model.modelled_uri))

    # Kinematic chain model
    kc_model = agn_model.kinematic.model
    _ensure_unique_scene_models(
        elem_model=kc_model, scene_inst=scene_inst, seen_model_uris=seen_model_uris
    )
    graph.add(triple=(agn_model.modelled_uri, URI_AGN_PRED_HAS_AGN_MODEL, kc_model.uri))
    graph.add(triple=(kc_model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
    graph.add(triple=(kc_model.uri, RDF.type, URI_KC_TYPE_KINEMATIC_CHAIN))
    add_model_spec(graph=graph, elem_model=kc_model)

    # Add geometry model to the same node
    _add_geometry_model(
        graph=graph,
        geom_spec=agn_model.kinematic.geometry,
        node_id=kc_model.uri,
        scene_geom=scene_inst.geometry,
    )

    for attachment in agn_model.attachments:
        model = attachment.model
        if model is None:
            continue
        _ensure_unique_scene_models(
            elem_model=model, scene_inst=scene_inst, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(agn_model.modelled_uri, URI_AGN_PRED_HAS_AGN_MODEL, model.uri))
        graph.add(triple=(agn_model.modelled_uri, URI_EXEC_PRED_HAS_FIXED_ATTACHMENT, model.uri))
        graph.add(triple=(model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
        graph.add(triple=(model.uri, RDF.type, URI_AGN_TYPE_ATTACHMENT_MODEL))
        add_model_spec(graph=graph, elem_model=model)
        if attachment.geometry is not None:
            _add_geometry_model(
                graph=graph,
                node_id=model.uri,
                geom_spec=attachment.geometry,
                scene_geom=scene_inst.geometry,
            )


def add_modelled_obj_set(
    graph: Graph,
    scene_inst: SceneInstance,
    obj_model_set: ModelledObjectSet,
    seen_model_uris: set[URIRef],
) -> None:
    for model in obj_model_set.models:
        _ensure_unique_scene_models(
            elem_model=model, scene_inst=scene_inst, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(model.uri, RDF.type, URI_ENV_TYPE_OBJ_MODEL))
        add_model_spec(graph=graph, elem_model=model)

        for index, obj in enumerate(obj_model_set.obj_set.objects):
            modelled_uri = obj_model_set.modelled_uri(index=index)
            graph.add(triple=(modelled_uri, RDF.type, URI_ENV_TYPE_MOD_OBJ))
            graph.add(triple=(modelled_uri, URI_ENV_PRED_OF_OBJ, obj.uri))
            graph.add(triple=(scene_inst.uri, URI_EXEC_PRED_HAS_MODELLED_OBJ, modelled_uri))
            graph.add(triple=(modelled_uri, URI_ENV_PRED_HAS_OBJ_MODEL, model.uri))


def add_modelled_agn_set(
    graph: Graph,
    scene_inst: SceneInstance,
    agn_model_set: ModelledAgentSet,
    seen_model_uris: set[URIRef],
) -> None:
    for model in agn_model_set.models:
        _ensure_unique_scene_models(
            elem_model=model, scene_inst=scene_inst, seen_model_uris=seen_model_uris
        )
        graph.add(triple=(model.uri, RDF.type, URI_AGN_TYPE_AGN_MODEL))
        add_model_spec(graph=graph, elem_model=model)

        for index, agn in enumerate(agn_model_set.agn_set.agents):
            modelled_uri = agn_model_set.modelled_uri(index=index)
            graph.add(triple=(modelled_uri, RDF.type, URI_AGN_TYPE_MOD_AGN))
            graph.add(triple=(modelled_uri, URI_AGN_PRED_OF_AGN, agn.uri))
            graph.add(triple=(scene_inst.uri, URI_EXEC_PRED_HAS_MODELLED_AGN, modelled_uri))
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


def add_modelled_scene(graph: Graph, scene_inst: SceneInstance) -> None:
    graph.bind(prefix=scene_inst.ns_prefix, namespace=scene_inst.namespace)
    graph.add(triple=(scene_inst.uri, RDF.type, URI_EXEC_TYPE_SCENE_INST))
    graph.add(triple=(scene_inst.uri, URI_BDD_PRED_OF_SCENE, scene_inst.scene.uri))

    seen_model_uris = set()

    if scene_inst.geometry is not None:
        _add_geometry_model(graph=graph, geom_spec=scene_inst.geometry)

    for obj_model in scene_inst.modelled_objs:
        add_modelled_obj(
            graph=graph,
            scene_inst=scene_inst,
            obj_model=obj_model,
            seen_model_uris=seen_model_uris,
        )

    for obj_model_set in scene_inst.modelled_obj_sets:
        add_modelled_obj_set(
            graph=graph,
            scene_inst=scene_inst,
            obj_model_set=obj_model_set,
            seen_model_uris=seen_model_uris,
        )

    for agn_model in scene_inst.modelled_agns:
        add_modelled_agn(
            graph=graph,
            scene_inst=scene_inst,
            agn_model=agn_model,
            seen_model_uris=seen_model_uris,
        )

    for agn_model_set in scene_inst.modelled_agn_sets:
        add_modelled_agn_set(
            graph=graph,
            scene_inst=scene_inst,
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

    scene_insts = getattr(model, "scene_insts", None)
    assert scene_insts is not None and isinstance(
        scene_insts, list
    ), "no 'scene_insts' attr of type 'list' in model"
    for scene_inst in scene_insts:
        add_modelled_scene(graph=g, scene_inst=scene_inst)

    return g
