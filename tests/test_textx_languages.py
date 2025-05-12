#!/usr/bin/env python
import unittest
from os.path import dirname, join
from urllib.error import HTTPError
from textx import metamodel_for_language

from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from robbdd.graph import create_bdd_model_graph


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


class TestTextXLanguages(unittest.TestCase):
    def test_robbdd_scene(self):
        """Test scene-tx language"""
        scene_mm = metamodel_for_language("robbdd-scene")
        scene_model = scene_mm.model_from_file(join(MODELS_DIR, "lab.scene"))
        assert len(scene_model.scene_models) > 0

    def test_robbdd(self):
        """Test RobBDD language"""
        bdd_mm = metamodel_for_language("robbdd")
        for model_name in [
            "pickplace_table.bdd",
            "pickplace_cart_product.bdd",
            "pickplace_quantifiers.bdd",
        ]:
            bdd_model = bdd_mm.model_from_file(join(MODELS_DIR, model_name))
            assert len(bdd_model.templates) > 0
            assert len(bdd_model.stories) > 0
            assert len(bdd_model.stories[0].scenarios) > 0

            g = create_bdd_model_graph(model=bdd_model)
            install_resolver()
            try:
                _ = UserStoryLoader(g)
            except HTTPError as e:
                raise RuntimeError(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
