from pprint import pprint

def prepare_context_data(metamodel, model):
    "Prepare and populate the context for jinja template"

    context = {
        'behaviours': model.behaviours,
        'events': model.events,
        'namespaces': model.namespaces,
        'stories': model.stories,
        'templates': model.templates,
    }
    
    # Add scene model to context
    for import_item in model.imports:
        if ".scene" in import_item.importURI:
            context['scene'] = import_item._tx_loaded_models[0]

    # Add agents and environments namespaces to context
    for ns_item in context['scene'].namespaces:
        if "_agn" in ns_item.name:
            context['agents_ns'] = ns_item
            context['agents_file'] = ns_item.name.split("_")[0]
        elif "_env" in ns_item.name:
            context['environments_ns'] = ns_item
            context['environments_file'] = ns_item.name.split("_")[0]

    pprint(context['scene'].__dict__)

    return context