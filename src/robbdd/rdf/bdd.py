# SPDX-License-Identifier: MPL-2.0
from typing import Any, Optional
from rdf_utils.namespace import NS_MM_TIME
from rdflib import RDF, XSD, BNode, Graph, IdentifiedNode, Literal, Node, URIRef
from rdflib.collection import Collection
from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_ELEMS,
    URI_BDD_PRED_GIVEN,
    URI_BDD_PRED_HAS_AC,
    URI_BDD_PRED_HAS_CLAUSE,
    URI_BDD_PRED_HAS_SCENE,
    URI_BDD_PRED_HAS_VARIATION,
    URI_BDD_PRED_OF_SCENARIO,
    URI_BDD_PRED_OF_SCENE,
    URI_BDD_PRED_OF_SETS,
    URI_BDD_PRED_OF_TMPL,
    URI_BDD_PRED_ROWS,
    URI_BDD_PRED_THEN,
    URI_BDD_PRED_VAR_LIST,
    URI_BDD_PRED_WHEN,
    URI_BDD_TYPE_CART_PRODUCT,
    URI_BDD_TYPE_CONST_SET,
    URI_BDD_TYPE_GIVEN,
    URI_BDD_TYPE_SCENARIO,
    URI_BDD_TYPE_SCENARIO_TMPL,
    URI_BDD_TYPE_SCENARIO_VARIANT,
    URI_BDD_TYPE_SCENE,
    URI_BDD_TYPE_SET,
    URI_BDD_TYPE_TABLE_VAR,
    URI_BDD_TYPE_TASK_VAR,
    URI_BDD_TYPE_THEN,
    URI_BDD_TYPE_US,
    URI_BDD_TYPE_VARIABLE,
    URI_BDD_TYPE_WHEN,
    URI_BHV_PRED_OF_BHV,
    URI_TASK_PRED_OF_TASK,
    URI_TASK_TYPE_TASK,
)
from bdd_dsl.models.variation import (
    URI_BDD_PRED_FROM,
    URI_BDD_PRED_LENGTH,
    URI_BDD_PRED_REP_ALLOWED,
    URI_BDD_TYPE_COMBINATION,
    URI_BDD_TYPE_PERMUTATION,
)
from robbdd.classes.bdd import (
    CartesianProductVariation,
    Combination,
    ExplicitSet,
    Permutation,
    ScenarioSetVariable,
    ScenarioTemplate,
    ScenarioVariable,
    ScenarioVariant,
    TableVariation,
    TaskVariation,
    UserStory,
    VariableBase,
)
from scene_dsl.classes.common import SetBase
from scene_dsl.classes.scene import (
    AgentSet,
    ObjectSet,
    SceneModel,
    SceneSet,
    SimilarAgentSet,
    SimilarObjectSet,
    WorkspaceSet,
)
from robbdd.rdf.clauses import add_clause_expr, add_gwt_expr, add_node_time_constraint
from robbdd.rdf.common import add_node_list_pred
from scene_dsl.rdf.scene import add_agn_set, add_obj_set, add_scene_model, add_scene_set, add_ws_set


def add_scenario_tmpl(graph: Graph, tmpl: ScenarioTemplate):
    graph.bind(prefix=tmpl.ns_prefix, namespace=tmpl.namespace)
    graph.add(triple=(tmpl.uri, RDF.type, URI_BDD_TYPE_SCENARIO_TMPL))

    add_node_time_constraint(graph=graph, tc=tmpl.duration, node_uri=tmpl.uri)

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


def get_var_value_node(graph: Graph, var_val: Any, set_uris: set[URIRef]) -> Node:
    if hasattr(var_val, "linked_val") and var_val.linked_val is not None:
        assert hasattr(
            var_val.linked_val, "uri"
        ), f"Linked value has no URI attr: {var_val.linked_val}"

        # Add scene sets, in case they're not included explicitly by ScenarioVariant
        if hasattr(var_val.linked_val, "parent") and isinstance(
            var_val.linked_val.parent, SceneSet
        ):
            add_scene_set(graph=graph, scene_set=var_val.linked_val.parent, set_uris=set_uris)

        assert var_val.linked_val.uri is not None
        return var_val.linked_val.uri

    if hasattr(var_val, "num_val") and var_val.num_val is not None:
        return Literal(var_val.num_val)

    if hasattr(var_val, "str_val") and var_val.str_val is not None:
        return Literal(var_val.str_val)

    raise ValueError(f"ValidVarValue object has unhandled attributes: {var_val}")


def add_explicit_set(graph: Graph, const_set: ExplicitSet, set_uris: set[URIRef]) -> IdentifiedNode:
    if const_set.uri in set_uris:
        return const_set.uri

    graph.add(triple=(const_set.uri, RDF.type, URI_BDD_TYPE_SET))
    graph.add(triple=(const_set.uri, RDF.type, URI_BDD_TYPE_CONST_SET))
    for v in const_set.elems:
        graph.add(
            triple=(
                const_set.uri,
                URI_BDD_PRED_ELEMS,
                get_var_value_node(graph=graph, var_val=v, set_uris=set_uris),
            )
        )
    set_uris.add(const_set.uri)
    return const_set.uri


def get_set_expr_set(graph: Graph, set_expr: Any, set_uris: set[URIRef]) -> IdentifiedNode:
    assert (
        hasattr(set_expr, "elems") and set_expr.elems is not None
    ), f"SetExpr object has invalid 'elems' attr: {set_expr}"
    col_first = BNode()
    col = Collection(graph=graph, uri=col_first, seq=[])
    for elem in set_expr.elems:
        col.append(get_var_value_node(graph=graph, var_val=elem, set_uris=set_uris))
    return col_first


def add_const_set(
    graph: Graph, scene_model: SceneModel, set_obj: SetBase, set_uris: set[URIRef]
) -> IdentifiedNode:
    if isinstance(set_obj, ExplicitSet):
        return add_explicit_set(graph=graph, const_set=set_obj, set_uris=set_uris)

    if isinstance(set_obj, (ObjectSet, SimilarObjectSet)):
        add_obj_set(
            graph=graph,
            obj_set=set_obj,
            set_uris=set_uris,
            scn_comp_uri=scene_model.scene_obj_uri,
        )
        return set_obj.uri

    if isinstance(set_obj, WorkspaceSet):
        add_ws_set(
            graph=graph,
            ws_set=set_obj,
            set_uris=set_uris,
            scn_comp_uri=scene_model.scene_ws_uri,
        )
        return set_obj.uri

    if isinstance(set_obj, (AgentSet, SimilarAgentSet)):
        add_agn_set(
            graph=graph,
            agn_set=set_obj,
            set_uris=set_uris,
            scn_comp_uri=scene_model.scene_agn_uri,
        )
        return set_obj.uri

    raise ValueError(f"ConstantSet type not handled for: {set_obj}")


def add_task_variation(
    graph: Graph, variation: TaskVariation, scene_model: SceneModel, set_uris: set[URIRef]
):
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
            num_row_val = len(r.values)
            num_var = len(variation.header.variables)
            if num_row_val != num_var:
                raise ValueError(
                    f"number of row values ({num_row_val}) != number of variables ({num_var})"
                )
            for i, v in enumerate(r.values):
                var = variation.header.variables[i]
                if "ValidVarValue" in v.__class__.__name__:
                    var_value = get_var_value_node(graph=graph, var_val=v, set_uris=set_uris)
                    if isinstance(var, ScenarioSetVariable):
                        raise ValueError(
                            f"ScenarioSetVariable '{var.name}' assigned a non-set value: {var_value}"
                        )
                    if hasattr(v, "linked_val") and isinstance(v.linked_val, (SetBase, SceneSet)):
                        raise ValueError(
                            f"ScenarioVariable '{var.name}' assigned a set: {var_value}"
                        )
                    r_col.append(var_value)
                elif "ConstSetLink" in v.__class__.__name__:
                    assert hasattr(
                        v, "linked_set"
                    ), f"ConstSetLink obj has no 'linked_set' attr: '{v}'"
                    if isinstance(var, ScenarioVariable):
                        raise ValueError(
                            f"ScenarioVariable '{var.name}' assigned a set value: {v.linked_set}"
                        )
                    r_col.append(
                        add_const_set(
                            graph=graph,
                            scene_model=scene_model,
                            set_obj=v.linked_set,
                            set_uris=set_uris,
                        )
                    )
                elif "SetExpr" in v.__class__.__name__:
                    if isinstance(var, ScenarioVariable):
                        raise ValueError(f"ScenarioVariable '{var.name}' assigned a set value")
                    r_col.append(get_set_expr_set(graph=graph, set_expr=v, set_uris=set_uris))
                else:
                    raise ValueError(
                        f"unhandled value type '{v.__class__.__name__}' in table variation for '{variation.uri}'"
                    )

            rows_col.append(r_first)

    elif isinstance(variation, CartesianProductVariation):
        graph.add(triple=(variation.uri, RDF.type, URI_BDD_TYPE_CART_PRODUCT))
        sets_col = add_node_list_pred(
            graph=graph, subject_uri=variation.uri, pred_uri=URI_BDD_PRED_OF_SETS, nodes=[]
        )
        for v_set in variation.var_sets:
            var_list_col.append(v_set.variable.uri)
            if hasattr(v_set.val_set, "elems"):
                # explicit set
                sets_col.append(
                    get_set_expr_set(graph=graph, set_expr=v_set.val_set, set_uris=set_uris)
                )
            elif hasattr(v_set.val_set, "sets"):
                # set of sets
                set_of_sets_first = BNode()
                set_of_sets_col = Collection(graph=graph, uri=set_of_sets_first, seq=[])
                for set_expr in v_set.val_set.sets:
                    set_of_sets_col.append(
                        get_set_expr_set(graph=graph, set_expr=set_expr, set_uris=set_uris)
                    )
                sets_col.append(set_of_sets_first)

            elif hasattr(v_set.val_set, "linked_set"):
                # link to constant set
                sets_col.append(
                    add_const_set(
                        graph=graph,
                        scene_model=scene_model,
                        set_obj=v_set.val_set.linked_set,
                        set_uris=set_uris,
                    )
                )

            elif isinstance(v_set.val_set, Combination):
                graph.add(triple=(v_set.val_set.uri, RDF.type, URI_BDD_TYPE_COMBINATION))
                graph.add(
                    triple=(
                        v_set.val_set.uri,
                        URI_BDD_PRED_LENGTH,
                        Literal(v_set.val_set.length, datatype=XSD.positiveInteger),
                    )
                )
                graph.add(
                    triple=(
                        v_set.val_set.uri,
                        URI_BDD_PRED_REP_ALLOWED,
                        Literal(v_set.val_set.repeated),
                    )
                )
                graph.add(triple=(v_set.val_set.uri, URI_BDD_PRED_FROM, v_set.val_set.from_set.uri))
                add_const_set(
                    graph=graph,
                    scene_model=scene_model,
                    set_obj=v_set.val_set.from_set,
                    set_uris=set_uris,
                )
                sets_col.append(v_set.val_set.uri)

            elif isinstance(v_set.val_set, Permutation):
                graph.add(triple=(v_set.val_set.uri, RDF.type, URI_BDD_TYPE_PERMUTATION))
                graph.add(
                    triple=(
                        v_set.val_set.uri,
                        URI_BDD_PRED_LENGTH,
                        Literal(v_set.val_set.length, datatype=XSD.positiveInteger),
                    )
                )
                graph.add(triple=(v_set.val_set.uri, URI_BDD_PRED_FROM, v_set.val_set.from_set.uri))
                add_const_set(
                    graph=graph,
                    scene_model=scene_model,
                    set_obj=v_set.val_set.from_set,
                    set_uris=set_uris,
                )
                sets_col.append(v_set.val_set.uri)
            else:
                raise ValueError(
                    f"unhandled attr '{v_set.val_set}' for VariationSet '{v_set}' in '{variation.uri}'"
                )
    else:
        raise ValueError(
            f"TaskVariation type not handled for variant '{variation.parent.uri}': {type(variation)}"
        )


def add_scenario_variant(
    graph: Graph,
    variant: ScenarioVariant,
    templates: set[URIRef],
    scenes: set[URIRef],
    set_uris: set[URIRef],
):
    graph.add(triple=(variant.uri, RDF.type, URI_BDD_TYPE_SCENARIO_VARIANT))

    # template
    if variant.template.uri not in templates:
        add_scenario_tmpl(graph=graph, tmpl=variant.template)
        templates.add(variant.template.uri)

    # add extra clauses:
    clause_col = add_node_list_pred(
        graph=graph, subject_uri=variant.uri, pred_uri=URI_BDD_PRED_HAS_CLAUSE, nodes=[]
    )
    if variant.given_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=variant.given_expr.given,
            clause_of_uri=variant.template.given_uri,
            clause_col=clause_col,
        )
    if variant.then_expr is not None:
        add_clause_expr(
            graph=graph,
            clause=variant.then_expr.then,
            clause_of_uri=variant.template.then_uri,
            clause_col=clause_col,
        )

    graph.add(triple=(variant.uri, URI_BDD_PRED_OF_TMPL, variant.template.uri))

    # scene
    scn_has_obj, scn_has_ws, scn_has_agn = False, False, False
    if variant.scene.uri not in scenes:
        scn_has_obj, scn_has_ws, scn_has_agn = add_scene_model(
            graph=graph, scene=variant.scene, set_uris=set_uris
        )
        scenes.add(variant.scene.uri)

    if scn_has_obj:
        graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_obj_uri))
        graph.add(
            triple=(variant.scene.scene_obj_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
        )
    if scn_has_ws:
        graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_ws_uri))
        graph.add(
            triple=(variant.scene.scene_ws_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
        )
    if scn_has_agn:
        graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_SCENE, variant.scene.scene_agn_uri))
        graph.add(
            triple=(variant.scene.scene_agn_uri, URI_BDD_PRED_OF_SCENE, variant.template.scene_uri)
        )

    # variation
    add_task_variation(
        graph=graph, variation=variant.variation, scene_model=variant.scene, set_uris=set_uris
    )
    graph.add(triple=(variant.uri, URI_BDD_PRED_HAS_VARIATION, variant.variation.uri))


def add_us_to_graph(
    graph: Graph,
    us: UserStory,
    templates: set[URIRef],
    scenes: set[URIRef],
    set_uris: set[URIRef],
):
    graph.bind(us.ns_prefix, us.namespace, override=True)
    graph.add(triple=(us.uri, RDF.type, URI_BDD_TYPE_US))
    for scr_var in us.scenarios:
        add_scenario_variant(
            graph=graph, variant=scr_var, templates=templates, scenes=scenes, set_uris=set_uris
        )
        graph.add((us.uri, URI_BDD_PRED_HAS_AC, scr_var.uri))


def create_bdd_model_graph(model: Any, g: Optional[Graph] = None) -> Graph:
    if g is None:
        g = Graph()

    events = getattr(model, "events", None)
    assert events is not None and isinstance(events, list), "no list of events in model"
    for evt in events:
        g.bind(prefix=evt.ns_prefix, namespace=evt.namespace)
        g.add(triple=(evt.uri, RDF.type, NS_MM_TIME["Event"]))

    tasks = getattr(model, "tasks", None)
    assert tasks is not None and isinstance(tasks, list), "no list of tasks in model"
    for task in tasks:
        g.bind(prefix=task.ns_prefix, namespace=task.namespace)
        g.add(triple=(task.uri, RDF.type, URI_TASK_TYPE_TASK))

    tmpl_uris = set()
    templates = getattr(model, "templates", None)
    if templates is not None:
        for tmpl in templates:
            tmpl_uris.add(tmpl.uri)
            add_scenario_tmpl(graph=g, tmpl=tmpl)

    stories = getattr(model, "stories", None)
    scenes = set()
    set_uris = set()
    if stories is not None:
        for us in stories:
            add_us_to_graph(graph=g, us=us, templates=tmpl_uris, scenes=scenes, set_uris=set_uris)

    return g
