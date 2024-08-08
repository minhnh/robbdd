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

    pprint(model.__dict__)
    pprint(model.namespaces[0].__dict__)
    pprint(model.namespaces[1].__dict__)

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
            context['agents_f'] = ns_item.name.split("_")[0]
        elif "_env" in ns_item.name:
            context['namespaces']['environments'] = ns_item
            context['environments_f'] = ns_item.name.split("_")[0]

    # Add behaviour filename to context
    context['behaviours_f'] = context['behaviours'][0].name

    return context