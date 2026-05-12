# SPDX-License-Identifier: MPL-2.0
import sys
from typing import Any
from os.path import abspath, basename, dirname, exists, join, splitext
from urllib.error import HTTPError
from rdflib.plugin import PluginException
from rdf_utils.naming import get_valid_filename
from rdf_utils.resolver import install_resolver
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import load_template_from_file, prepare_jinja2_template_data
from robbdd.graph import create_bdd_model_graph, create_bddx_model_graph, create_scene_model_graph


__CWD = abspath(dirname(__file__))
__GRAPH_FORMAT_EXT = {"json-ld": "json", "ttl": "ttl", "xml": "xml"}


def __parse_rdflib_serial_args(**kwargs):
    g_format = kwargs.get("format", "json-ld")
    assert (
        g_format in __GRAPH_FORMAT_EXT
    ), f"file extension not handled for graph format '{g_format}', try {list(__GRAPH_FORMAT_EXT.keys())}"

    ser_kwargs = {"format": g_format}
    if g_format == "json-ld":
        if "nocompact" in kwargs:
            ser_kwargs["auto_compact"] = False
        else:
            ser_kwargs["auto_compact"] = True
    return ser_kwargs


def __get_rdf_full_output_path(
    model, output_path: str, g_format: str, model_type: str, **kwargs: Any
):
    filename = kwargs.get("filename", basename(model._tx_filename))
    if filename is None:
        filename = "graph"
    full_filename = f"{splitext(filename)[0]}.{model_type}.{__GRAPH_FORMAT_EXT[g_format]}"
    full_output_path = join("" if output_path is None else output_path, full_filename)

    return full_output_path


def bdd_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    g = create_bdd_model_graph(model=model)
    try:
        print(g.serialize(**ser_kwargs))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def bdd_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    full_output_path = __get_rdf_full_output_path(
        model=model,
        output_path=output_path,
        g_format=ser_kwargs["format"],
        model_type="bdd",
        **kwargs,
    )
    if exists(full_output_path) and not overwrite:
        print(f"not overwriting existing file '{full_output_path}'")
        return

    g = create_bdd_model_graph(model=model)
    with open(full_output_path, "w") as outfile:
        outfile.write(g.serialize(**ser_kwargs))
    print(f"... wrote {full_output_path}")


def bddx_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    g = create_bddx_model_graph(model=model)
    try:
        print(g.serialize(**ser_kwargs))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def bddx_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    full_output_path = __get_rdf_full_output_path(
        model=model,
        output_path=output_path,
        g_format=ser_kwargs["format"],
        model_type="bddx",
        **kwargs,
    )
    if exists(full_output_path) and not overwrite:
        print(f"not overwriting existing file '{full_output_path}'")
        return

    g = create_bddx_model_graph(model=model)
    with open(full_output_path, "w") as outfile:
        outfile.write(g.serialize(**ser_kwargs))
    print(f"... wrote {full_output_path}")


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


def scene_graph_gen_console(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)
    g_format = ser_kwargs["format"]

    g = create_scene_model_graph(model=model)
    try:
        print(g.serialize(**ser_kwargs))
    except PluginException as e:
        raise ValueError(
            f"serialization format '{g_format}' not supported by rdflib, try {list(__GRAPH_FORMAT_EXT.keys())}: {e.msg}"
        )


def scene_graph_gen(metamodel, model, output_path, overwrite, debug, **kwargs):
    ser_kwargs = __parse_rdflib_serial_args(**kwargs)

    full_output_path = __get_rdf_full_output_path(
        model=model,
        output_path=output_path,
        g_format=ser_kwargs["format"],
        model_type="scene",
        **kwargs,
    )
    if exists(full_output_path) and not overwrite:
        print(f"not overwriting existing file '{full_output_path}'")
        return

    g = create_scene_model_graph(model=model)
    with open(full_output_path, "w") as outfile:
        outfile.write(g.serialize(**ser_kwargs))
    print(f"... wrote {full_output_path}")
