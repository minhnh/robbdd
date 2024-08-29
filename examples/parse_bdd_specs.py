#!/usr/bin/env python
from os.path import abspath, dirname, join
from textx import metamodel_for_language
from pprint import pprint

CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(join(CWD, "models", "pickplace_table.bdd"))
    print(model.stories[0].uri_n3)
    scenario_variant = model.stories[0].scenarios[0]
    print(
        f"found variant '{scenario_variant.name}' of template '{scenario_variant.template.name}', variations:"
    )
    #pprint(scenario_variant.__dict__)
    for variation in scenario_variant.variations:
        #pprint(variation.__dict__)
        if type(variation).__name__ == "TaskVariation":
            print(
                f"- of '{variation.variable.name}':"
                f" objects=({', '.join([x.name for x in variation.objects])})"
                f" workspaces=({', '.join([x.name for x in variation.workspaces])})"
                f" agents=({', '.join([x.name for x in variation.agents])})"
            )
        elif type(variation).__name__ == "TableVariation":
            print(
                f"variating task '{variation.task}'"
                f" {variation.variable.name} is"
                f" {variation.object} or {variation.workspace} or {variation.agent}"
            )

if __name__ == "__main__":
    main()
