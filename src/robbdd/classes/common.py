# SPDX-License-Identifier: MPL-2.0
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
    _ns_obj: Namespace

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ns = kwargs.get("ns", None)
        assert self.ns is not None

        self.name = kwargs.get("name", None)
        assert self.name is not None

        self._ns_obj = Namespace(self.ns.uri)
        self.uri = self._ns_obj[self.name]

    @property
    def namespace(self) -> Namespace:
        return self._ns_obj


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
