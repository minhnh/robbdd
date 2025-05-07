#!/usr/bin/env python
import sys
from sys import argv
from os.path import abspath, dirname, join
from urllib.request import HTTPError
from rdf_utils.uri import URL_SECORO_M
from textx import metamodel_for_language
from rdf_utils.resolver import install_resolver
from rdf_utils.naming import get_valid_filename
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import load_template_from_url, prepare_jinja2_template_data
from bdd_textx.graph import create_bdd_model_graph


CWD = abspath(dirname(__file__))
GENERATED_DIR = join(CWD, "generated")


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(argv[1])
    g = create_bdd_model_graph(model=model)
    print(g.serialize(format="json-ld"))
    install_resolver()
    # check_shacl_constraints(graph=g, shacl_dict=BDD_SHACL_URLS)

    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    processed_bdd_data = prepare_jinja2_template_data(us_loader, g)

    feature_template = load_template_from_url(
        f"{URL_SECORO_M}/acceptance-criteria/bdd/jinja/feature.jinja"
    )
    for us_data in processed_bdd_data:
        us_name = us_data["name"]
        feature_content = feature_template.render(data=us_data)
        feature_filename = f"{get_valid_filename(us_name)}.feature"
        filepath = join(GENERATED_DIR, feature_filename)
        with open(filepath, mode="w", encoding="utf-8") as of:
            of.write(feature_content)
            print(f"... wrote {filepath}")

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
