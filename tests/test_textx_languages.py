#!/usr/bin/env python
import unittest
from os.path import dirname, join
from urllib.error import HTTPError
from rdflib import RDF
from textx import metamodel_for_language

from bdd_dsl.models.urirefs import (
    URI_BDD_PRED_OF_SCENE,
)
from rdf_utils.resolver import install_resolver
from rdf_utils.constraints import check_shacl_constraints
from bdd_dsl.models.user_story import UserStoryLoader
from robbdd.rdf.scene import (
    URI_DYN_TYPE_MASS_SCALAR,
    URI_GEOM_TYPE_RIGID_BODY,
    create_scene_model_graph,
)
from robbdd.rdf.bdd import create_bdd_model_graph
from robbdd.rdf.bddx import create_bddx_model_graph


ROOT_DIR = dirname(dirname(__file__))
MODELS_DIR = join(ROOT_DIR, "examples", "models")


class TestTextXLanguages(unittest.TestCase):
    def setUp(self) -> None:
        install_resolver()

    def test_robbdd_scene(self):
        """Test scene-tx language"""
        scene_mm = metamodel_for_language("robbdd-scene")
        scene_model = scene_mm.model_from_file(join(MODELS_DIR, "lab.scene"))
        assert len(scene_model.scene_models) > 0
        assert len(scene_model.scene_insts) > 0
        assert len(scene_model.sim_obj_sets) > 0
        balls = next(s for s in scene_model.sim_obj_sets if s.name == "balls")
        cubes = next(s for s in scene_model.sim_obj_sets if s.name == "cubes")
        assert [obj.name for obj in balls.objects] == ["ball0", "ball1", "ball2"]
        assert [obj.name for obj in cubes.objects] == ["cube0", "cube1"]
        table_obj = next(
            obj
            for inst in scene_model.scene_insts
            for obj in inst.modelled_objs
            if obj.geometry.name == "table_geom"
        )
        assert table_obj.body.name == "table_body"
        assert table_obj.body.mass == 10.0
        panda = next(
            agn
            for inst in scene_model.scene_insts
            for agn in inst.modelled_agns
            if agn.agn.name == "panda"
        )
        gripper_body = panda.attachments[0].body
        assert gripper_body.name == "gripper_body"

        g = create_scene_model_graph(scene_model)
        assert len(g) > 0
        assert (table_obj.body.uri, RDF.type, URI_GEOM_TYPE_RIGID_BODY) in g
        assert (table_obj.body.inertia_coord_uri, RDF.type, URI_DYN_TYPE_MASS_SCALAR) in g
        assert (gripper_body.uri, RDF.type, URI_GEOM_TYPE_RIGID_BODY) in g

        check_shacl_constraints(
            graph=g,
            shacl_dict={
                "https://comp-rob2b.github.io/metamodels/geometry/spatial-relations.ttl": "turtle",
                "https://comp-rob2b.github.io/metamodels/geometry/coordinates.ttl": "turtle",
            },
            quiet=False,
        )

    def test_robbdd(self):
        """Test RobBDD language"""
        bdd_mm = metamodel_for_language("robbdd")
        for model_name in [
            "pickplace_table.bdd",
            "pickplace_cart_product.bdd",
            "pickplace_quantifiers.bdd",
            "pickplace_table_custom.bdd",
        ]:
            bdd_model = bdd_mm.model_from_file(join(MODELS_DIR, model_name))
            assert len(bdd_model.templates) > 0
            assert len(bdd_model.stories) > 0
            assert len(bdd_model.stories[0].scenarios) > 0

            g = create_bdd_model_graph(model=bdd_model)
            try:
                _ = UserStoryLoader(g)
            except HTTPError as e:
                raise RuntimeError(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")

    def test_robbdd_exec(self):
        """Test RobBDD execution language"""
        bddx_mm = metamodel_for_language("robbdd-exec")
        bddx_model = bddx_mm.model_from_file(join(MODELS_DIR, "pickplace_table_custom.bddx"))

        g = create_bddx_model_graph(model=bddx_model)
        assert len(g) > 0
        scr_exec = bddx_model.scenario_execs[0]
        assert (
            scr_exec.scene_inst.uri,
            URI_BDD_PRED_OF_SCENE,
            scr_exec.variant.template.scene_uri,
        ) in g
