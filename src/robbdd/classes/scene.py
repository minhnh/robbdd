# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from typing import Any, Optional
from rdflib import URIRef, Namespace
from robbdd.classes.common import IHasNamespace, IHasNamespaceDeclare, SetBase


class ElementModel(IHasNamespace):
    model_spec: Any
    model_kind: Optional[str]
    _uri: Optional[URIRef]

    def __init__(self, parent, name, model_kind, model_spec) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.model_kind = model_kind
        self.model_spec = model_spec
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of ElementModel not an 'IHasNamespace': {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class OrientationSpec:
    pass


class EulerOrientationSpec(OrientationSpec):
    extrinsic: bool

    def __init__(self, parent, axes, extrinsic, alpha, beta, gamma, unit) -> None:
        self.parent = parent
        self.extrinsic = extrinsic
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.axes = axes or "zyx"
        self.unit = unit or "rad"


class PoseSpec:
    wrt: Optional[Frame]
    orientation: OrientationSpec

    def __init__(self, parent, wrt, x, y, z, orientation) -> None:
        self.parent = parent
        self.wrt = wrt
        self.x = x
        self.y = y
        self.z = z
        self.orientation = orientation


class Object(IHasNamespace):
    _uri: Optional[URIRef]

    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent)
        self.name = name
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, (ObjectSet, SimilarObjectSet)
        ), f"parent of obj not an object set: {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class Workspace(IHasNamespace):
    _uri: Optional[URIRef]

    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent)
        self.name = name
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, WorkspaceSet
        ), f"parent of ws not a 'WorkspaceSet': {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class Agent(IHasNamespace):
    _uri: Optional[URIRef]

    def __init__(self, parent, name) -> None:
        super().__init__(parent=parent)
        self.name = name
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, (AgentSet, SimilarAgentSet)
        ), f"parent of agn not an agent set: {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri


class SceneSet(SetBase, IHasNamespaceDeclare):
    def __init__(self, parent, ns, name) -> None:
        super().__init__(parent=parent, ns=ns, name=name)


class ObjectSet(SceneSet):
    objects: list[Object]

    def __init__(self, parent, ns, name, objects) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.objects = objects


class SimilarObjectSet(SceneSet):
    base_name: str
    count: int
    objects: list[Object]

    def __init__(self, parent, ns, name, base_name, count) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        if count < 1:
            raise ValueError(f"SimilarObjectSet '{name}' must have count >= 1, got {count}")
        self.base_name = base_name
        self.count = count
        self.objects = [Object(parent=self, name=f"{base_name}{i}") for i in range(count)]


class WorkspaceSet(SceneSet):
    workspaces: list[Workspace]

    def __init__(self, parent, ns, name, workspaces) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.workspaces = workspaces


class AgentSet(SceneSet):
    agents: list[Agent]

    def __init__(self, parent, ns, name, agents) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.agents = agents


class SimilarAgentSet(SceneSet):
    base_name: str
    count: int
    agents: list[Agent]

    def __init__(self, parent, ns, name, base_name, count) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        if count < 1:
            raise ValueError(f"SimilarAgentSet '{name}' must have count >= 1, got {count}")
        self.base_name = base_name
        self.count = count
        self.agents = [Agent(parent=self, name=f"{base_name}{i}") for i in range(count)]


class WorkspaceComposition(IHasNamespaceDeclare):
    objects: list[Object]
    ws: Workspace
    workspaces: list[Workspace]
    ws_comps: list[WorkspaceComposition]

    def __init__(self, parent, ns, name, ws, objects, workspaces, ws_comps) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.ws = ws
        self.objects = objects
        self.workspaces = workspaces
        self.ws_comps = ws_comps


class SceneModel(IHasNamespaceDeclare):
    obj_sets: list[ObjectSet | SimilarObjectSet]
    ws_sets: list[WorkspaceSet]
    ws_comps: list[WorkspaceComposition]
    agn_sets: list[AgentSet | SimilarAgentSet]
    scene_obj_uri: URIRef
    scene_ws_uri: URIRef
    scene_agn_uri: URIRef

    def __init__(self, parent, ns, name, obj_sets, ws_sets, ws_comps, agn_sets) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.obj_sets = obj_sets
        self.ws_sets = ws_sets
        self.ws_comps = ws_comps
        self.agn_sets = agn_sets
        self.scene_obj_uri = self.namespace[f"{self.name}-scene-has-obj"]
        self.scene_ws_uri = self.namespace[f"{self.name}-scene-has-ws"]
        self.scene_agn_uri = self.namespace[f"{self.name}-scene-has-agn"]


class ModelledObject(IHasNamespace):
    obj: Object
    models: list[ElementModel]
    geometry: GeometrySpec
    _modelled_uri: Optional[URIRef]

    def __init__(self, parent, obj, models, geometry) -> None:
        super().__init__(parent=parent)
        self.obj = obj
        self.models = models
        self.geometry = geometry
        self._modelled_uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled obj not a 'SceneInstance': {self.parent}"
        return self.parent.namespace

    @property
    def modelled_uri(self) -> URIRef:
        if self._modelled_uri is None:
            assert isinstance(
                self.parent, SceneInstance
            ), f"parent of modelled obj not a 'SceneInstance': {self.parent}"
            self._modelled_uri = self.namespace[f"modelled-obj-{self.parent.name}-{self.obj.name}"]
        return self._modelled_uri


class ModelledObjectSet(IHasNamespace):
    obj_set: SimilarObjectSet
    models: list[ElementModel]

    def __init__(self, parent, obj_set, models) -> None:
        super().__init__(parent=parent)
        self.obj_set = obj_set
        self.models = models

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled obj set not a 'SceneInstance': {self.parent}"
        return self.parent.namespace

    def modelled_uri(self, index: int) -> URIRef:
        obj = self.obj_set.objects[index]
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled obj set not a 'SceneInstance': {self.parent}"
        return self.namespace[f"modelled-obj-{self.parent.name}-{obj.name}"]


class Frame(IHasNamespace):
    _uri: Optional[URIRef]
    _origin_uri: Optional[URIRef]

    def __init__(self, parent=None, name=None) -> None:
        super().__init__(parent=parent)
        self.name = name
        self._uri = None
        self._origin_uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of frame has no namespace: {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            assert isinstance(
                self.parent, GeometrySpec
            ), f"parent of frame not a GeometrySpec: {self.parent}"
            self._uri = self.namespace[f"{self.parent.name}-{self.name}"]
        return self._uri

    @property
    def origin_uri(self) -> URIRef:
        if self._origin_uri is None:
            self._origin_uri = URIRef(f"{self.uri}-origin")
        return self._origin_uri


class GeometrySpec(IHasNamespace):
    name: str
    root: Frame
    frames: list[Frame]
    pose: Optional[PoseSpec]
    _uri: Optional[URIRef]

    def __init__(self, parent, name, root, frames=None, pose=None) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.root = root
        self.frames = frames or []
        self.pose = pose
        self._uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, IHasNamespace
        ), f"parent of geometry spec has no namespace: {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri

    def pose_uri(self, wrt: Frame) -> URIRef:
        return self.namespace[f"{self.root.name}-wrt-{wrt.name}"]

    def pose_coord_uri(self, wrt: Frame) -> URIRef:
        return self.namespace[f"{self.root.name}-wrt-{wrt.name}-coord"]


class KinematicSpec(IHasNamespace):
    model: ElementModel
    geometry: GeometrySpec

    def __init__(self, parent, model, geometry) -> None:
        super().__init__(parent=parent)
        self.model = model
        self.geometry = geometry

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, ModelledAgent
        ), f"parent of kinematic spec not a 'ModelledAgent': {self.parent}"
        return self.parent.namespace


class FixedAttachment(IHasNamespace):
    model: ElementModel
    geometry: GeometrySpec

    def __init__(
        self,
        parent,
        name,
        model,
        geometry,
    ) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.model = model
        self.geometry = geometry

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, ModelledAgent
        ), f"parent of fixed attachment not a 'ModelledAgent': {self.parent}"
        return self.parent.namespace

    @property
    def agent_model(self):
        return self.parent


class ModelledAgent(IHasNamespace):
    agn: Agent
    kinematic: KinematicSpec
    attachments: list[FixedAttachment]
    _modelled_uri: Optional[URIRef]

    def __init__(self, parent, agn, kinematic, attachments=None) -> None:
        super().__init__(parent=parent)
        self.agn = agn
        self.kinematic = kinematic
        self.attachments = attachments or []
        self._modelled_uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled agn not a 'SceneInstance': {self.parent}"
        return self.parent.namespace

    @property
    def modelled_uri(self) -> URIRef:
        if self._modelled_uri is None:
            assert isinstance(
                self.parent, SceneInstance
            ), f"parent of modelled agn not a 'SceneInstance': {self.parent}"
            self._modelled_uri = self.namespace[f"modelled-agn-{self.parent.name}-{self.agn.name}"]
        return self._modelled_uri


class ModelledAgentSet(IHasNamespace):
    agn_set: SimilarAgentSet
    models: list[ElementModel]

    def __init__(self, parent, agn_set, models) -> None:
        super().__init__(parent=parent)
        self.agn_set = agn_set
        self.models = models

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled agn set not a 'SceneInstance': {self.parent}"
        return self.parent.namespace

    def modelled_uri(self, index: int) -> URIRef:
        agn = self.agn_set.agents[index]
        assert isinstance(
            self.parent, SceneInstance
        ), f"parent of modelled agn set not a 'SceneInstance': {self.parent}"
        return self.namespace[f"modelled-agn-{self.parent.name}-{agn.name}"]


class SceneInstance(IHasNamespaceDeclare):
    scene: SceneModel
    geometry: Optional[GeometrySpec]
    modelled_objs: list[ModelledObject]
    modelled_obj_sets: list[ModelledObjectSet]
    modelled_agns: list[ModelledAgent]
    modelled_agn_sets: list[ModelledAgentSet]

    def __init__(
        self,
        parent,
        ns,
        name,
        scene,
        geometry,
        modelled_objs,
        modelled_obj_sets,
        modelled_agns,
        modelled_agn_sets,
    ) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.scene = scene
        self.geometry = geometry
        self.modelled_objs = modelled_objs
        self.modelled_obj_sets = modelled_obj_sets
        self.modelled_agns = modelled_agns
        self.modelled_agn_sets = modelled_agn_sets
