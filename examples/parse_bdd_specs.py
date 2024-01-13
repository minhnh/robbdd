#!/usr/bin/env python
from os.path import abspath, dirname, join
from textx import metamodel_for_language


CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(join(CWD, "models", "pickplace.bdd"))
    print(model.stories[0].uri_n3)
    scenario_variant = model.stories[0].scenarios[0]
    print(
        f"found variant '{scenario_variant.name}' of template '{scenario_variant.template.name}', variations:"
    )
    for variation in scenario_variant.variations:
        print(
            f"- of '{variation.variable.name}':"
            f" objects=({', '.join([x.name for x in variation.objects])})"
            f" workspaces=({', '.join([x.name for x in variation.workspaces])})"
            f" agents=({', '.join([x.name for x in variation.agents])})"
        )
    print(model.templates[0].uri_n3)


if __name__ == "__main__":
    main()
