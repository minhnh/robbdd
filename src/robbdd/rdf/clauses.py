# SPDX-License-Identifier: MPL-2.0
from typing import Any
from bdd_dsl.representation import VariableStrTemplate
from rdflib import Graph, Literal, URIRef, RDF
from bdd_dsl.models.namespace import NS_MM_BDD
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_ARG_NAMES,
    URI_BDD_PRED_ARG_VARS,
    URI_BDD_PRED_CFG_NAME,
    URI_BDD_PRED_CFG_TARGET,
    URI_BDD_PRED_CFG_VAR,
    URI_BDD_PRED_CLAUSE_OF,
    URI_BDD_PRED_HAS_CLAUSE,
    URI_BDD_PRED_IN_SET,
    URI_BDD_PRED_REF_AGN,
    URI_BDD_PRED_REF_OBJ,
    URI_BDD_PRED_REF_VAR,
    URI_BDD_PRED_REF_WS,
    URI_BDD_PRED_TMPL_STR,
    URI_BDD_TYPE_CONFIG,
    URI_BDD_TYPE_EXISTS,
    URI_BDD_TYPE_FLUENT_CLAUSE,
    URI_BDD_TYPE_FORALL,
    URI_BDD_TYPE_IS_HELD,
    URI_BDD_TYPE_LOCATED_AT,
    URI_BDD_TYPE_SORTED,
    URI_BDD_TYPE_STR_TMPL,
    URI_BDD_TYPE_VARIABLE,
    URI_BDD_TYPE_WHEN_BHV,
    URI_BHV_PRED_OF_BHV,
    URI_BHV_PRED_TARGET_AGN,
    URI_BHV_PRED_TARGET_OBJ,
    URI_BHV_PRED_TARGET_WS,
    URI_BHV_TYPE_BHV,
    URI_BHV_TYPE_PICK,
    URI_BHV_TYPE_PLACE,
    URI_TIME_PRED_AFTER_EVT,
    URI_TIME_PRED_BEFORE_EVT,
    URI_TIME_PRED_HRZN_SEC,
    URI_TIME_TYPE_AFTER_EVT,
    URI_TIME_TYPE_BEFORE_EVT,
    URI_TIME_TYPE_DURING,
    URI_TIME_TYPE_TC,
)
from rdflib.collection import Collection
from robbdd.classes.bdd import (
    AfterEvent,
    BeforeEvent,
    Clause,
    DuringEvent,
    ExistsExpr,
    FluentAndExpr,
    ForAllExpr,
    HoldsExpr,
    ScenarioSetVariable,
    TimeConstraint,
    VariableBase,
    WhenBehaviourClause,
)
from robbdd.rdf.common import add_literal_list_pred, add_node_list_pred


def add_fc_predicate(graph: Graph, clause: HoldsExpr, clause_uri: URIRef):
    pred_type_str = type(clause.predicate).__name__

    if "LocatedAtPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_LOCATED_AT))

        obj_var = getattr(clause.predicate, "object", None)
        assert (
            obj_var is not None and isinstance(obj_var, VariableBase)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        ws_var = getattr(clause.predicate, "workspace", None)
        assert (
            ws_var is not None and isinstance(ws_var, VariableBase)
        ), f"unexpected 'workspace' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {ws_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, ws_var.uri))
        return

    if "IsHeldPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_IS_HELD))

        obj_var = getattr(clause.predicate, "object", None)
        assert (
            obj_var is not None and isinstance(obj_var, VariableBase)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        agent_var = getattr(clause.predicate, "agent", None)
        assert (
            agent_var is not None and isinstance(agent_var, VariableBase)
        ), f"unexpected 'agent' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {agent_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_AGN, agent_var.uri))
        return

    if "CanReachPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["CanReach"]))

        obj_var = getattr(clause.predicate, "object", None)
        assert (
            obj_var is not None and isinstance(obj_var, VariableBase)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        agent_var = getattr(clause.predicate, "agent", None)
        assert (
            agent_var is not None and isinstance(agent_var, VariableBase)
        ), f"unexpected 'agent' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {agent_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_AGN, agent_var.uri))
        return

    if "DoesNotDropPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["DoesNotDropPredicate"]))

        agent_var = getattr(clause.predicate, "agent", None)
        assert (
            agent_var is not None and isinstance(agent_var, VariableBase)
        ), f"unexpected 'agent' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {agent_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_AGN, agent_var.uri))

        obj_var = getattr(clause.predicate, "object", None)
        assert (
            obj_var is not None and isinstance(obj_var, VariableBase)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))
        return

    if "DoesNotCollidePred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["DoesNotCollidePredicate"]))

        agent_var = getattr(clause.predicate, "agent", None)
        assert (
            agent_var is not None and isinstance(agent_var, VariableBase)
        ), f"unexpected 'agent' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {agent_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_AGN, agent_var.uri))

        target_var = getattr(clause.predicate, "target", None)
        assert (
            target_var is not None and isinstance(target_var, VariableBase)
        ), f"unexpected 'target' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {agent_var}"
        graph.add(triple=(clause_uri, NS_MM_BDD["target"], target_var.uri))
        return

    if "HasConfigPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_CONFIG))

        cfg_name = getattr(clause.predicate, "cfg_name", None)
        assert isinstance(
            cfg_name, str
        ), f"unexpected 'cfg_name' attr for '{pred_type_str}' predicate of clause '{clause_uri}': {cfg_name}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_CFG_NAME, Literal(cfg_name)))

        cfg_target = getattr(clause.predicate, "cfg_target", None)
        assert isinstance(
            cfg_target, VariableBase
        ), f"unexpected 'cfg_target' attr for '{pred_type_str}' predicate of clause '{clause_uri}': {cfg_target}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_CFG_TARGET, cfg_target.uri))

        cfg_var = getattr(clause.predicate, "cfg_var", None)
        assert isinstance(
            cfg_var, VariableBase
        ), f"unexpected 'cfg_var' attr for '{pred_type_str}' predicate of clause '{clause_uri}': {cfg_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_CFG_VAR, cfg_var.uri))
        return

    if "StrTmplPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_STR_TMPL))

        tmpl_str = getattr(clause.predicate, "tmpl_str", None)
        assert isinstance(
            tmpl_str, str
        ), f"unexpected 'tmpl_str' attr for '{pred_type_str}' predicate of clause '{clause_uri}': {tmpl_str}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_TMPL_STR, Literal(tmpl_str)))

        arg_maps = getattr(clause.predicate, "arg_maps", None)
        assert isinstance(
            arg_maps, list
        ), f"unexpected 'arg_maps' attr for '{pred_type_str}' predicate of clause '{clause_uri}': {arg_maps}"

        arg_names = []
        arg_vars = []
        var_map = {}
        for arg_m in arg_maps:
            arg_names.append(arg_m.arg_name)
            arg_var_uri = arg_m.arg_var.uri
            arg_vars.append(arg_var_uri)
            assert (
                arg_var_uri not in var_map
            ), f"clause '{clause_uri}': duplicate refs to '{arg_var_uri}'"
            var_map[arg_var_uri] = arg_m.arg_name

        # Create string template obj to test valid argument mappings
        _ = VariableStrTemplate(tmpl_str=tmpl_str, var_map=var_map)
        add_literal_list_pred(
            graph=graph, subject_uri=clause_uri, pred_uri=URI_BDD_PRED_ARG_NAMES, values=arg_names
        )
        add_node_list_pred(
            graph=graph, subject_uri=clause_uri, pred_uri=URI_BDD_PRED_ARG_VARS, nodes=arg_vars
        )

        return

    if "IsSortedPred" in pred_type_str:
        graph.add(triple=(clause_uri, RDF.type, URI_BDD_TYPE_SORTED))

        obj_var = getattr(clause.predicate, "objects", None)
        assert (
            obj_var is not None and isinstance(obj_var, ScenarioSetVariable)
        ), f"unexpected 'object' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {obj_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_OBJ, obj_var.uri))

        ws_var = getattr(clause.predicate, "workspaces", None)
        assert (
            ws_var is not None and isinstance(ws_var, ScenarioSetVariable)
        ), f"unexpected 'workspaces' variable for '{pred_type_str}' predicate of clause '{clause_uri}': {ws_var}"
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, ws_var.uri))
        return

    raise ValueError(f"unhandled predicate type: {pred_type_str}")


def add_node_time_constraint(graph: Graph, tc: TimeConstraint, node_uri: URIRef):
    graph.add(triple=(node_uri, RDF.type, URI_TIME_TYPE_TC))

    if isinstance(tc, BeforeEvent):
        graph.add(triple=(node_uri, RDF.type, URI_TIME_TYPE_BEFORE_EVT))
        graph.add(triple=(node_uri, URI_TIME_PRED_BEFORE_EVT, tc.event.uri))
        if tc.horizon is not None:
            graph.add(triple=(node_uri, URI_TIME_PRED_HRZN_SEC, Literal(tc.horizon.val)))
        return

    if isinstance(tc, AfterEvent):
        graph.add(triple=(node_uri, RDF.type, URI_TIME_TYPE_AFTER_EVT))
        graph.add(triple=(node_uri, URI_TIME_PRED_AFTER_EVT, tc.event.uri))
        if tc.horizon is not None:
            graph.add(triple=(node_uri, URI_TIME_PRED_HRZN_SEC, Literal(tc.horizon.val)))
        return

    if isinstance(tc, DuringEvent):
        graph.add(triple=(node_uri, RDF.type, URI_TIME_TYPE_DURING))
        graph.add(triple=(node_uri, URI_TIME_PRED_AFTER_EVT, tc.start_event.uri))
        graph.add(triple=(node_uri, URI_TIME_PRED_BEFORE_EVT, tc.end_event.uri))
        return

    raise ValueError(f"unhandled time constraint type: {type(tc)}")


def add_clause_expr(
    graph: Graph,
    clause: Clause,
    clause_of_uri: URIRef,
    clause_col: Collection,
):
    if isinstance(clause, HoldsExpr):
        fc_uri = clause.uri

        graph.add((fc_uri, RDF.type, URI_BDD_TYPE_FLUENT_CLAUSE))
        graph.add((fc_uri, URI_BDD_PRED_CLAUSE_OF, clause_of_uri))

        add_fc_predicate(graph=graph, clause=clause, clause_uri=fc_uri)
        add_node_time_constraint(graph=graph, tc=clause.tc, node_uri=fc_uri)

        clause_col.append(fc_uri)

    elif isinstance(clause, FluentAndExpr):
        for fc in clause.expressions:
            add_clause_expr(
                graph=graph,
                clause=fc,
                clause_of_uri=clause_of_uri,
                clause_col=clause_col,
            )

    elif isinstance(clause, ExistsExpr):
        graph.add(triple=(clause.uri, RDF.type, URI_BDD_TYPE_EXISTS))
        graph.add(triple=(clause.var.uri, RDF.type, URI_BDD_TYPE_VARIABLE))
        graph.add(triple=(clause.uri, URI_BDD_PRED_REF_VAR, clause.var.uri))
        graph.add(triple=(clause.uri, URI_BDD_PRED_IN_SET, clause.in_set.uri))
        graph.add(triple=(clause.uri, URI_BDD_PRED_CLAUSE_OF, clause_of_uri))
        exists_clause_col = add_node_list_pred(
            graph=graph, subject_uri=clause.uri, pred_uri=URI_BDD_PRED_HAS_CLAUSE, nodes=[]
        )
        add_clause_expr(
            graph=graph,
            clause=clause.fl_expr,
            clause_of_uri=clause_of_uri,
            clause_col=exists_clause_col,
        )
        clause_col.append(clause.uri)

    else:
        raise ValueError(f"clause expression of type '{type(clause)}' is not handled: {clause}")


def add_when_behaviour(graph: Graph, wbh_clause: WhenBehaviourClause, when_uri: URIRef) -> URIRef:
    graph.add(triple=(wbh_clause.behaviour.uri, RDF.type, URI_BHV_TYPE_BHV))
    graph.add(triple=(wbh_clause.uri, RDF.type, URI_BDD_TYPE_WHEN_BHV))
    graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_OF_BHV, wbh_clause.behaviour.uri))
    graph.add(triple=(wbh_clause.uri, URI_BDD_PRED_CLAUSE_OF, when_uri))

    add_node_time_constraint(graph=graph, tc=wbh_clause.duration, node_uri=wbh_clause.uri)

    param_bhv_cls_str = wbh_clause.param_bhv.__class__.__name__
    if "PickPlaceBehaviour" in param_bhv_cls_str:
        graph.add(triple=(wbh_clause.behaviour.uri, RDF.type, URI_BHV_TYPE_PICK))
        graph.add(triple=(wbh_clause.behaviour.uri, RDF.type, URI_BHV_TYPE_PLACE))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_AGN, wbh_clause.param_bhv.agent.uri))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_OBJ, wbh_clause.param_bhv.object.uri))
        graph.add(
            triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_WS, wbh_clause.param_bhv.workspace.uri)
        )
    elif "PickBehaviour" in param_bhv_cls_str:
        graph.add(triple=(wbh_clause.behaviour.uri, RDF.type, URI_BHV_TYPE_PICK))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_AGN, wbh_clause.param_bhv.agent.uri))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_OBJ, wbh_clause.param_bhv.object.uri))
    elif "PlaceBehaviour" in param_bhv_cls_str:
        graph.add(triple=(wbh_clause.behaviour.uri, RDF.type, URI_BHV_TYPE_PLACE))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_AGN, wbh_clause.param_bhv.agent.uri))
        graph.add(triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_OBJ, wbh_clause.param_bhv.object.uri))
        graph.add(
            triple=(wbh_clause.uri, URI_BHV_PRED_TARGET_WS, wbh_clause.param_bhv.workspace.uri)
        )
    else:
        raise ValueError(
            f"WhenBehaviourClause '{wbh_clause.uri}' has unhandled ParameterizedBehaviour type: {param_bhv_cls_str}"
        )

    return wbh_clause.behaviour.uri


def add_gwt_expr(
    graph: Graph,
    gwt_expr: Any,
    parent_uri: URIRef,
    given_uri: URIRef,
    when_uri: URIRef,
    then_uri: URIRef,
) -> URIRef:
    clause_col = add_node_list_pred(
        graph=graph, subject_uri=parent_uri, pred_uri=URI_BDD_PRED_HAS_CLAUSE, nodes=[]
    )

    if gwt_expr.given_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=gwt_expr.given_expr.given,
            clause_of_uri=given_uri,
            clause_col=clause_col,
        )

    bhv_uri = None
    if gwt_expr.forall_expr is not None:
        assert isinstance(gwt_expr.forall_expr, ForAllExpr)
        graph.add(triple=(gwt_expr.forall_expr.uri, RDF.type, URI_BDD_TYPE_FORALL))
        graph.add(triple=(gwt_expr.forall_expr.var.uri, RDF.type, URI_BDD_TYPE_VARIABLE))
        graph.add(
            triple=(gwt_expr.forall_expr.uri, URI_BDD_PRED_REF_VAR, gwt_expr.forall_expr.var.uri)
        )
        graph.add(
            triple=(gwt_expr.forall_expr.uri, URI_BDD_PRED_IN_SET, gwt_expr.forall_expr.in_set.uri)
        )
        graph.add(triple=(gwt_expr.forall_expr.uri, URI_BDD_PRED_CLAUSE_OF, when_uri))
        clause_col.append(gwt_expr.forall_expr.uri)
        bhv_uri = add_gwt_expr(
            graph=graph,
            gwt_expr=gwt_expr.forall_expr.gwt_expr,
            parent_uri=gwt_expr.forall_expr.uri,
            given_uri=given_uri,
            when_uri=when_uri,
            then_uri=then_uri,
        )
    elif gwt_expr.when_expr is not None:
        for when_evt in gwt_expr.when_expr.when_events:
            print(when_evt)
        bhv_uri = add_when_behaviour(
            graph=graph, wbh_clause=gwt_expr.when_expr.when_bhv, when_uri=when_uri
        )
        clause_col.append(gwt_expr.when_expr.when_bhv.uri)
    else:
        raise ValueError(
            f"Given-When-Then expression must either have a ForAll or WhenBehaviour expressions, parent: {parent_uri.n3()}"
        )

    if gwt_expr.then_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=gwt_expr.then_expr.then,
            clause_of_uri=then_uri,
            clause_col=clause_col,
        )

    assert bhv_uri is not None, f"no behaviour found in GivenWhenThenExpr for '{parent_uri}'"
    return bhv_uri
