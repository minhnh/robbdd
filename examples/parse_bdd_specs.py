#!/usr/bin/env python
from sys import argv
from os.path import abspath, dirname
from rdflib import Graph
from textx import metamodel_for_language
from rdf_utils.resolver import install_resolver
from rdf_utils.constraints import check_shacl_constraints
from bdd_dsl.models.user_story import BDD_SHACL_URLS
from bdd_textx.graph import add_bdd_model_to_graph


CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(argv[1])
    g = Graph()
    add_bdd_model_to_graph(graph=g, model=model)
    print(g.serialize(format="json-ld"))
    install_resolver()
    check_shacl_constraints(graph=g, shacl_dict=BDD_SHACL_URLS)

    print(model.stories[0].uri.n3())
    scenario_variant = model.stories[0].scenarios[0]
    print(
        f"found variant '{scenario_variant.name}' of template '{scenario_variant.template.name}', variations:"
    )
    if type(scenario_variant.variation).__name__ == "CartesianProductVariation":
        for var_entry in scenario_variant.variation.var_entries:
            print(
                f"- of '{var_entry.variable.name}':"
                f" objects=({', '.join([x.name for x in var_entry.objects])})"
                f" workspaces=({', '.join([x.name for x in var_entry.workspaces])})"
                f" agents=({', '.join([x.name for x in var_entry.agents])})"
            )
    elif type(scenario_variant.variation).__name__ == "TableVariation":
        for var in scenario_variant.variation.header.variables:
            print(var.uri)


if __name__ == "__main__":
    main()
