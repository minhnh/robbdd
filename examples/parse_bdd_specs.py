#!/usr/bin/env python
from os.path import abspath, dirname, join
from textx import metamodel_for_language
from pprint import pprint
from sys import argv

CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(argv[1])
    print(model.stories[0].uri_n3)
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
        for row in scenario_variant.variation.rows:
            print([cell.value.name for cell in row.cells])

if __name__ == "__main__":
    main()
