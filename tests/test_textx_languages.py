#!/usr/bin/env python
import unittest
from os.path import dirname, join
from urllib.error import HTTPError

from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_HAS_AC,
    URI_BDD_PRED_HAS_BHV_IMPL,
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_HAS_VARIATION,
    URI_BDD_PRED_OF_SCENE,
    URI_BDD_PRED_OF_TMPL,
    URI_BDD_PRED_OF_VARIANT,
    URI_BDD_TYPE_BHV_IMPL,
    URI_BDD_TYPE_SCENARIO,
    URI_BDD_TYPE_SCENARIO_EXEC,
    URI_BDD_TYPE_SCENARIO_TMPL,
    URI_BDD_TYPE_SCENARIO_VARIANT,
    URI_BDD_TYPE_US,
    URI_OBS_PRED_POLICY,
    URI_OBS_TYPE_POLICY,
)
from bdd_dsl.models.user_story import UserStoryLoader
from rdf_utils.resolver import install_resolver
from rdf_utils.models.vocab import URI_EXEC_TYPE_SCENE_INST
from rdflib import RDF
from textx import metamodel_for_language

from robbdd.rdf.bdd import create_bdd_model_graph
from robbdd.rdf.bddx import create_bddx_model_graph


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


def assert_bdd_graph_contract(model, graph):
    for tmpl in model.templates:
        assert (tmpl.uri, RDF.type, URI_BDD_TYPE_SCENARIO_TMPL) in graph
        assert (tmpl.scenario_uri, RDF.type, URI_BDD_TYPE_SCENARIO) in graph
        assert (tmpl.uri, URI_BDD_PRED_HAS_SCENE, tmpl.scene_uri) in graph

    for story in model.stories:
        assert story.scenarios
        assert (story.uri, RDF.type, URI_BDD_TYPE_US) in graph
        for variant in story.scenarios:
            assert (variant.uri, RDF.type, URI_BDD_TYPE_SCENARIO_VARIANT) in graph
            assert (story.uri, URI_BDD_PRED_HAS_AC, variant.uri) in graph
            assert (variant.uri, URI_BDD_PRED_OF_TMPL, variant.template.uri) in graph
            assert (variant.uri, URI_BDD_PRED_HAS_VARIATION, variant.variation.uri) in graph


def assert_bddx_graph_contract(model, graph):
    assert model.scenario_execs
    for scr_exec in model.scenario_execs:
        assert (scr_exec.uri, RDF.type, URI_BDD_TYPE_SCENARIO_EXEC) in graph
        assert (scr_exec.uri, URI_BDD_PRED_OF_VARIANT, scr_exec.variant.uri) in graph
        assert (scr_exec.scene_inst.uri, RDF.type, URI_EXEC_TYPE_SCENE_INST) in graph
        assert (
            scr_exec.scene_inst.uri,
            URI_BDD_PRED_OF_SCENE,
            scr_exec.variant.template.scene_uri,
        ) in graph
        assert (scr_exec.uri, URI_BDD_PRED_HAS_BHV_IMPL, scr_exec.bhv_impl.uri) in graph
        assert (scr_exec.bhv_impl.uri, RDF.type, URI_BDD_TYPE_BHV_IMPL) in graph

        for obs_policy in scr_exec.obs_policies:
            assert (scr_exec.uri, URI_OBS_PRED_POLICY, obs_policy.uri) in graph
            assert (obs_policy.uri, RDF.type, URI_OBS_TYPE_POLICY) in graph


class TestTextXLanguages(unittest.TestCase):
    def setUp(self) -> None:
        install_resolver()

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
            assert bdd_model.templates
            assert bdd_model.stories

            graph = create_bdd_model_graph(model=bdd_model)
            assert graph
            assert_bdd_graph_contract(bdd_model, graph)
            try:
                _ = UserStoryLoader(graph)
            except HTTPError as e:
                raise RuntimeError(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")

    def test_robbdd_exec(self):
        """Test RobBDD execution language"""
        bddx_mm = metamodel_for_language("robbdd-exec")
        bddx_model = bddx_mm.model_from_file(join(MODELS_DIR, "pickplace_table_custom.bddx"))

        graph = create_bddx_model_graph(model=bddx_model)
        assert graph
        assert_bddx_graph_contract(bddx_model, graph)
