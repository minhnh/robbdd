# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
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

    def __init__(self, parent, ns, name, objects, workspaces, agents) -> None:
        super().__init__(ns=ns, name=name)
        self.parent = parent
        self.objects = objects
        self.workspaces = workspaces
        self.agents = agents
