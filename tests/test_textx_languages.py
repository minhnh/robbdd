import unittest
from os.path import dirname, join
from pathlib import Path
from urllib.error import HTTPError

from bdd_dsl.models.namespace import NS_MM_CSTR, NS_MM_OBS
from bdd_dsl.models.observation import (
    LinearDistanceEvaluator,
    ObservationPolicyEvaluator,
    ObservationStamped,
    ObsPolicyModel,
)
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
    URI_OBS_TYPE_DIRECT_TRINARY_POLICY,
    URI_OBS_TYPE_POLICY,
    URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER,
    URI_ROS_TYPE_TOPIC,
    URI_TIME_PRED_HRZN_SEC,
    URI_TIME_TYPE_AFTER_EVT,
)
from bdd_dsl.models.user_story import UserStoryLoader
from rdf_utils.models.vocab import (
    URI_EXEC_PRED_RUNS_SCENE,
    URI_EXEC_TYPE_SCENE_INST,
    URI_QUDT_PRED_QUANTITY_KIND,
    URI_QUDT_PRED_UNIT,
    URI_QUDT_PRED_VALUE,
    URI_QUDT_QK_FREQ,
    URI_QUDT_TYPE_QUANTITY,
)
from rdf_utils.namespace import NS_MM_GEOM_COORD, NS_MM_QUDT_UNIT
from rdf_utils.resolver import install_resolver
from rdflib import RDF, URIRef
from rdflib.namespace import SOSA
from scene_dsl.rdf.scene import create_scene_model_graph
from scene_dsl.rdf.sensors import URI_SENS_PRED_UPDATE_RATE
from textx import metamodel_for_language
from textx.exceptions import TextXSyntaxError

from robbdd.classes.bddx import EvaluatedObservationPolicy, RosTrinaryTopicPolicy
from robbdd.rdf.bdd import create_bdd_model_graph
from robbdd.rdf.bddx import create_bddx_model_graph


class TruthWithReasonEvaluator(ObservationPolicyEvaluator):
    def _evaluate_samples(self, samples):
        return bool(samples), "samples are present"


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


def load_observation_policy(graph, scr_var, policy):
    fluent = next(fc for fc in scr_var.fluent_clauses() if fc.id == policy.fluent.uri)
    return next(
        policy_model
        for policy_model in ObsPolicyModel.policies_for_fluent_clause(graph=graph, fc=fluent)
        if policy_model.id == policy.uri
    )


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
        assert all(
            isinstance(policy.policy_spec, RosTrinaryTopicPolicy)
            for policy in bddx_model.obs_policies
        )
        assert all(
            (policy.uri, RDF.type, URI_OBS_TYPE_DIRECT_TRINARY_POLICY) in graph
            and (policy.uri, RDF.type, URI_ROS_TYPE_TOPIC) in graph
            for policy in bddx_model.obs_policies
        )

    def test_robbdd_observations(self):
        bddx_model = metamodel_for_language("robbdd-exec").model_from_file(
            join(MODELS_DIR, "pickplace_observations.bddx")
        )
        graph = create_bddx_model_graph(model=bddx_model)

        policy = bddx_model.obs_policies[0]
        assert isinstance(policy.policy_spec, EvaluatedObservationPolicy)
        entity_state, recognized_poses = bddx_model.obs_providers

        assert (entity_state.uri, RDF.type, URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER) in graph
        assert (entity_state.uri, RDF.type, NS_MM_OBS.PoseProvider) in graph
        assert (entity_state.uri, RDF.type, SOSA.Sensor) in graph
        rate = graph.value(entity_state.uri, URI_SENS_PRED_UPDATE_RATE, any=False)
        assert isinstance(rate, URIRef)
        assert graph.value(rate, RDF.type, any=False) == URI_QUDT_TYPE_QUANTITY
        assert (
            graph.value(rate, URI_QUDT_PRED_VALUE, any=False).toPython()
            == entity_state.provider_spec.update_rate
        )
        assert graph.value(rate, URI_QUDT_PRED_UNIT, any=False) == NS_MM_QUDT_UNIT["HZ"]
        assert graph.value(rate, URI_QUDT_PRED_QUANTITY_KIND, any=False) == URI_QUDT_QK_FREQ
        assert (recognized_poses.uri, RDF.type, URI_ROS_TYPE_TOPIC) in graph
        assert (recognized_poses.uri, RDF.type, NS_MM_OBS.PoseProvider) not in graph
        assert all(
            (policy.uri, NS_MM_OBS["has-observation"], observation.uri) in graph
            and (observation.uri, URI_OBS_PRED_PROVIDER, entity_state.uri) in graph
            and (observation.uri, NS_MM_OBS["observes-target"], observation.target.uri) in graph
            for observation in policy.policy_spec.observations
        )
        assert any(graph.triples((None, RDF.type, NS_MM_CSTR.LinearDistanceConstraint)))
        assert any(graph.triples((None, NS_MM_GEOM_COORD.of, None)))
        assert graph.value(policy.uri, URI_TIME_PRED_HRZN_SEC, any=False).toPython() == 0.5
        assert graph.value(policy.fluent.uri, URI_TIME_PRED_HRZN_SEC, any=False) is None
        assert (policy.uri, RDF.type, URI_TIME_TYPE_AFTER_EVT) in graph

        bdd_model = metamodel_for_language("robbdd").model_from_file(
            join(MODELS_DIR, "pickplace_table_custom.bdd")
        )
        full_graph = create_bdd_model_graph(model=bdd_model)
        full_graph += graph
        scr_var = UserStoryLoader(full_graph).load_scenario_variant(
            full_graph=full_graph, variant_id=bddx_model.scenario_execs[0].variant.uri
        )
        policy_model = load_observation_policy(full_graph, scr_var, policy)
        assert isinstance(policy_model.evaluator, LinearDistanceEvaluator)
        assert policy_model.start_event is not None
        policy_model.on_event(policy_model.start_event, 1.0)
        accepted, _ = policy_model.add_samples(
            [
                ObservationStamped(
                    observation_uri=observation.uri,
                    provider_uri=observation.provider.uri,
                    stamp=1.1,
                    value=position,
                )
                for observation, position in zip(
                    policy.policy_spec.observations, ((0.0, 0.0, 0.0), (0.1, 0.0, 0.0)), strict=True
                )
            ]
        )
        assert accepted

    def test_robbdd_python_observation_policy(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        model_text = fixture.read_text().replace(
            """    evaluator: linear distance {
        equals: 0.10 m tolerance: 0.01 m
    }""",
            """    evaluator: py { module: test_textx_languages, attr: TruthWithReasonEvaluator}""",
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
        assert graph.value(policy.uri, NS_MM_OBS["time-extractor"], any=False) is None
        assert all(
            graph.value(observation.uri, NS_MM_OBS["time-extractor"], any=False)
            == observation.time_extractor_uri
            for observation in policy.policy_spec.observations
        )
        assert graph.value(policy.uri, NS_MM_OBS["has-evaluator"], any=False) is not None

        policy_model = load_observation_policy(full_graph, scr_var, policy)
        assert isinstance(policy_model.evaluator, TruthWithReasonEvaluator)
        if policy_model.start_event is not None:
            policy_model.on_event(policy_model.start_event, 1.0)
        accepted, _ = policy_model.add_samples(
            [
                ObservationStamped(
                    observation_uri=observation.uri,
                    provider_uri=observation.provider.uri,
                    stamp=stamp,
                    value=True,
                )
                for stamp, observation in zip(
                    (1.1, 1.2), policy.policy_spec.observations, strict=True
                )
            ]
        )
        assert accepted
        assert policy_model.trinary_timeline[-1].reason == "samples are present"
        assert policy_model.trinary_timeline[-1].trinary

    def test_linear_distance_constraint_forms_round_trip_to_bdd_dsl(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        original = "equals: 0.10 m tolerance: 0.01 m"
        cases = (
            ("less-than: 10 cm", False),
            ("greater-than: 100 mm", False),
            ("between: 10 cm and 0.2 m", True),
            ("equals: 100 mm tolerance: 0 mm", True),
        )
        bdd_model = metamodel_for_language("robbdd").model_from_file(
            join(MODELS_DIR, "pickplace_table_custom.bdd")
        )
        for constraint, expected in cases:
            with self.subTest(constraint=constraint):
                model = metamodel_for_language("robbdd-exec").model_from_str(
                    fixture.read_text().replace(original, constraint),
                    file_name=str(fixture),
                )
                graph = create_bdd_model_graph(model=bdd_model)
                graph += create_bddx_model_graph(model=model)
                scr_var = UserStoryLoader(graph).load_scenario_variant(
                    full_graph=graph, variant_id=model.scenario_execs[0].variant.uri
                )
                policy = load_observation_policy(graph, scr_var, model.obs_policies[0])
                assert policy.start_event is not None
                policy.on_event(policy.start_event, 1.0)
                accepted, _ = policy.add_samples(
                    [
                        ObservationStamped(
                            observation.uri,
                            observation.provider.uri,
                            1.1,
                            position,
                        )
                        for observation, position in zip(
                            model.obs_policies[0].policy_spec.observations,
                            ((0.0, 0.0, 0.0), (0.1, 0.0, 0.0)),
                            strict=True,
                        )
                    ]
                )
                assert accepted
                assert policy.trinary_timeline[-1].trinary is expected

    def test_observation_target_qualifiers_round_trip_to_bdd_dsl(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        original = "observes var <tmpl_pickplace.target_object>"
        targets = (
            ("obj", "pickplace_objects.box1"),
            ("agn", "isaac_agents.panda"),
            ("ws", "lab_workspaces.table_ws"),
        )
        bdd_model = metamodel_for_language("robbdd").model_from_file(
            join(MODELS_DIR, "pickplace_table_custom.bdd")
        )
        scene_model = metamodel_for_language("scene").model_from_file(join(MODELS_DIR, "lab.scene"))
        scene_graph = create_scene_model_graph(model=scene_model)
        for qualifier, target in targets:
            with self.subTest(qualifier=qualifier):
                model_text = fixture.read_text().replace(
                    'import "lab.scenex"', 'import "lab.scenex"\nimport "lab.scene"'
                )
                model = metamodel_for_language("robbdd-exec").model_from_str(
                    model_text.replace(original, f"observes {qualifier} <{target}>"),
                    file_name=str(fixture),
                )
                graph = create_bdd_model_graph(model=bdd_model)
                target_uri = model.obs_policies[0].policy_spec.observations[0].target.uri
                for triple in scene_graph.triples((target_uri, RDF.type, None)):
                    graph.add(triple)
                graph += create_bddx_model_graph(model=model)
                UserStoryLoader(graph).load_scenario_variant(
                    full_graph=graph, variant_id=model.scenario_execs[0].variant.uri
                )

    def test_robbdd_fluent_horizon_is_rejected(self):
        fixture = Path(join(MODELS_DIR, "pickplace_table_custom.bdd"))
        invalid_model = fixture.read_text().replace(
            "after <evt-place-end>", "0.5 seconds after <evt-place-end>"
        )
        with self.assertRaises(TextXSyntaxError):
            metamodel_for_language("robbdd").model_from_str(
                invalid_model,
                file_name=str(fixture),
            )

    def test_robbdd_during_policy_horizon_is_rejected(self):
        fixture = Path(join(MODELS_DIR, "pickplace_table_custom.bddx"))
        invalid_model = fixture.read_text().replace(
            "for <pickplace_table.fc-collide>\n{",
            "for <pickplace_table.fc-collide>\n    horizon: 0.5 seconds\n{",
        )
        model = metamodel_for_language("robbdd-exec").model_from_str(
            invalid_model,
            file_name=str(fixture),
        )
        with self.assertRaisesRegex(ValueError, "during horizon"):
            create_bddx_model_graph(model=model)

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

    def test_simulation_provider_rejects_non_positive_update_rate(self):
        fixture = Path(join(MODELS_DIR, "pickplace_observations.bddx"))
        model = metamodel_for_language("robbdd-exec").model_from_str(
            fixture.read_text().replace("update-rate: 10 Hz", "update-rate: 0 Hz"),
            file_name=str(fixture),
        )
        with self.assertRaisesRegex(ValueError, "must be positive"):
            create_bddx_model_graph(model=model)
