# SPDX-License-Identifier: MPL-2.0
import sys
from os.path import abspath, dirname, join
from urllib.error import HTTPError
from rdf_utils.naming import get_valid_filename
from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import load_template_from_file, prepare_jinja2_template_data
from robbdd.rdf.bdd import create_bdd_model_graph
from robbdd.rdf.bddx import create_bddx_model_graph
from scene_dsl.gens import graph_gen, graph_gen_console


__CWD = abspath(dirname(__file__))


def bdd_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    graph_gen_console(create_bdd_model_graph(model=model), **kwargs)


def bdd_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    graph_gen(create_bdd_model_graph(model=model), model, output_path, overwrite, "bdd", **kwargs)


def bddx_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    graph_gen_console(create_bddx_model_graph(model=model), **kwargs)


def bddx_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    graph_gen(create_bddx_model_graph(model=model), model, output_path, overwrite, "bddx", **kwargs)


def gherkin_gen(metamodel, model, output_path, overwrite, debug):
    g = create_bdd_model_graph(model=model)

    # resolver for caching remote models
    install_resolver()

    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    processed_bdd_data = prepare_jinja2_template_data(us_loader, g)
    feature_template = load_template_from_file(join(__CWD, "templates", "robbdd.feature.jinja"))
    for us_data in processed_bdd_data:
        us_name = us_data["name"]
        feature_content = feature_template.render(data=us_data)
        feature_filename = f"{get_valid_filename(us_name)}.feature"
        filepath = join("" if output_path is None else output_path, feature_filename)
        with open(filepath, mode="w", encoding="utf-8") as of:
            of.write(feature_content)
        print(f"... wrote {filepath}")
