#!/usr/bin/env python
from os.path import abspath, dirname, join
from textx import metamodel_for_language


CWD = abspath(dirname(__file__))


def main():
    bdd_tx_mm = metamodel_for_language("bdd-tx")
    model = bdd_tx_mm.model_from_file(join(CWD, "models", "pickplace.bdd"))
    print(model.stories[0].uri.n3())


if __name__ == "__main__":
    main()
