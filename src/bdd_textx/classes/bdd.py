from rdflib.namespace import Namespace


class UserStory(object):
    def __init__(self, parent, ns, name, role, feature, benefit, scenarios):
        self.parent = parent
        self.ns = ns
        self.name = name
        self.role = role
        self.feature = feature
        self.benefit = benefit
        self.scenarios = scenarios

        self._ns_obj = Namespace(self.ns.uri)
        self.uri = self._ns_obj[self.name]
        self.uri_n3 = self.uri.n3()


class ScenarioTemplate(object):
    def __init__(self, parent, ns, name, variables, givens):
        self.parent = parent
        self.ns = ns
        self.name = name
        self.variables = variables
        self.givens = givens

        self._ns_obj = Namespace(self.ns.uri)
        self.uri = self._ns_obj[self.name]
        self.uri_n3 = self.uri.n3()
