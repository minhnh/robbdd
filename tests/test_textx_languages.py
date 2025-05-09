#!/usr/bin/env python
import unittest
from os.path import dirname, join
from textx import metamodel_for_language


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


class TestTextXLanguages(unittest.TestCase):
    def test_robbdd_scene(self):
        """Test scene-tx language"""
        scene_mm = metamodel_for_language("robbdd-scene")
        scene_model = scene_mm.model_from_file(join(MODELS_DIR, "lab.scene"))
        assert len(scene_model.model.objects) > 0
        assert len(scene_model.model.workspaces) > 0
        assert len(scene_model.model.agents) > 0

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
