import logging
from rdflib.term import URIRef
from rdflib.namespace import Namespace


REGISTERED_NS = {}


class URIBase(object):
    pass


class URI(URIBase):
    def __init__(self, parent: object, val: str):
        self.parent = parent
        self.val = val
        self.uri = URIRef(val)
        self.uri_n3 = self.uri.n3()


class ShortURI(object):
    def __init__(self, parent: object, ns: str, name: str):
        self.parent = parent
        self.ns = ns
        self.name = name
        if ns not in REGISTERED_NS:
            raise ValueError(f"namespace '{ns}' not registered")

        self.ns_obj = Namespace(REGISTERED_NS[ns])
        self.uri = self.ns_obj[self.name]
        self.uri_n3 = self.uri.n3()


class NamespaceDeclare(object):
    def __init__(self, parent: object, name: str, uri: URI):
        self.parent = parent
        self.name = name
        self.uri = uri

        if self.name not in REGISTERED_NS:
            REGISTERED_NS[self.name] = self.uri.val
