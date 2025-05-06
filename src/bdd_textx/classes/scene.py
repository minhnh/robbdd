# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from rdflib import URIRef
from bdd_textx.classes.common import IHasNamespaceDeclare


class Object(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name) -> None:
        super().__init__(ns=ns, name=name)
        self.parent = parent


class Workspace(IHasNamespaceDeclare):
    objects: list[Object]
    workspaces: list[Workspace]

    def __init__(self, parent, ns, name, objects, workspaces) -> None:
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.objects = objects
        self.workspaces = workspaces


class Agent(IHasNamespaceDeclare):
    def __init__(self, parent, ns, name) -> None:
        super().__init__(ns=ns, name=name)
        self.parent = parent


class SceneModel(IHasNamespaceDeclare):
    objects: list[Object]
    workspaces: list[Workspace]
    agents: list[Agent]
    scene_obj_uri: URIRef
    scene_ws_uri: URIRef
    scene_agn_uri: URIRef

    def __init__(self, parent, ns, name, objects, workspaces, agents) -> None:
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.objects = objects
        self.workspaces = workspaces
        self.agents = agents
        self.scene_obj_uri = self.namespace[f"{self.name}-scene-has-obj"]
        self.scene_ws_uri = self.namespace[f"{self.name}-scene-has-ws"]
        self.scene_agn_uri = self.namespace[f"{self.name}-scene-has-agn"]
