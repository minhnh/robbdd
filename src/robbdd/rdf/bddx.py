# SPDX-License-Identifier: MPL-2.0
from typing import Any

from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_HAS_BHV_IMPL,
    URI_BDD_PRED_OF_CLAUSE,
    URI_BDD_PRED_OF_VARIANT,
    URI_BDD_TYPE_BHV_IMPL,
    URI_BDD_TYPE_SCENARIO_EXEC,
    URI_BHV_PRED_OF_BHV,
    URI_CSTR_PRED_HAS_CONSTRAINT,
    URI_CSTR_PRED_LOWER_THRESHOLD,
    URI_CSTR_PRED_QUANTITY,
    URI_CSTR_PRED_REFERENCE_VALUE,
    URI_CSTR_PRED_THRESHOLD,
    URI_CSTR_PRED_TOLERANCE,
    URI_CSTR_PRED_UPPER_THRESHOLD,
    URI_CSTR_TYPE_BILATERAL,
    URI_CSTR_TYPE_EQUALITY,
    URI_CSTR_TYPE_GREATER_THAN,
    URI_CSTR_TYPE_LESS_THAN,
    URI_CSTR_TYPE_LINEAR_DISTANCE,
    URI_GEOM_PRED_BETWEEN_ENTITIES,
    URI_GEOM_PRED_COORD_OF,
    URI_GEOM_TYPE_DISTANCE_REF,
    URI_GEOM_TYPE_LINEAR_DISTANCE,
    URI_GEOM_TYPE_LINEAR_DISTANCE_COORD,
    URI_OBS_PRED_ENTITY_MAPPER,
    URI_OBS_PRED_HAS_EVALUATOR,
    URI_OBS_PRED_HAS_OBSERVATION,
    URI_OBS_PRED_OBSERVES_TARGET,
    URI_OBS_PRED_POLICY,
    URI_OBS_PRED_PROVIDER,
    URI_OBS_PRED_TIME_EXTRACTOR,
    URI_OBS_TYPE_DIRECT_TRINARY_POLICY,
    URI_OBS_TYPE_EVALUATED_POLICY,
    URI_OBS_TYPE_LINEAR_DISTANCE_EVALUATOR,
    URI_OBS_TYPE_OBSERVATION,
    URI_OBS_TYPE_POLICY,
    URI_OBS_TYPE_POSE_PROVIDER,
    URI_OBS_TYPE_PROVIDER,
    URI_QUDT_QK_DISTANCE,
    URI_ROS_PRED_CHNL_NAME,
    URI_ROS_PRED_TYPE_NAME,
    URI_ROS_TYPE_ACTION,
    URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER,
    URI_ROS_TYPE_TOPIC,
)
from rdf_utils.models.vocab import (
    URI_EXEC_PRED_RUNS_SCENE,
    URI_QUDT_PRED_QUANTITY_KIND,
    URI_QUDT_PRED_UNIT,
    URI_QUDT_PRED_VALUE,
    URI_QUDT_QK_FREQ,
    URI_QUDT_TYPE_QUANTITY,
)
from rdf_utils.namespace import NS_MM_QUDT_UNIT
from rdflib import RDF, XSD, Graph, Literal, URIRef
from rdflib.namespace import SOSA
from scene_dsl.rdf.common import add_py_module_attr
from scene_dsl.rdf.geom import LENGTH_UNITS
from scene_dsl.rdf.scenex import add_modelled_scene
from scene_dsl.rdf.sensors import URI_SENS_PRED_UPDATE_RATE

from robbdd.classes.bdd import DuringEvent
from robbdd.classes.bddx import (
    BehaviourImplementation,
    EvaluatedObservationPolicy,
    LinearDistanceEvaluator,
    Observation,
    ObservationPolicy,
    ObservationProvider,
    RosTrinaryTopicPolicy,
    ScenarioExecution,
)
from robbdd.rdf.clauses import add_node_time_constraint


def add_bhv_impl_to_graph(graph: Graph, bhv_impl: BehaviourImplementation) -> None:
    graph.bind(prefix=bhv_impl.ns_prefix, namespace=bhv_impl.namespace)
    graph.add(triple=(bhv_impl.uri, RDF.type, URI_BDD_TYPE_BHV_IMPL))

    bhv_spec_type = bhv_impl.bhv_spec.__class__.__name__
    if "RosBhvAction" in bhv_spec_type:
        graph.add(triple=(bhv_impl.uri, RDF.type, URI_ROS_TYPE_ACTION))
        action_name = bhv_impl.bhv_spec.action_name
        graph.add(
            triple=(bhv_impl.uri, URI_ROS_PRED_TYPE_NAME, Literal("bdd_ros2_interfaces/Behaviour"))
        )
        graph.add(triple=(bhv_impl.uri, URI_ROS_PRED_CHNL_NAME, Literal(action_name)))
        return

    if "PyModuleAttr" in bhv_spec_type:
        add_py_module_attr(graph=graph, node_uri=bhv_impl.uri, py_model=bhv_impl.bhv_spec)
        return

    raise ValueError(f"unhandled PolicySpec type: {bhv_impl.bhv_spec.__class__}")


def add_obs_provider_to_graph(graph: Graph, provider: ObservationProvider) -> None:
    graph.bind(prefix=provider.ns_prefix, namespace=provider.namespace)
    graph.add((provider.uri, RDF.type, URI_OBS_TYPE_PROVIDER))
    spec_type = provider.provider_spec.__class__.__name__
    if spec_type == "SimulationEntityStateProvider":
        if provider.provider_spec.update_rate <= 0:
            raise ValueError("simulation entity-state update-rate must be positive")
        graph.add((provider.uri, RDF.type, URI_OBS_TYPE_POSE_PROVIDER))
        graph.add((provider.uri, RDF.type, URI_ROS_TYPE_SIM_ENTITY_STATE_PROVIDER))
        graph.add((provider.uri, RDF.type, SOSA.Sensor))
        update_rate_uri = provider.namespace[f"{provider.name}/update-rate"]
        graph.add((provider.uri, URI_SENS_PRED_UPDATE_RATE, update_rate_uri))
        graph.add((update_rate_uri, RDF.type, URI_QUDT_TYPE_QUANTITY))
        graph.add(
            (
                update_rate_uri,
                URI_QUDT_PRED_VALUE,
                Literal(provider.provider_spec.update_rate, datatype=XSD.double),
            )
        )
        graph.add((update_rate_uri, URI_QUDT_PRED_UNIT, NS_MM_QUDT_UNIT["HZ"]))
        graph.add((update_rate_uri, URI_QUDT_PRED_QUANTITY_KIND, URI_QUDT_QK_FREQ))
        return

    if spec_type == "RosTopicProvider":
        graph.add((provider.uri, RDF.type, URI_ROS_TYPE_TOPIC))
        graph.add(
            (provider.uri, URI_ROS_PRED_CHNL_NAME, Literal(provider.provider_spec.topic_name))
        )
        graph.add((provider.uri, URI_ROS_PRED_TYPE_NAME, Literal(provider.provider_spec.type_name)))
        return

    raise ValueError(f"unhandled observation provider type: {provider.provider_spec.__class__}")


def add_observation_to_graph(
    graph: Graph, observation: Observation, policy: ObservationPolicy
) -> None:
    graph.add((observation.uri, RDF.type, URI_OBS_TYPE_OBSERVATION))
    graph.add((policy.uri, URI_OBS_PRED_HAS_OBSERVATION, observation.uri))
    graph.add((observation.uri, URI_OBS_PRED_PROVIDER, observation.provider.uri))
    if observation.target is not None:
        graph.add((observation.uri, URI_OBS_PRED_OBSERVES_TARGET, observation.target.uri))


def add_distance_value(graph: Graph, value, quantity_uri: URIRef) -> URIRef:
    graph.add((quantity_uri, RDF.type, URI_QUDT_QK_DISTANCE))
    graph.add((quantity_uri, URI_QUDT_PRED_VALUE, Literal(value.value, datatype=XSD.double)))
    graph.add((quantity_uri, URI_QUDT_PRED_UNIT, LENGTH_UNITS[value.unit]))
    return quantity_uri


def add_linear_distance_to_graph(
    graph: Graph,
    eval_uri: URIRef,
    evaluator: LinearDistanceEvaluator,
    observations: list[Observation],
) -> None:
    if len(observations) != 2:
        raise ValueError(f"LinearDistanceEvaluator {eval_uri} requires exactly two observations")
    graph.add(triple=(eval_uri, RDF.type, URI_OBS_TYPE_LINEAR_DISTANCE_EVALUATOR))
    graph.add(triple=(eval_uri, RDF.type, URI_GEOM_TYPE_LINEAR_DISTANCE))
    for obs in observations:
        graph.add((eval_uri, URI_GEOM_PRED_BETWEEN_ENTITIES, obs.uri))

    coord_uri = evaluator.coordinate_uri
    cstr_uri = evaluator.constraint_uri
    graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_LINEAR_DISTANCE_COORD))
    graph.add(triple=(coord_uri, RDF.type, URI_GEOM_TYPE_DISTANCE_REF))
    graph.add(triple=(coord_uri, URI_QUDT_PRED_QUANTITY_KIND, URI_QUDT_QK_DISTANCE))
    graph.add(triple=(coord_uri, URI_GEOM_PRED_COORD_OF, eval_uri))
    graph.add(triple=(eval_uri, URI_CSTR_PRED_HAS_CONSTRAINT, cstr_uri))
    graph.add(triple=(cstr_uri, RDF.type, URI_CSTR_TYPE_LINEAR_DISTANCE))
    graph.add(triple=(cstr_uri, URI_CSTR_PRED_QUANTITY, coord_uri))

    distance = evaluator.constraint
    lower_uri = evaluator.lower_uri
    upper_uri = evaluator.upper_uri
    if distance.less_than is not None:
        graph.add((cstr_uri, RDF.type, URI_CSTR_TYPE_LESS_THAN))
        graph.add(
            (
                cstr_uri,
                URI_CSTR_PRED_THRESHOLD,
                add_distance_value(graph, distance.less_than, upper_uri),
            )
        )
    elif distance.greater_than is not None:
        graph.add((cstr_uri, RDF.type, URI_CSTR_TYPE_GREATER_THAN))
        graph.add(
            triple=(
                cstr_uri,
                URI_CSTR_PRED_THRESHOLD,
                add_distance_value(graph, distance.greater_than, lower_uri),
            )
        )
    elif distance.lower is not None:
        graph.add((cstr_uri, RDF.type, URI_CSTR_TYPE_BILATERAL))
        graph.add(
            triple=(
                cstr_uri,
                URI_CSTR_PRED_LOWER_THRESHOLD,
                add_distance_value(graph, distance.lower, lower_uri),
            )
        )
        graph.add(
            triple=(
                cstr_uri,
                URI_CSTR_PRED_UPPER_THRESHOLD,
                add_distance_value(graph, distance.upper, upper_uri),
            )
        )
    else:
        graph.add(triple=(cstr_uri, RDF.type, URI_CSTR_TYPE_EQUALITY))
        graph.add(
            triple=(
                cstr_uri,
                URI_CSTR_PRED_REFERENCE_VALUE,
                add_distance_value(graph, distance.equals, evaluator.ref_value_uri),
            )
        )
        graph.add(
            triple=(
                cstr_uri,
                URI_CSTR_PRED_TOLERANCE,
                add_distance_value(graph, distance.tolerance, evaluator.tolerance_uri),
            )
        )


def add_obs_pol_to_graph(graph: Graph, obs_pol: ObservationPolicy) -> None:
    graph.bind(prefix=obs_pol.ns_prefix, namespace=obs_pol.namespace)
    graph.add(triple=(obs_pol.uri, RDF.type, URI_OBS_TYPE_POLICY))
    graph.add(triple=(obs_pol.uri, URI_BDD_PRED_OF_CLAUSE, obs_pol.fluent.uri))
    policy_horizon = obs_pol.policy_horizon.val if obs_pol.policy_horizon is not None else None
    if isinstance(obs_pol.fluent.tc, DuringEvent) and policy_horizon is not None:
        raise ValueError(f"ObservationPolicy '{obs_pol.uri}' must not specify a during horizon")
    add_node_time_constraint(
        graph=graph,
        tc=obs_pol.fluent.tc,
        node_uri=obs_pol.uri,
        horizon=policy_horizon,
    )

    if isinstance(obs_pol.policy_spec, RosTrinaryTopicPolicy):
        graph.add(triple=(obs_pol.uri, RDF.type, URI_OBS_TYPE_DIRECT_TRINARY_POLICY))
        graph.add(triple=(obs_pol.uri, RDF.type, URI_ROS_TYPE_TOPIC))
        topic_name = obs_pol.policy_spec.topic_name
        graph.add(
            triple=(
                obs_pol.uri,
                URI_ROS_PRED_TYPE_NAME,
                Literal("bdd_ros2_interfaces/TrinaryStamped"),
            )
        )
        graph.add(triple=(obs_pol.uri, URI_ROS_PRED_CHNL_NAME, Literal(topic_name)))
        return

    if isinstance(obs_pol.policy_spec, EvaluatedObservationPolicy):
        spec = obs_pol.policy_spec
        graph.add(triple=(obs_pol.uri, RDF.type, URI_OBS_TYPE_EVALUATED_POLICY))
        for observation in spec.observations:
            add_observation_to_graph(graph, observation, obs_pol)

        te_uri = spec.time_extractor_uri
        graph.add(triple=(obs_pol.uri, URI_OBS_PRED_TIME_EXTRACTOR, te_uri))
        add_py_module_attr(graph=graph, node_uri=te_uri, py_model=spec.time_extractor)

        if spec.entity_mapper is not None:
            em_uri = spec.entity_mapper_uri
            graph.add(triple=(obs_pol.uri, URI_OBS_PRED_ENTITY_MAPPER, em_uri))
            add_py_module_attr(graph=graph, node_uri=em_uri, py_model=spec.entity_mapper)

        evaluator_type = spec.evaluator.__class__.__name__
        eval_uri = spec.evaluator_uri
        graph.add(triple=(obs_pol.uri, URI_OBS_PRED_HAS_EVALUATOR, eval_uri))
        if evaluator_type == "LinearDistanceEvaluator":
            add_linear_distance_to_graph(
                graph=graph,
                eval_uri=eval_uri,
                evaluator=spec.evaluator,
                observations=spec.observations,
            )
            return

        if evaluator_type == "PyModuleAttr":
            add_py_module_attr(graph=graph, node_uri=eval_uri, py_model=spec.evaluator)
            return

        raise ValueError(f"unhandled evaluator type: {evaluator_type}")

    raise TypeError(f"unsupported ObservationPolicy type: {type(obs_pol)}")


def add_scr_exec_to_graph(graph: Graph, scr_exec: ScenarioExecution) -> None:
    if scr_exec.scene_inst.scene.uri != scr_exec.variant.scene.uri:
        raise ValueError(
            f"ScenarioExecution '{scr_exec.uri}' binds scene instance '{scr_exec.scene_inst.uri}' "
            f"for scene '{scr_exec.scene_inst.scene.uri}', expected '{scr_exec.variant.scene.uri}'"
        )

    graph.bind(prefix=scr_exec.ns_prefix, namespace=scr_exec.namespace)
    graph.add(triple=(scr_exec.uri, RDF.type, URI_BDD_TYPE_SCENARIO_EXEC))
    graph.add(triple=(scr_exec.uri, URI_BDD_PRED_OF_VARIANT, scr_exec.variant.uri))
    graph.add(triple=(scr_exec.uri, URI_EXEC_PRED_RUNS_SCENE, scr_exec.scene_inst.uri))

    # behaviour implementation
    graph.add(triple=(scr_exec.uri, URI_BDD_PRED_HAS_BHV_IMPL, scr_exec.bhv_impl.uri))
    graph.add(
        triple=(
            scr_exec.bhv_impl.uri,
            URI_BHV_PRED_OF_BHV,
            scr_exec.variant.template.when_bhv.behaviour.uri,
        )
    )
    add_bhv_impl_to_graph(graph=graph, bhv_impl=scr_exec.bhv_impl)

    # observation policies
    for obs_pol in scr_exec.obs_policies:
        if (not scr_exec.variant.has_holds_expr_uri(obs_pol.fluent.uri)) and (
            not scr_exec.variant.template.has_holds_expr(obs_pol.fluent.uri)
        ):
            raise ValueError(
                f"{obs_pol.fluent} does not belong to {scr_exec.variant} or {scr_exec.variant.template}"
            )
        graph.add(triple=(scr_exec.uri, URI_OBS_PRED_POLICY, obs_pol.uri))
        add_obs_pol_to_graph(graph=graph, obs_pol=obs_pol)


def create_bddx_model_graph(model: Any, g: Graph | None = None) -> Graph:
    if g is None:
        g = Graph()

    for provider in model.obs_providers:
        add_obs_provider_to_graph(graph=g, provider=provider)

    scene_inst_uris = set()
    for scr_exec in model.scenario_execs:
        add_scr_exec_to_graph(graph=g, scr_exec=scr_exec)
        if scr_exec.scene_inst.uri not in scene_inst_uris:
            add_modelled_scene(
                graph=g,
                scene_inst=scr_exec.scene_inst,
                of_scene_id=scr_exec.variant.template.scene_uri,
            )
            scene_inst_uris.add(scr_exec.scene_inst.uri)

    return g
