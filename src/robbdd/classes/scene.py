# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from typing import Any, Optional
from rdflib import URIRef, Namespace
from robbdd.classes.common import IHasNamespace, IHasNamespaceDeclare, SetBase


class ElementModel(IHasNamespace):
    model_spec: Any
    _uri: Optional[URIRef]

    def __init__(self, parent, name, model_spec) -> None:
        super().__init__(parent=parent)
        self.name = name
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


class Object(IHasNamespace):
    models: Optional[list[ElementModel]]
    _uri: Optional[URIRef]
    _modelled_uri: Optional[URIRef]

    def __init__(self, parent, name, models) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.models = models
        self._uri = None
        self._modelled_uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(
            self.parent, ObjectSet
        ), f"parent of obj not an 'ObjectSet': {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri

    @property
    def modelled_uri(self) -> URIRef:
        if self._modelled_uri is None:
            self._modelled_uri = self.namespace[f"modelled-{self.name}"]
        return self._modelled_uri


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
    models: Optional[list[ElementModel]]
    _uri: Optional[URIRef]
    _modelled_uri: Optional[URIRef]

    def __init__(self, parent, name, models) -> None:
        super().__init__(parent=parent)
        self.name = name
        self.models = models
        self._uri = None
        self._modelled_uri = None

    @property
    def namespace(self) -> Namespace:
        assert isinstance(self.parent, AgentSet), f"parent of agn not an 'AgentSet': {self.parent}"
        return self.parent.namespace

    @property
    def uri(self) -> URIRef:
        if self._uri is None:
            self._uri = self.namespace[self.name]
        return self._uri

    @property
    def modelled_uri(self) -> URIRef:
        if self._modelled_uri is None:
            self._modelled_uri = self.namespace[f"modelled-{self.name}"]
        return self._modelled_uri


class SceneSet(SetBase, IHasNamespaceDeclare):
    def __init__(self, parent, ns, name) -> None:
        super().__init__(parent=parent, ns=ns, name=name)


class ObjectSet(SceneSet):
    objects: list[Object]

    def __init__(self, parent, ns, name, objects) -> None:
        super().__init__(parent=parent, ns=ns, name=name)
        self.objects = objects


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
    obj_sets: list[ObjectSet]
    ws_sets: list[WorkspaceSet]
    ws_comps: list[WorkspaceComposition]
    agn_sets: list[AgentSet]
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
