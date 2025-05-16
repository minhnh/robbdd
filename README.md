# RobBDD

A Domain-Specific Language (DSL) for specifying robotic acceptance criteria, using
concepts from [bdd-dsl](https://github.com/secorolab/bdd-dsl)
(described on [this tutorial](https://secorolab.github.io/bdd-dsl/bdd-concepts.html)).
Details on how to create a RobBDD model is also available in [a tutorial](https://secorolab.github.io/bdd-dsl/robbdd.html)
on the same GitHub page.

## Installation

`robbdd` is a Python package and can be installed using `pip install`.
The following Python packages must also be installed as dependencies:

- [rdf-utils](https://github.com/minhnh/rdf-utils)
- [bdd-dsl](https://github.com/minhnh/bdd-dsl)

## Model generators

The `*.bdd` models under `examples/models` folder can be used to generate RDF graphs
or Gherkin feature files using the generators described below. RDF graph generation
uses available [serialization plugins provided by `rdflib`](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.serializers.html).
These generators are created using [textx generator mechanism](https://textx.github.io/textX/registration.html#textx-generators).
Two custom arguments are handled by the generators:

- `format`: available for `console` & `graph` generators, for specifying the RDF graph
  serialization format. See `rdflib` documentation (linked above) to see which are available.
  Typical formats are `json-ld`, `ttl`, `xml`. Default format if non specified is `json-ld`.
- `nocompact`: available for `console` & `graph` generators, when format is `json-ld`.
  If specified, won't add `@context` with prefix-namespace mapping in the serialized JSON.
- `filename`: available for `graph` & `gherkin` generators, for specifying the output file name.
  File extensions will be ignored. If not specified, the model file name will be used by default.

### Console

The `console` generator prints graph serialization to the console. Example use:

```console
foo@bar:~$ textx generate examples/models/pickplace_quantifiers.bdd --target console --format ttl
```

### Graph

The `graph` generator dump graph serialization to a file. Only `json-ld`, `ttl`, and `xml` formats
are currently supported, which generate to `.json`, `.ttl`, and `.xml` file extensions,
respectively. Example use for generating to the Turtle format:

```console
foo@bar:~$ textx generate examples/models/pickplace_table.bdd --target graph -o examples/generated --format ttl --filename model_graph
```

Or generate JSON-LD without compacting IRIs, using model name as file name:

```console
foo@bar:~$ textx generate examples/models/pickplace_quantifiers.bdd --target graph --nocompact -o examples/generated
```

### Gherkin

The `gherkin` generator create [Gherkin feature files](https://cucumber.io/docs/gherkin/reference/)
from the models using generation mechanism from the `bdd-dsl` package. Example use:

```console
foo@bar:~$ textx generate models/pickplace_quantifiers.bdd --target gherkin -o generated
```
