from pprint import pprint
from rdf_utils.uri import URL_SECORO_M, URL_SECORO_MM

def prepare_context_data(metamodel, model):
    "Prepare and populate the context for jinja template"

    context = {
        'behaviours': model.behaviours,
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
        elif "scene" == ns_item.name:
            context['namespaces']['scene'] = ns_item
        elif "scene_" + context['namespaces']['environments'].name == ns_item.name:
            context['namespaces']['scene_env'] = ns_item

    # Add behaviour filename to context
    context['behaviours_f'] = context['behaviours'][0].name

    return context