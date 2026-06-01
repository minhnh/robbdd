# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID, uuid4
from rdflib import Namespace, URIRef


class IHasParent(object):
    def __init__(self, **kwargs) -> None:
        self.parent = kwargs.get("parent", None)
        assert self.parent is not None, f"'parent' not handled for type '{self.__class__.__name__}'"


class IHasNamespace(IHasParent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def namespace(self) -> Namespace:
        raise NotImplementedError(
            f"'namespace' property not implemented for '{self.__class__.__name__}'"
        )


class IHasNamespaceDeclare(IHasNamespace):
    uri: URIRef
    ns_prefix: str
    _ns_obj: Namespace

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ns = kwargs.get("ns", None)
        assert self.ns is not None
        self.ns_prefix = self.ns.name

        self.name = kwargs.get("name", None)
        assert self.name is not None

        self._ns_obj = Namespace(self.ns.uri)
        self.uri = self._ns_obj[self.name]

    @property
    def namespace(self) -> Namespace:
        return self._ns_obj

    def __str__(self) -> str:
        return f"<({self.__class__.__name__}) {self.ns_prefix}:{self.name}>"


class IHasUUID(IHasParent):
    uuid: UUID

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.uuid = uuid4()

    @property
    def uri(self) -> URIRef:
        raise NotImplementedError(f"'uri' property not implemented for '{self.__class__.__name__}'")


class SetBase(IHasParent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


def parse_py_module_attr(model: Any) -> tuple[str, str]:
    modules = getattr(model, "modules", None)
    if not isinstance(modules, list):
        raise ValueError(
            f"PyModuleAttr {model} doesn't have 'modules' field of list type: {modules}"
        )
    module_name = ".".join(modules)
    attr_name = getattr(model, "attr_name", None)
    if attr_name is None:
        raise ValueError(f"PyModuleAttr {model} doesn't have valid 'attr_name' field")
    return module_name, attr_name
