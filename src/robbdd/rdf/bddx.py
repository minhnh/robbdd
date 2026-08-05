# SPDX-License-Identifier: MPL-2.0
from typing import Any

from bdd_dsl.models.namespace import NS_MM_CSTR, NS_MM_CSTR_EXT
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_HAS_BHV_IMPL,
    URI_BDD_PRED_OF_CLAUSE,
    URI_BDD_PRED_OF_VARIANT,
    URI_BDD_TYPE_BHV_IMPL,
    URI_BDD_TYPE_SCENARIO_EXEC,
    URI_BHV_PRED_OF_BHV,
    URI_OBS_PRED_HAS_OBSERVATION,
    URI_OBS_PRED_OBSERVES_TARGET,
    URI_OBS_PRED_POLICY,
    URI_OBS_PRED_PROVIDER,
    URI_OBS_TYPE_OBSERVATION,
    URI_OBS_TYPE_POLICY,
    URI_OBS_TYPE_POSE_PROVIDER,
    URI_OBS_TYPE_PROVIDER,
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
from rdf_utils.namespace import NS_MM_GEOM_COORD, NS_MM_GEOM_REL, NS_MM_QUDT_QTY, NS_MM_QUDT_UNIT
from rdflib import RDF, XSD, BNode, Graph, Literal
from scene_dsl.rdf.common import add_py_module_attr
from scene_dsl.rdf.geom import LENGTH_UNITS
from scene_dsl.rdf.scenex import add_modelled_scene
from scene_dsl.rdf.sensors import URI_SENS_PRED_UPDATE_RATE, URI_SOSA_TYPE_SENSOR

from robbdd.classes.bddx import (
    BehaviourImplementation,
    Observation,
    ObservationPolicy,
    ObservationProvider,
    ScenarioExecution,
)


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
        graph.add((provider.uri, RDF.type, URI_SOSA_TYPE_SENSOR))
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


def add_distance_value(graph: Graph, value) -> BNode:
    quantity = BNode()
    graph.add((quantity, RDF.type, NS_MM_QUDT_QTY.Distance))
    graph.add((quantity, URI_QUDT_PRED_VALUE, Literal(value.value, datatype=XSD.double)))
    graph.add((quantity, URI_QUDT_PRED_UNIT, LENGTH_UNITS[value.unit]))
    return quantity


def add_linear_distance_to_graph(graph: Graph, policy: ObservationPolicy) -> None:
    spec = policy.policy_spec
    relation = BNode()
    coordinate = BNode()
    constraint = BNode()
    graph.add((relation, RDF.type, NS_MM_GEOM_REL.LinearDistance))
    graph.add((relation, NS_MM_GEOM_REL["between-entities"], spec.left.uri))
    graph.add((relation, NS_MM_GEOM_REL["between-entities"], spec.right.uri))
    graph.add((coordinate, RDF.type, NS_MM_GEOM_COORD.LinearDistanceCoordinate))
    graph.add((coordinate, RDF.type, NS_MM_GEOM_COORD.DistanceReference))
    graph.add((coordinate, URI_QUDT_PRED_QUANTITY_KIND, NS_MM_QUDT_QTY.Distance))
    graph.add((coordinate, NS_MM_GEOM_COORD.of, relation))
    graph.add((policy.uri, NS_MM_CSTR_EXT["has-constraint"], constraint))
    graph.add((constraint, RDF.type, NS_MM_CSTR.LinearDistanceConstraint))
    graph.add((constraint, NS_MM_CSTR.quantity, coordinate))

    distance = spec.constraint
    if distance.less_than is not None:
        graph.add((constraint, RDF.type, NS_MM_CSTR.LessThanConstraint))
        graph.add((constraint, NS_MM_CSTR.threshold, add_distance_value(graph, distance.less_than)))
    elif distance.greater_than is not None:
        graph.add((constraint, RDF.type, NS_MM_CSTR.GreaterThanConstraint))
        graph.add(
            (constraint, NS_MM_CSTR.threshold, add_distance_value(graph, distance.greater_than))
        )
    elif distance.lower is not None:
        graph.add((constraint, RDF.type, NS_MM_CSTR.BilateralConstraint))
        graph.add(
            (constraint, NS_MM_CSTR["lower-threshold"], add_distance_value(graph, distance.lower))
        )
        graph.add(
            (constraint, NS_MM_CSTR["upper-threshold"], add_distance_value(graph, distance.upper))
        )
    else:
        graph.add((constraint, RDF.type, NS_MM_CSTR.EqualityConstraint))
        graph.add(
            (constraint, NS_MM_CSTR["reference-value"], add_distance_value(graph, distance.equals))
        )
        graph.add(
            (constraint, NS_MM_CSTR_EXT.tolerance, add_distance_value(graph, distance.tolerance))
        )


def add_obs_pol_to_graph(graph: Graph, obs_pol: ObservationPolicy) -> None:
    graph.bind(prefix=obs_pol.ns_prefix, namespace=obs_pol.namespace)
    graph.add(triple=(obs_pol.uri, RDF.type, URI_OBS_TYPE_POLICY))
    graph.add(triple=(obs_pol.uri, URI_BDD_PRED_OF_CLAUSE, obs_pol.fluent.uri))
    if "RosTrinaryTopic" in obs_pol.policy_spec.__class__.__name__:
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

    for observation in obs_pol.observations:
        add_observation_to_graph(graph, observation, obs_pol)
    if "LinearDistanceObservation" in obs_pol.policy_spec.__class__.__name__:
        add_linear_distance_to_graph(graph, obs_pol)
        return
    if "PyModuleAttr" in obs_pol.policy_spec.__class__.__name__:
        add_py_module_attr(graph=graph, node_uri=obs_pol.uri, py_model=obs_pol.policy_spec)
        return
    raise ValueError(f"unhandled PolicySpec type: {obs_pol.policy_spec.__class__.__name__}")


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
