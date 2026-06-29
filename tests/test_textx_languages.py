#!/usr/bin/env python
import unittest
from os.path import dirname, join
from urllib.error import HTTPError
from rdflib import RDF
from textx import metamodel_for_language

from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from robbdd.rdf.scene import (
    URI_EXEC_TYPE_SCENE_REAL,
    URI_MJCF_MUJOCO,
    URI_EXEC_PRED_HAS_MODELLED_AGN,
    URI_EXEC_PRED_HAS_MODELLED_OBJ,
    URI_XML_DOCUMENT,
    create_scene_model_graph,
)
from robbdd.rdf.bdd import create_bdd_model_graph
from robbdd.rdf.bddx import create_bddx_model_graph
from bdd_dsl.models.urirefs import URI_BDD_PRED_OF_SCENE


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


class TestTextXLanguages(unittest.TestCase):
    def test_robbdd_scene(self):
        """Test scene-tx language"""
        scene_mm = metamodel_for_language("robbdd-scene")
        scene_model = scene_mm.model_from_file(join(MODELS_DIR, "lab.scene"))
        assert len(scene_model.scene_models) > 0
        assert len(scene_model.modelled_scenes) > 0
        g = create_scene_model_graph(scene_model)
        assert len(g) > 0
        modelled_scene = scene_model.modelled_scenes[0]
        assert (modelled_scene.uri, RDF.type, URI_EXEC_TYPE_SCENE_REAL) in g
        assert (
            modelled_scene.uri,
            URI_EXEC_PRED_HAS_MODELLED_OBJ,
            modelled_scene.modelled_objs[0].modelled_uri,
        ) in g
        assert (
            modelled_scene.uri,
            URI_EXEC_PRED_HAS_MODELLED_AGN,
            modelled_scene.modelled_agns[0].modelled_uri,
        ) in g
        modelled_agn = modelled_scene.modelled_agns[0]
        model_node = modelled_agn.models[0].uri
        assert (model_node, RDF.type, URI_MJCF_MUJOCO) in g
        assert (model_node, RDF.type, URI_XML_DOCUMENT) in g

    def test_robbdd(self):
        """Test RobBDD language"""
        bdd_mm = metamodel_for_language("robbdd")
        for model_name in [
            "pickplace_table.bdd",
            "pickplace_cart_product.bdd",
            "pickplace_quantifiers.bdd",
            "pickplace_table_custom.bdd",
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

    def test_robbdd_exec(self):
        """Test RobBDD execution language"""
        bddx_mm = metamodel_for_language("robbdd-exec")
        bddx_model = bddx_mm.model_from_file(join(MODELS_DIR, "pickplace_table_custom.bddx"))

        g = create_bddx_model_graph(model=bddx_model)
        assert len(g) > 0
        scr_exec = bddx_model.scenario_execs[0]
        assert (
            scr_exec.modelled_scene.uri,
            URI_BDD_PRED_OF_SCENE,
            scr_exec.variant.template.scene_uri,
        ) in g
