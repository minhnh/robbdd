from pprint import pprint
from rdf_utils.uri import URL_SECORO_M, URL_SECORO_MM
from os import path

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

    # Prepare fluents
    context['fluents'] = []
    for template in context['templates']:
        for given_clause in template.given_clauses:
            clause_type = type(given_clause).__name__
            if clause_type not in [fluent['clause_type'] for fluent in context['fluents']]:
                fluent = {
                    'clause_type': clause_type
                }
                if clause_type == 'LocatedAtFluentClause':
                    fluent['name'] = 'fl-located-at'
                    fluent['type'] = 'LocatedAtPredicate'
                elif clause_type == 'DoesNotDropFluentClause':
                    fluent['name'] = 'fl-does-not-drop'
                    fluent['type'] = 'DoesNotDropPredicate'
                else:
                    fluent['name'] = 'fl-' + clause_type
                    fluent['type'] = clause_type + 'Predicate'
                context['fluents'].append(fluent)
            
            # Prepare given clauses
            

    pprint(type(context['templates'][0].given_clauses[0]).__name__)

    # Add behaviour filename to context
    file_name, _ = path.splitext(path.basename(model._tx_filename))
    context['behaviours_f'] = file_name

    return context