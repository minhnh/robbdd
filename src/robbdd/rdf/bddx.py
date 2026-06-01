# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdflib import Graph, RDF, Literal
from rdf_utils.models.python import (
    URI_PY_TYPE_MODULE_ATTR,
    URI_PY_PRED_MODULE_NAME,
    URI_PY_PRED_ATTR_NAME,
)
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_HAS_BHV_IMPL,
    URI_BDD_PRED_OF_CLAUSE,
    URI_BDD_PRED_OF_VARIANT,
    URI_BDD_TYPE_BHV_IMPL,
    URI_BDD_TYPE_SCENARIO_EXEC,
    URI_BHV_PRED_OF_BHV,
    URI_OBS_PRED_POLICY,
    URI_OBS_TYPE_POLICY,
    URI_ROS_PRED_CHNL_NAME,
    URI_ROS_PRED_TYPE_NAME,
    URI_ROS_TYPE_ACTION,
    URI_ROS_TYPE_TOPIC,
)
from robbdd.classes.bddx import BehaviourImplementation, ObservationPolicy, ScenarioExecution
from robbdd.classes.common import parse_py_module_attr


def add_bhv_impl_to_graph(graph: Graph, bhv_impl: BehaviourImplementation) -> None:
    graph.add(triple=(bhv_impl.uri, RDF.type, URI_BDD_TYPE_BHV_IMPL))

    bhv_spec_type = bhv_impl.bhv_spec.__class__.__name__
    if "RosBhvAction" in bhv_spec_type:
        graph.add(triple=(bhv_impl.uri, RDF.type, URI_ROS_TYPE_ACTION))
        action_name = bhv_impl.bhv_spec.action_name
        graph.add(
            triple=(bhv_impl.uri, URI_ROS_PRED_TYPE_NAME, Literal("bdd_ros2_interfaces/Behaviour"))
        )
        graph.add(triple=(bhv_impl.uri, URI_ROS_PRED_CHNL_NAME, Literal(action_name)))
    elif "PyModuleAttr" in bhv_spec_type:
        module_name, attr_name = parse_py_module_attr(bhv_impl.bhv_spec)
        graph.add(triple=(bhv_impl.uri, RDF.type, URI_PY_TYPE_MODULE_ATTR))
        graph.add(triple=(bhv_impl.uri, URI_PY_PRED_MODULE_NAME, Literal(module_name)))
        graph.add(triple=(bhv_impl.uri, URI_PY_PRED_ATTR_NAME, Literal(attr_name)))
    else:
        raise ValueError(f"unhandled BhvImplSpec type: {bhv_impl.bhv_spec.__class__}")


def add_obs_pol_to_graph(graph: Graph, obs_pol: ObservationPolicy) -> None:
    graph.add(triple=(obs_pol.uri, RDF.type, URI_OBS_TYPE_POLICY))
    graph.add(triple=(obs_pol.uri, URI_BDD_PRED_OF_CLAUSE, obs_pol.fluent.uri))
    if "RosTrinaryTopic" in obs_pol.obs_spec.__class__.__name__:
        graph.add(triple=(obs_pol.uri, RDF.type, URI_ROS_TYPE_TOPIC))
        topic_name = obs_pol.obs_spec.topic_name
        graph.add(
            triple=(
                obs_pol.uri,
                URI_ROS_PRED_TYPE_NAME,
                Literal("bdd_ros2_interfaces/TrinaryStamped"),
            )
        )
        graph.add(triple=(obs_pol.uri, URI_ROS_PRED_CHNL_NAME, Literal(topic_name)))
    else:
        raise ValueError(f"unhandled BhvImplSpec type: {obs_pol.obs_spec.__class__.__name__}")


def add_scr_exec_to_graph(graph: Graph, scr_exec: ScenarioExecution) -> None:
    graph.add(triple=(scr_exec.uri, RDF.type, URI_BDD_TYPE_SCENARIO_EXEC))
    graph.add(triple=(scr_exec.uri, URI_BDD_PRED_OF_VARIANT, scr_exec.variant.uri))

    # behaviour implementaiton
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


def create_bddx_model_graph(model: Any, g: Optional[Graph] = None) -> Graph:
    if g is None:
        g = Graph()

    for scr_exec in model.scenario_execs:
        add_scr_exec_to_graph(graph=g, scr_exec=scr_exec)

    return g
