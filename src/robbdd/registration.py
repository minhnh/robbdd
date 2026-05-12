# SPDX-License-Identifier: MPL-2.0
from textx import (
    LanguageDesc,
    GeneratorDesc,
)
from robbdd.langs import scene_metamodel, bdd_metamodel, bddx_metamodel
from robbdd.gens import (
    bdd_graph_gen_console,
    bdd_graph_gen,
    bddx_graph_gen,
    bddx_graph_gen_console,
    gherkin_gen,
    scene_graph_gen_console,
    scene_graph_gen,
)


scene_lang = LanguageDesc(
    "robbdd-scene",
    pattern="*.scene",
    description="Language for describing robotic scenes",
    metamodel=scene_metamodel,
)
bdd_lang = LanguageDesc(
    "robbdd",
    pattern="*.bdd",
    description="Behaviour-Driven Development language",
    metamodel=bdd_metamodel,
)
bddx_lang = LanguageDesc(
    "robbdd-exec",
    pattern="*.bddx",
    description="DSL for describing BDD execution",
    metamodel=bddx_metamodel,
)

robbdd_console_gen = GeneratorDesc(
    language="robbdd",
    target="console",
    description="Print a representation of RobBDD model graph to the console, default format is JSON-LD",
    generator=bdd_graph_gen_console,
)
robbdd_graph_gen = GeneratorDesc(
    language="robbdd",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD model graph, default format is JSON-LD",
    generator=bdd_graph_gen,
)
robbdd_exec_console_gen = GeneratorDesc(
    language="robbdd-exec",
    target="console",
    description="Print a representation of RobBDD execution model graph to the console, default format is JSON-LD",
    generator=bddx_graph_gen_console,
)
robbdd_exec_graph_gen = GeneratorDesc(
    language="robbdd-exec",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD execution model graph, default format is JSON-LD",
    generator=bddx_graph_gen,
)
robbdd_gherkin_gen = GeneratorDesc(
    language="robbdd",
    target="gherkin",
    description="Generate Gherkin feature files from RobBDD models",
    generator=gherkin_gen,
)
robbdd_scene_console_gen = GeneratorDesc(
    language="robbdd-scene",
    target="console",
    description="Print a representation of RobBDD scene model graph to the console, default format is JSON-LD",
    generator=scene_graph_gen_console,
)
robbdd_scene_graph_gen = GeneratorDesc(
    language="robbdd-scene",
    target="graph",
    description="Generate a RDF serialization of the given RobBDD scene model graph, default format is JSON-LD",
    generator=scene_graph_gen,
)
