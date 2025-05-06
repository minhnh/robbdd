#!/usr/bin/env python
import sys
from sys import argv
from os.path import abspath, dirname
from urllib.request import HTTPError
from rdflib import Graph
from textx import metamodel_for_language
from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import prepare_jinja2_template_data
from bdd_textx.graph import add_bdd_model_to_graph


CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(argv[1])
    g = Graph()
    add_bdd_model_to_graph(graph=g, model=model)
    print(g.serialize(format="json-ld"))
    install_resolver()
    # check_shacl_constraints(graph=g, shacl_dict=BDD_SHACL_URLS)

    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    _ = prepare_jinja2_template_data(us_loader, g)

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
