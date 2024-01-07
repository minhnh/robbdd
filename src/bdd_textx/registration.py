from os.path import abspath, dirname, join
from textx import LanguageDesc, metamodel_from_file
import textx.scoping.providers as scoping_providers
from bdd_textx.classes.uri import URI, ShortURI, NamespaceDeclare


CWD = abspath(dirname(__file__))


def bdd_metamodel():
    mm_bdd = metamodel_from_file(
        join(CWD, "grammars", "bdd.tx"), classes=[URI, ShortURI, NamespaceDeclare]
    )
    mm_bdd.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )
    return mm_bdd


bdd_lang = LanguageDesc(
    "bdd-tx",
    pattern="*.bdd",
    description="Behaviour-Driven Development language",
    metamodel=bdd_metamodel,
)
