# SPDX-License-Identifier: MPL-2.0
from typing import Any
from bdd_dsl.models.namespace import NS_MM_BDD
from rdf_utils.namespace import NS_MM_TIME
from rdflib import BNode, Graph, RDF, IdentifiedNode, Literal, Node, URIRef
from rdflib.collection import Collection
from bdd_dsl.models.urirefs import (
    URI_AGN_PRED_HAS_AGN,
    URI_AGN_TYPE_AGN,
    URI_BDD_PRED_CLAUSE_OF,
    URI_BDD_PRED_ELEMS,
    URI_BDD_PRED_HAS_AC,
    URI_BDD_PRED_HAS_CLAUSE,
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_HAS_VARIATION,
    URI_BDD_PRED_HOLDS_AT,
    URI_BDD_PRED_IN_SET,
    URI_BDD_PRED_OF_SCENARIO,
    URI_BDD_PRED_OF_SCENE,
    URI_BDD_PRED_OF_TMPL,
    URI_BDD_PRED_REF_OBJ,
    URI_BDD_PRED_REF_VAR,
    URI_BDD_PRED_REF_WS,
    URI_BDD_PRED_ROWS,
    URI_BDD_PRED_VAR_LIST,
    URI_BDD_TYPE_CONST_SET,
    URI_BDD_TYPE_EXISTS,
    URI_BDD_TYPE_FLUENT_CLAUSE,
    URI_BDD_TYPE_FORALL,
    URI_BDD_TYPE_IS_HELD,
    URI_BDD_TYPE_LOCATED_AT,
    URI_BDD_TYPE_SCENARIO,
    URI_BDD_PRED_GIVEN,
    URI_BDD_PRED_WHEN,
    URI_BDD_PRED_THEN,
    URI_BDD_TYPE_GIVEN,
    URI_BDD_TYPE_VARIABLE,
    URI_BDD_TYPE_SCENARIO_VARIANT,
    URI_BDD_TYPE_SCENE_AGN,
    URI_BDD_TYPE_SCENE_OBJ,
    URI_BDD_TYPE_SCENE_WS,
    URI_BDD_TYPE_SET,
    URI_BDD_TYPE_SORTED,
    URI_BDD_TYPE_TABLE_VAR,
    URI_BDD_TYPE_TASK_VAR,
    URI_BDD_TYPE_WHEN,
    URI_BDD_TYPE_THEN,
    URI_BDD_TYPE_SCENARIO_TMPL,
    URI_BDD_TYPE_SCENE,
    URI_BDD_TYPE_US,
    URI_BDD_TYPE_WHEN_BHV,
    URI_BHV_PRED_OF_BHV,
    URI_BHV_PRED_TARGET_AGN,
    URI_BHV_PRED_TARGET_OBJ,
    URI_BHV_PRED_TARGET_WS,
    URI_BHV_TYPE_BHV,
    URI_BHV_TYPE_PICK,
    URI_BHV_TYPE_PLACE,
    URI_ENV_PRED_HAS_OBJ,
    URI_ENV_PRED_HAS_WS,
    URI_ENV_TYPE_OBJ,
    URI_ENV_TYPE_WS,
    URI_TASK_PRED_OF_TASK,
    URI_TASK_TYPE_TASK,
    URI_TIME_TYPE_TC,
    URI_TIME_PRED_AFTER_EVT,
    URI_TIME_PRED_BEFORE_EVT,
    URI_TIME_TYPE_AFTER_EVT,
    URI_TIME_TYPE_BEFORE_EVT,
    URI_TIME_TYPE_DURING,
)
from bdd_textx.classes.bdd import (
    AfterEvent,
    BeforeEvent,
    Clause,
    ConstantSet,
    DuringEvent,
    ExistsExpr,
    FluentAndExpr,
    ForAllExpr,
    HoldsExpr,
    ScenarioSetVariable,
    ScenarioTemplate,
    ScenarioVariant,
    TableVariation,
    TaskVariation,
    TimeConstraint,
    UserStory,
    VariableBase,
    WhenBehaviourClause,
)
from bdd_textx.classes.scene import SceneModel


def add_node_list_pred(
    graph: Graph, subject_uri: URIRef, pred_uri: URIRef, nodes: list[Node]
) -> Collection:
    b = BNode()
    c = Collection(graph=graph, uri=b, seq=nodes)
    graph.add((subject_uri, pred_uri, b))
    return c


def add_literal_list_pred(
    graph: Graph, subject_uri: URIRef, pred_uri: URIRef, values: list[Any]
) -> Collection:
    literals = []
    for val in values:
        literals.append(Literal(val))
    return add_node_list_pred(
        graph=graph, subject_uri=subject_uri, pred_uri=pred_uri, nodes=literals
    )


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
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, agent_var.uri))
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
        graph.add(triple=(clause_uri, URI_BDD_PRED_REF_WS, agent_var.uri))
        return

    if "HasConfigPred" in pred_type_str:
        # TODO(minhnh): handle vars
        graph.add(triple=(clause_uri, RDF.type, NS_MM_BDD["HasConfigPredicate"]))
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


def add_fc_time_constraint(graph: Graph, tc: TimeConstraint, clause_uri: URIRef):
    graph.add(triple=(tc.uri, RDF.type, URI_TIME_TYPE_TC))
    graph.add(triple=(clause_uri, URI_BDD_PRED_HOLDS_AT, tc.uri))

    if isinstance(tc, BeforeEvent):
        graph.add(triple=(tc.uri, RDF.type, URI_TIME_TYPE_BEFORE_EVT))
        graph.add(triple=(tc.uri, URI_TIME_PRED_BEFORE_EVT, tc.event.uri))
        return

    if isinstance(tc, AfterEvent):
        graph.add(triple=(tc.uri, RDF.type, URI_TIME_TYPE_AFTER_EVT))
        graph.add(triple=(tc.uri, URI_TIME_PRED_AFTER_EVT, tc.event.uri))
        return

    if isinstance(tc, DuringEvent):
        graph.add(triple=(tc.uri, RDF.type, URI_TIME_TYPE_DURING))
        graph.add(triple=(tc.uri, URI_TIME_PRED_AFTER_EVT, tc.start_event.uri))
        graph.add(triple=(tc.uri, URI_TIME_PRED_BEFORE_EVT, tc.end_event.uri))
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
        add_fc_time_constraint(graph=graph, tc=clause.tc, clause_uri=fc_uri)

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


def add_scenario_tmpl(graph: Graph, tmpl: ScenarioTemplate):
    graph.bind(prefix=tmpl.ns.name, namespace=tmpl.namespace)
    graph.add(triple=(tmpl.uri, RDF.type, URI_BDD_TYPE_SCENARIO_TMPL))

    # scenario
    graph.add(triple=(tmpl.scenario_uri, RDF.type, URI_BDD_TYPE_SCENARIO))
    graph.add(triple=(tmpl.given_uri, RDF.type, URI_BDD_TYPE_GIVEN))
    graph.add(triple=(tmpl.when_uri, RDF.type, URI_BDD_TYPE_WHEN))
    graph.add(triple=(tmpl.then_uri, RDF.type, URI_BDD_TYPE_THEN))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_GIVEN, tmpl.given_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_WHEN, tmpl.when_uri))
    graph.add(triple=(tmpl.scenario_uri, URI_BDD_PRED_THEN, tmpl.then_uri))
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_OF_SCENARIO, tmpl.scenario_uri))

    # task, if process more complex task models should make sure that
    # this task is not already handled, like with templates
    graph.add(triple=(tmpl.task.uri, RDF.type, URI_TASK_TYPE_TASK))
    graph.add(triple=(tmpl.scenario_uri, URI_TASK_PRED_OF_TASK, tmpl.task.uri))

    # scene
    graph.add(triple=(tmpl.scene_uri, RDF.type, URI_BDD_TYPE_SCENE))
    graph.add(triple=(tmpl.uri, URI_BDD_PRED_HAS_SCENE, tmpl.scene_uri))

    # variables
    for var in tmpl.variables:
        graph.add(triple=(var.uri, RDF.type, URI_BDD_TYPE_VARIABLE))
        if isinstance(var, ScenarioSetVariable):
            graph.add(triple=(var.uri, RDF.type, URI_BDD_TYPE_SET))

    # clauses
    bhv_uri = add_gwt_expr(
        graph=graph,
        gwt_expr=tmpl.gwt_expr,
        parent_uri=tmpl.uri,
        given_uri=tmpl.given_uri,
        when_uri=tmpl.when_uri,
        then_uri=tmpl.then_uri,
    )
    graph.add(triple=(tmpl.scenario_uri, URI_BHV_PRED_OF_BHV, bhv_uri))


def get_var_value_node(var_val: Any) -> Node:
    if hasattr(var_val, "linked_val") and var_val.linked_val is not None:
        assert hasattr(
            var_val.linked_val, "uri"
        ), f"Linked value has no URI attr: {var_val.linked_val}"
        assert var_val.linked_val.uri is not None
        return var_val.linked_val.uri

    if hasattr(var_val, "literal_val") and var_val.literal_val is not None:
        return Literal(var_val.literal_val)

    raise ValueError(f"ValidVarValue object has unhandled attributes: {var_val}")


def get_const_set(graph: Graph, const_set_link: Any, value_sets: set[URIRef]) -> IdentifiedNode:
    assert hasattr(const_set_link, "linked_set") and isinstance(
        const_set_link.linked_set, ConstantSet
    ), f"ConstSetLink obj has no valid 'linked_set' attr: '{const_set_link}'"

    if const_set_link.linked_set.uri in value_sets:
        return const_set_link.linked_set.uri

    graph.add(triple=(const_set_link.linked_set.uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(const_set_link.linked_set.uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    for v in const_set_link.linked_set.elems:
        graph.add(
            triple=(
                const_set_link.linked_set.uri,
                URI_BDD_PRED_ELEMS,
                get_var_value_node(var_val=v),
            )
        )
    value_sets.add(const_set_link.linked_set.uri)
    return const_set_link.linked_set.uri


def get_set_expr_set(graph: Graph, set_expr: Any, value_sets: set[URIRef]) -> IdentifiedNode:
    assert (
        hasattr(set_expr, "elems") and set_expr.elems is not None
    ), f"SetExpr object has invalid 'elems' attr: {set_expr}"
    col_first = BNode()
    col = Collection(graph=graph, uri=col_first, seq=[])
    for elem in set_expr.elems:
        col.append(get_var_value_node(var_val=elem))
    return col_first


def add_task_variation(graph: Graph, variation: TaskVariation, value_sets: set[URIRef]):
    graph.add(triple=(variation.uri, RDF.type, URI_BDD_TYPE_TASK_VAR))
    graph.add(triple=(variation.uri, URI_TASK_PRED_OF_TASK, variation.parent.template.task.uri))

    var_list_col = add_node_list_pred(
        graph=graph, subject_uri=variation.uri, pred_uri=URI_BDD_PRED_VAR_LIST, nodes=[]
    )
    if isinstance(variation, TableVariation):
        graph.add(triple=(variation.uri, RDF.type, URI_BDD_TYPE_TABLE_VAR))
        for var in variation.header.variables:
            assert isinstance(var, VariableBase)
            var_list_col.append(var.uri)

        rows_col = add_node_list_pred(
            graph=graph, subject_uri=variation.uri, pred_uri=URI_BDD_PRED_ROWS, nodes=[]
        )
        for r in variation.rows:
            r_first = BNode()
            r_col = Collection(graph=graph, uri=r_first, seq=[])
            for v in r.values:
                if "ValidVarValue" in v.__class__.__name__:
                    r_col.append(get_var_value_node(var_val=v))
                elif "ConstSetLink" in v.__class__.__name__:
                    r_col.append(
                        get_const_set(graph=graph, const_set_link=v, value_sets=value_sets)
                    )
                elif "SetExpr" in v.__class__.__name__:
                    r_col.append(get_set_expr_set(graph=graph, set_expr=v, value_sets=value_sets))
                else:
                    raise ValueError(
                        f"unhandled value type '{v.__class__.__name__}' in table variation for '{variation.uri}'"
                    )

            assert len(r_col) == len(
                var_list_col
            ), f"number of row values ({len(r_col)}) != number of variables ({len(var_list_col)})"
            rows_col.append(r_first)
    else:
        raise ValueError(
            f"TaskVariaiton type not handled for variant '{variation.parent.uri}': {type(variation)}"
        )


def add_scene_model(graph: Graph, scene: SceneModel):
    graph.bind(prefix=scene.ns.name, namespace=scene.namespace)

    graph.add(triple=(scene.scene_obj_uri, RDF.type, URI_BDD_TYPE_SCENE_OBJ))
    graph.add(triple=(scene.scene_obj_uri, RDF.type, URI_BDD_TYPE_SET))
    for obj in scene.objects:
        graph.bind(prefix=obj.ns.name, namespace=obj.namespace)
        graph.add(triple=(obj.uri, RDF.type, URI_ENV_TYPE_OBJ))
        graph.add(triple=(scene.scene_obj_uri, URI_ENV_PRED_HAS_OBJ, obj.uri))

    graph.add(triple=(scene.scene_ws_uri, RDF.type, URI_BDD_TYPE_SCENE_WS))
    graph.add(triple=(scene.scene_ws_uri, RDF.type, URI_BDD_TYPE_SET))
    for ws in scene.workspaces:
        graph.bind(prefix=ws.ns.name, namespace=ws.namespace)
        graph.add(triple=(ws.uri, RDF.type, URI_ENV_TYPE_WS))
        graph.add(triple=(scene.scene_ws_uri, URI_ENV_PRED_HAS_WS, ws.uri))

    graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SCENE_AGN))
    graph.add(triple=(scene.scene_agn_uri, RDF.type, URI_BDD_TYPE_SET))
    for agn in scene.agents:
        graph.bind(prefix=agn.ns.name, namespace=agn.namespace)
        graph.add(triple=(agn.uri, RDF.type, URI_AGN_TYPE_AGN))
        graph.add(triple=(scene.scene_agn_uri, URI_AGN_PRED_HAS_AGN, agn.uri))


def add_scenario_variant(
    graph: Graph,
    variant: ScenarioVariant,
    templates: set[URIRef],
    scenes: set[URIRef],
    value_sets: set[URIRef],
):
    graph.add(triple=(variant.uri, RDF.type, URI_BDD_TYPE_SCENARIO_VARIANT))

    # template
    if variant.template.uri not in templates:
        add_scenario_tmpl(graph=graph, tmpl=variant.template)
        templates.add(variant.template.uri)

    graph.add(triple=(variant.uri, URI_BDD_PRED_OF_TMPL, variant.template.uri))

    # scene
    if variant.scene.uri not in scenes:
        add_scene_model(graph=graph, scene=variant.scene)
        scenes.add(variant.scene.uri)

    graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_obj_uri))
    graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_ws_uri))
    graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_agn_uri))

    graph.add(
        triple=(variant.scene.scene_obj_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
    )
    graph.add(
        triple=(variant.scene.scene_ws_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
    )
    graph.add(
        triple=(variant.scene.scene_agn_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
    )

    # variation
    add_task_variation(graph=graph, variation=variant.variation, value_sets=value_sets)
    graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_VARIATION, variant.variation.uri))


def add_us_to_graph(
    graph: Graph,
    us: UserStory,
    templates: set[URIRef],
    scenes: set[URIRef],
    value_sets: set[URIRef],
):
    graph.bind(us.ns.name, us.ns.uri, override=True)
    graph.add(triple=(us.uri, RDF.type, URI_BDD_TYPE_US))
    for scr_var in us.scenarios:
        add_scenario_variant(
            graph=graph, variant=scr_var, templates=templates, scenes=scenes, value_sets=value_sets
        )
        graph.add((us.uri, URI_BDD_PRED_HAS_AC, scr_var.uri))


def create_bdd_model_graph(model: Any) -> Graph:
    g = Graph()
    events = getattr(model, "events", None)
    assert events is not None and isinstance(events, list), "no list of events in model"
    for evt in events:
        g.bind(prefix=evt.ns.name, namespace=evt.namespace)
        g.add(triple=(evt.uri, RDF.type, NS_MM_TIME["Event"]))

    tasks = getattr(model, "tasks", None)
    assert tasks is not None and isinstance(tasks, list), "no list of tasks in model"
    for task in tasks:
        g.bind(prefix=task.ns.name, namespace=task.namespace)
        g.add(triple=(task.uri, RDF.type, URI_TASK_TYPE_TASK))

    stories = getattr(model, "stories", None)
    assert stories is not None and isinstance(stories, list), "no list of user stories in model"
    templates = set()
    scenes = set()
    value_sets = set()
    for us in stories:
        add_us_to_graph(graph=g, us=us, templates=templates, scenes=scenes, value_sets=value_sets)

    return g
