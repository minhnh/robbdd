import unittest
from pathlib import Path
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
    URI_OBS_PRED_PROVIDER,
    URI_OBS_TYPE_POLICY,
    URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER,
    URI_ROS_TYPE_TOPIC,
)
from bdd_dsl.models.namespace import NS_MM_CSTR, NS_MM_OBS
from bdd_dsl.models.observation import ObservationManager, ObservationStamped
from bdd_dsl.models.user_story import UserStoryLoader
from rdf_utils.models.vocab import URI_EXEC_PRED_RUNS_SCENE, URI_EXEC_TYPE_SCENE_INST
from rdf_utils.namespace import NS_MM_GEOM_COORD
from rdf_utils.resolver import install_resolver
from rdflib import RDF
from textx import metamodel_for_language
from textx.exceptions import TextXSyntaxError

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
        assert (
            scr_exec.uri,
            URI_EXEC_PRED_RUNS_SCENE,
            scr_exec.scene_inst.uri,
        ) in graph
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

    def test_robbdd_observations(self):
        bddx_model = metamodel_for_language("robbdd-exec").model_from_file(
            join(MODELS_DIR, "pickplace_observations.bddx")
        )
        graph = create_bddx_model_graph(model=bddx_model)

        policy = bddx_model.obs_policies[0]
        entity_state, recognized_poses = bddx_model.obs_providers

        assert (entity_state.uri, RDF.type, URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER) in graph
        assert (entity_state.uri, RDF.type, NS_MM_OBS.PoseProvider) in graph
        assert (recognized_poses.uri, RDF.type, URI_ROS_TYPE_TOPIC) in graph
        assert (recognized_poses.uri, RDF.type, NS_MM_OBS.PoseProvider) not in graph
        assert all(
            (policy.uri, NS_MM_OBS["has-observation"], observation.uri) in graph
            and (observation.uri, URI_OBS_PRED_PROVIDER, entity_state.uri) in graph
            and (observation.uri, NS_MM_OBS["observes-target"], observation.target.uri) in graph
            for observation in policy.observations
        )
        assert any(graph.triples((None, RDF.type, NS_MM_CSTR.LinearDistanceConstraint)))
        assert any(graph.triples((None, NS_MM_GEOM_COORD.of, None)))

    def test_robbdd_python_observation_policy(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        model_text = fixture.read_text().replace(
            """    linear distance between <object-pose> and <workspace-pose> {
        equals: 0.10 m tolerance: 0.01 m
    }""",
            """    py { module: operator, attr: truth}""",
        )
        model = metamodel_for_language("robbdd-exec").model_from_str(
            model_text, file_name=str(fixture)
        )
        policy = model.obs_policies[0]
        graph = create_bddx_model_graph(model=model)

        bdd_model = metamodel_for_language("robbdd").model_from_file(
            join(MODELS_DIR, "pickplace_table_custom.bdd")
        )
        full_graph = create_bdd_model_graph(model=bdd_model)
        full_graph += graph
        scr_var = UserStoryLoader(full_graph).load_scenario_variant(
            full_graph=full_graph, variant_id=model.scenario_execs[0].variant.uri
        )
        manager = ObservationManager.from_scenario_variant(
            graph=full_graph,
            scr_var=scr_var,
            bhv_loaders=[],
            obs_loaders=[],
        )
        assert policy.uri in manager.obs_policies

        policy_model = manager.obs_policies[policy.uri]
        if policy_model.start_event is not None:
            manager.on_event(policy_model.start_event, 1.0)
        for stamp, observation in zip((1.1, 1.2), policy.observations, strict=True):
            accepted, message = manager.update_observation(
                ObservationStamped(
                    observation_uri=observation.uri,
                    provider_uri=observation.provider.uri,
                    stamp=stamp,
                    value=True,
                )
            )
            assert accepted, message
        assert manager.obs_policies[policy.uri].trinary_timeline[-1].trinary

    def test_robbdd_between_rejects_tolerance(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        invalid_model = fixture.read_text().replace(
            "equals: 0.10 m tolerance: 0.01 m",
            "between: 0.05 m and 0.10 m tolerance: 0.01 m",
        )
        with self.assertRaises(TextXSyntaxError):
            metamodel_for_language("robbdd-exec").model_from_str(
                invalid_model,
                file_name=str(fixture),
            )
