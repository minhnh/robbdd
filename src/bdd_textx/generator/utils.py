from rdf_utils.uri import URL_SECORO_M, URL_SECORO_MM
from os import path

def append_to_fluents(context, clause_type):
    "Append a new fluent to the context if it does not exist"

    if 'fluents' not in context:
        context['fluents'] = []

    if clause_type not in [fluent['clause_type'] for fluent in context['fluents']]:
        fluent = {
            'clause_type': clause_type
        }
        if clause_type == 'LocatedAtFluentClause':
            fluent['name'] = 'located-at'
            fluent['type'] = 'LocatedAtPredicate'
        elif clause_type == 'DoesNotDropFluentClause':
            fluent['name'] = 'does-not-drop'
            fluent['type'] = 'DoesNotDropPredicate'
        else:
            fluent['name'] = clause_type
            fluent['type'] = clause_type + 'Predicate'
        context['fluents'].append(fluent)

def create_clause_data(tc_type, clause_type):
    "Create clause data based on time constraint type"

    clause_data = {}
    if tc_type == 'BeforeEvent':
        clause_data['tc_name'] = 'before'
        clause_data['ec_type'] = 'BeforeEventConstraint'
    elif tc_type == 'AfterEvent':
        clause_data['tc_name'] = 'after'
        clause_data['ec_type'] = 'AfterEventConstraint'
    elif tc_type == 'DuringEvent':
        clause_data['tc_name'] = 'during'
        clause_data['ec_type'] = 'DuringEventConstraint'
    if clause_type == 'LocatedAtFluentClause':
        clause_data['fl_name'] = 'located-at'
    elif clause_type == 'DoesNotDropFluentClause':
        clause_data['fl_name'] = 'does-not-drop'
    else:
        clause_data['fl_name'] = clause_type
    return clause_data

def create_variation_data(var_type):
    "Create variation data based on variation type"

    variation_data = {
        'var_type': var_type
    }
    if var_type == 'CartesianProductVariation':
        variation_data['var_name'] = 'var-product'
    elif var_type == 'TableVariation':
        variation_data['var_name'] = 'var-table'
    return variation_data

def prepare_context_data(metamodel, model):
    "Prepare and populate the context for jinja template"

    context = {
        'behaviours': model.behaviours,
        'tasks': model.tasks,
        'events': model.events,
        'stories': model.stories,
        'templates': model.templates,
    }

    # Add Secoro namespaces to context
    context['secoro_m'] = URL_SECORO_M
    context['secoro_mm'] = URL_SECORO_MM

    context['namespaces'] = {
        'bdd': model.namespaces[0],
        'tmpl': model.namespaces[1],
    }
    
    # Add scene model to context
    for import_item in model.imports:
        if ".scene" in import_item.importURI:
            context['scene'] = import_item._tx_loaded_models[0]

    # Add agents and environments namespaces to context
    for ns_item in context['scene'].namespaces:
        if "_agn" in ns_item.name:
            context['namespaces']['agents'] = ns_item
            context['namespaces']['agents'].name = ns_item.name.split("_")[0]
            context['agents_f'] = ns_item.name.split("_")[0]
        elif "_env" in ns_item.name:
            context['namespaces']['environments'] = ns_item
            context['namespaces']['environments'].name = ns_item.name.split("_")[0]
            context['environments_f'] = ns_item.name.split("_")[0]

    context['namespaces']['scene'] = context['scene'].model.agent_ns[0].ns
    context['namespaces']['scene_env'] = context['scene'].model.environment_ns[0].ns

    # Prepare fluents and clauses
    context['fl_templates'] = []
    for i in range(len(context['templates'])):
        template = context['templates'][i]
        context['fl_templates'].append({
            'given_clauses': [],
            'then_clauses': [],
        })
        for j in range(len(template.given_clauses)):
            given_clause = context['templates'][i].given_clauses[j]
            clause_type = type(given_clause).__name__
            append_to_fluents(context, clause_type)
            
            tc_type = type(given_clause.tc).__name__
            fl_given_clause = create_clause_data(tc_type, clause_type)
            context['fl_templates'][i]['given_clauses'].append(fl_given_clause)

        for j in range(len(template.then_clauses)):
            then_clause = context['templates'][i].then_clauses[j]
            clause_type = type(then_clause).__name__
            append_to_fluents(context, clause_type)

            tc_type = type(then_clause.tc).__name__
            fl_then_clause = create_clause_data(tc_type, clause_type)
            context['fl_templates'][i]['then_clauses'].append(fl_then_clause)

    # Prepare variations and check for product/table variations
    context['var_stories'] = []
    for i in range(len(context['stories'])):
        story = context['stories'][i]
        context['var_stories'].append({
            'scenarios': [],
        })
        for j in range(len(story.scenarios)):
            scenario = story.scenarios[j]
            var_type = type(scenario.variation).__name__
            context['var_stories'][i]['scenarios'].append(create_variation_data(var_type))

    # Add behaviour filename to context
    file_name, _ = path.splitext(path.basename(model._tx_filename))
    context['behaviours_f'] = file_name

    return context