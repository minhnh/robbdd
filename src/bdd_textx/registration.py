from os.path import abspath, dirname, join
from textx import LanguageDesc, metamodel_from_file
import textx.scoping.providers as scoping_providers
from bdd_textx.classes.bdd import UserStory, ScenarioTemplate


CWD = abspath(dirname(__file__))


def scene_metamodel():
    mm_scene = metamodel_from_file(join(CWD, "grammars", "scene.tx"))
    mm_scene.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )
    return mm_scene


def bdd_metamodel():
    mm_bdd = metamodel_from_file(
        join(CWD, "grammars", "bdd.tx"), classes=[UserStory, ScenarioTemplate]
    )
    mm_bdd.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(),
        }
    )
    return mm_bdd


scene_lang = LanguageDesc(
    "scene-tx",
    pattern="*.scene",
    description="Language for describing robotic scenes",
    metamodel=scene_metamodel,
)
bdd_lang = LanguageDesc(
    "bdd-tx",
    pattern="*.bdd",
    description="Behaviour-Driven Development language",
    metamodel=bdd_metamodel,
)
