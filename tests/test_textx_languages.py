#!/usr/bin/env python
import unittest
from os.path import dirname, join
from textx import metamodel_for_language


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


class TestTextXLanguages(unittest.TestCase):
    def test_scene_tx(self):
        """Test scene-tx language"""
        scene_tx_mm = metamodel_for_language("scene-tx")
        scene_model = scene_tx_mm.model_from_file(join(MODELS_DIR, "brsu.scene"))
        assert len(scene_model.model.objects) > 0
        assert len(scene_model.model.workspaces) > 0
        assert len(scene_model.model.agents) > 0

    def test_bdd_tx(self):
        """Test bdd-tx language"""
        bdd_tx_mm = metamodel_for_language("bdd-tx")
        bdd_model = bdd_tx_mm.model_from_file(join(MODELS_DIR, "pickplace.bdd"))
        assert len(bdd_model.templates) > 0
        assert len(bdd_model.stories) > 0
        assert len(bdd_model.stories[0].scenarios) > 0
        assert len(bdd_model.stories[0].scenarios[0].variations) > 0
