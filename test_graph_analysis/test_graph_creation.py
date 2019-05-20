"""
Copyright (C) 2018 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""


import json
import tempfile
import unittest
import uuid
import warnings
from pathlib import Path

import pandas as pd

from graph_analysis.graph_creation import Evaluator, Manager, MDTranslator
from graph_analysis.graph_objects import DiEdge, PropertyDiGraph, Vertex

from . import DATA_DIRECTORY, OUTPUT_DIRECTORY, PATTERNS


class TestManager(unittest.TestCase):
    def setUp(self):
        pass
        # instead of making objects that go through all these tests
        # make the data the instance variables that I can access to make
        # instances of the classes locally within the function scope.
        # self.manager = Manager(
        #     excel_path=[
        #         DATA_DIRECTORY / 'Composition Example.xlsx'
        #         for i in range(2)],
        #     json_path=PATTERNS / 'Composition.json')

    def test_ids_assinged_in_change(self):
        manager = Manager(
            excel_path=[
                (
                    DATA_DIRECTORY
                    / "Composition Example 2 Model Baseline.xlsx"
                ),
                (DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx"),
            ],
            json_path=(PATTERNS / "Composition.json"),
        )
        eval_base = manager.evaluators[0]
        eval_change = manager.evaluators[1]

        eval_base.rename_df_columns()
        eval_base.add_missing_columns()
        eval_base.to_property_di_graph()
        base_prop_graph = eval_base.prop_di_graph

        base_vert_set = base_prop_graph.vertex_set

        eval_change.rename_df_columns()
        eval_change.add_missing_columns()
        eval_change.to_property_di_graph()
        change_prop_graph = eval_change.prop_di_graph

        change_vert_set = change_prop_graph.vertex_set

        # I want to see if the nodes in the graph have the right ids
        diff_nodes = set(change_prop_graph).difference(set(base_prop_graph))
        diff_dict = {
            key: eval_change.translator.uml_id[key] for key in diff_nodes
        }
        self.assertTrue(
            set(eval_base.translator.uml_id.keys()).issubset(
                set(eval_change.translator.uml_id.keys())
            )
        )
        for key in eval_base.translator.uml_id.keys():
            if key is not "count":
                self.assertEqual(
                    eval_base.translator.uml_id[key],
                    eval_change.translator.uml_id[key],
                )

    def test_get_json_data(self):
        manager = Manager(
            excel_path=[
                DATA_DIRECTORY / "Composition Example.xlsx" for i in range(2)
            ],
            json_path=PATTERNS / "Composition.json",
        )
        expected_keys = [
            "Columns to Navigation Map",
            "Pattern Graph Edges",
            "Root Node",
            "Vertex MetaTypes",
            "Vertex Settings",
            "Vertex Stereotypes",
        ]

        assert expected_keys == list(manager.json_data.keys())

    def test_create_evaluators(self):
        manager = Manager(
            excel_path=[
                DATA_DIRECTORY / "Composition Example.xlsx" for i in range(2)
            ],
            json_path=PATTERNS / "Composition.json",
        )
        # weak test: create_evaluators() run during init
        self.assertEqual(2, len(manager.evaluators))
        for eval in manager.evaluators:
            self.assertIsInstance(eval, Evaluator)

    def test_get_pattern_graph_diff(self):
        # this is a bad function and an improper test.
        # The test ignores the obvious problem of non-unique matchings
        # Want added edge, deleted edge, one matched, one unstable pair
        manager = Manager(
            excel_path=[
                DATA_DIRECTORY / "Composition Example.xlsx" for i in range(2)
            ],
            json_path=PATTERNS / "Composition.json",
        )
        # Have to create the actual graph object because get_pattern_graph_diff
        # employs the graph object properties
        # with 2 different original edges of the same type I can induce a
        # match based on rename and an unstable pair.
        og_eval = manager.evaluators[0]
        og_graph = PropertyDiGraph()
        og_eval.prop_di_graph = og_graph
        ch_eval = manager.evaluators[1]
        ch_graph = PropertyDiGraph()
        ch_eval.prop_di_graph = ch_graph
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            orig_edge = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            renm_source = DiEdge(
                source=Vertex(
                    name="Subaru",
                    id="_001",
                    original_name="Car",
                    original_id="_001",
                    node_types=["Atomic Thing"],
                ),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            orig_edge2 = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="Vehicle", id="_003"),
                edge_attribute="type",
            )
            unstab_edge1 = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="Not Car", id="_100"),
                edge_attribute="type",
            )
            unstab_edge2 = DiEdge(
                source=Vertex(name="Cup", id="_101"),
                target=Vertex(name="Vehicle", id="_003"),
                edge_attribute="type",
            )
            added_edge = DiEdge(
                source=Vertex(
                    name="New Source",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                target=Vertex(
                    name="New Target",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                edge_attribute="newEdge",
            )
            del_edge = DiEdge(
                source=Vertex(name="Old Source", id="_010"),
                target=Vertex(name="Old Target", id="_011"),
                edge_attribute="oldEdge",
            )
            original_edges = [orig_edge, orig_edge2, del_edge]
            change_edge = [
                renm_source,
                unstab_edge1,
                unstab_edge2,
                added_edge,
            ]
            orig_attrs = [
                {"diedge": edge, "edge_attribute": edge.edge_attribute}
                for edge in original_edges
            ]
            change_attrs = [
                {"diedge": edge, "edge_attribute": edge.edge_attribute}
                for edge in change_edge
            ]
            for edge in zip(original_edges, orig_attrs):
                og_graph.add_node(
                    edge[0].source.name,
                    **{edge[0].source.name: edge[0].source}
                )
                og_graph.add_node(
                    edge[0].target.name,
                    **{edge[0].target.name: edge[0].target}
                )
                og_graph.add_edge(
                    edge[0].source.name, edge[0].target.name, **edge[1]
                )
            for edge in zip(change_edge, change_attrs):
                ch_graph.add_node(
                    edge[0].source.name,
                    **{edge[0].source.name: edge[0].source}
                )
                ch_graph.add_node(
                    edge[0].target.name,
                    **{edge[0].target.name: edge[0].target}
                )
                ch_graph.add_edge(
                    edge[0].source.name, edge[0].target.name, **edge[1]
                )

            ch_dict = manager.get_pattern_graph_diff(out_directory=tmpdir)

            ch_dict = ch_dict["0-1"]

            changes = ch_dict["Changes"]
            add = changes["Added"]  # a list
            deld = changes["Deleted"]  # a list
            unstab = ch_dict["Unstable Pairs"]  # DiEdge: [DiEdge ...]
            unstab[orig_edge2] = set(unstab[orig_edge2])
            change = changes[orig_edge]

            assert change[0] == renm_source
            assert add == [added_edge]
            assert deld == [del_edge]
            assert unstab == {
                orig_edge2: {unstab_edge1, renm_source, unstab_edge2}
            }

    def test_changes_to_excel(self):
        manager = Manager(
            excel_path=[
                DATA_DIRECTORY / "Composition Example.xlsx" for i in range(1)
            ],
            json_path=PATTERNS / "Composition.json",
        )
        og_edge = DiEdge(
            source=Vertex(name="green"),
            target=Vertex(name="apple"),
            edge_attribute="fruit",
        )
        change_edge = DiEdge(
            source=Vertex(name="gala"),
            target=Vertex(name="apple"),
            edge_attribute="fruit",
        )
        added_edge = DiEdge(
            source=Vertex(name="blueberry"),
            target=Vertex(name="berry"),
            edge_attribute="bush",
        )
        deleted_edge = DiEdge(
            source=Vertex(name="yellow"),
            target=Vertex(name="delicious"),
            edge_attribute="apple",
        )
        unstable_key = DiEdge(
            source=Vertex(name="tomato"),
            target=Vertex(name="fruit"),
            edge_attribute="fruit",
        )
        unstable_one = DiEdge(
            source=Vertex(name="tomato"),
            target=Vertex(name="vegetable"),
            edge_attribute="fruit",
        )
        unstable_two = DiEdge(
            source=Vertex(name="tomahto"),
            target=Vertex(name="fruit"),
            edge_attribute="fruit",
        )
        new_name = Vertex(name="new name")
        old_name = Vertex(name="old name")

        fake_datas = {
            "0-1": {
                "Changes": {
                    "Added": [added_edge],
                    "Deleted": [deleted_edge],
                    og_edge: [change_edge],
                },
                "Unstable Pairs": {
                    unstable_key: [unstable_one, unstable_two]
                },
            }
        }
        manager.evaluator_change_dict = fake_datas
        with tempfile.TemporaryDirectory() as tmpdir:
            outdir = Path(tmpdir)
            manager.changes_to_excel(out_directory=outdir)

            created_file_name = list(outdir.glob("*.xlsx"))[0]
            created_file = OUTPUT_DIRECTORY / created_file_name
            created_df = pd.read_excel(created_file)
            created_dict = created_df.to_dict()

            expected_data = {
                "Edit 1": ["('green', 'apple', 'fruit')"],
                "Edit 2": ["('gala', 'apple', 'fruit')"],
                "Unstable Matches Original": [
                    "('tomato', 'fruit', 'fruit')",
                    "('tomato', 'fruit', 'fruit')",
                ],
                "Unstable Matches Change": [
                    "('tomato', 'vegetable', 'fruit')",
                    "('tomahto', 'fruit', 'fruit')",
                ],
                "Added": ["('blueberry', 'berry', 'bush')"],
                "Deleted": ["('yellow', 'delicious', 'apple')"],
            }

            expected_df = pd.DataFrame(
                data=dict(
                    [(k, pd.Series(v)) for k, v in expected_data.items()]
                )
            )
            expected_dict = expected_df.to_dict()

            self.assertDictEqual(expected_dict, created_dict)
            self.assertTrue(expected_df.equals(created_df))

    def test_graph_difference_to_json(self):
        manager = Manager(
            excel_path=[
                DATA_DIRECTORY / "Composition Example.xlsx" for i in range(2)
            ],
            json_path=PATTERNS / "Composition.json",
        )
        tr = manager.translator
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            orig_edge = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            renm_source = DiEdge(
                source=Vertex(
                    name="Subaru",
                    id="_001",
                    original_name="Car",
                    original_id="_001",
                    node_types=["Atomic Thing"],
                ),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            orig_edge2 = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="Vehicle", id="_003"),
                edge_attribute="type",
            )
            renm_target = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(
                    name="vehicle",
                    id="_003",
                    original_name="Vehicle",
                    original_id="_003",
                    node_types=["Composite Thing"],
                ),
                edge_attribute="type",
            )
            orig_edge3 = DiEdge(
                source=Vertex(name="subaru", id="_004"),
                target=Vertex(name="Vehicle", id="_005"),
                edge_attribute="type",
            )
            renm_both = DiEdge(
                source=Vertex(
                    name="Subaru",
                    id="_004",
                    original_name="subaru",
                    original_id="_004",
                    node_types=["composite owner"],
                ),
                target=Vertex(
                    name="vehicle",
                    id="_005",
                    original_name="Vehicle",
                    original_id="_005",
                    node_types=["Atomic Thing"],
                ),
                edge_attribute="type",
            )
            orig_edge4 = DiEdge(
                source=Vertex(name="subaru", id="_004"),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            new_source = DiEdge(
                source=Vertex(
                    name="Subaru",
                    id=uuid.uuid4(),
                    node_types=["Composite Thing"],
                ),
                target=Vertex(name="car", id="_002"),
                edge_attribute="type",
            )
            orig_edge5 = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(name="Vehicle", id="_005"),
                edge_attribute="type",
            )
            new_target = DiEdge(
                source=Vertex(name="Car", id="_001"),
                target=Vertex(
                    name="vehicle",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                edge_attribute="type",
            )
            orig_edge6 = DiEdge(
                source=Vertex(name="Car", id="_007"),
                target=Vertex(name="Vehicle", id="_005"),
                edge_attribute="type",
            )
            new_sub = Vertex(
                name="Subaru", id=uuid.uuid4(), node_types=["Composite Thing"]
            )
            sub_cons = {
                "successors": [
                    {
                        "source": "Subaru",
                        "target": "Car",
                        "edge_attribute": "type",
                    }
                ]
            }
            new_sub.successrs = sub_cons
            new_both = DiEdge(
                source=Vertex(
                    name="Subaru",
                    id=uuid.uuid4(),
                    node_types=["Composite Thing"],
                ),
                target=Vertex(
                    name="vehicle",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                edge_attribute="type",
            )
            added_edge = DiEdge(
                source=Vertex(
                    name="New Source",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                target=Vertex(
                    name="New Target",
                    id=uuid.uuid4(),
                    node_types=["Atomic Thing"],
                ),
                edge_attribute="newEdge",
            )
            del_edge = DiEdge(
                source=Vertex(name="Old Source", id="_010"),
                target=Vertex(name="Old Target", id="_011"),
                edge_attribute="oldEdge",
            )
            change_dict = {
                orig_edge: [renm_source],
                orig_edge2: [renm_target],
                orig_edge3: [renm_both],
                orig_edge4: [new_source],
                orig_edge5: [new_target],
                orig_edge6: [new_both],
                "Added": [added_edge],
                "Deleted": [del_edge],
            }

            changes = manager.graph_difference_to_json(
                change_dict=change_dict,
                evaluators="0-1",
                translator=tr,
                out_directory=tmpdir,
            )

            rename = 0
            replace = 0
            create = 0
            delete = 0
            fall_through_ops = []
            for item in changes:
                op = item["ops"][0]["op"]
                if op == "create":
                    create += 1
                elif op == "replace":
                    replace += 1
                elif op == "rename":
                    rename += 1
                elif op == "delete":
                    delete += 1
                else:
                    fall_through_ops.append(op)
            # expect 4 node Renames
            # expect 7 edge replaces (1 is from add edge)
            # expect 6 node creates
            # expect 1 delete
            assert (
                rename == 4 and replace == 7 and create == 6 and delete == 1
            )
            assert not fall_through_ops

    def tearDown(self):
        pass


class TestEvaluator(unittest.TestCase):
    # TODO: Make sure all additional graph objects that are desired are
    # created by the graph creation logic.
    # TODO: Test the PROCESS of some of these functions.

    def setUp(self):
        data = (PATTERNS / "Composition.json").read_text()
        data = json.loads(data)

        self.translator = MDTranslator(json_data=data)
        self.evaluator = Evaluator(
            excel_file=DATA_DIRECTORY / "Composition Example.xlsx",
            translator=self.translator,
        )

        data_dict = {
            "Component": [
                "Car",
                "Car",
                "Car",
                "Car",
                "Car",
                "Car",
                "Car",
                "Wheel",
                "Wheel",
                "Wheel",
                "Engine",
                "Engine",
                "Engine",
                "Engine",
                "Engine",
                "Engine",
            ],
            "Position": [
                "engine",
                "chassis",
                "driveshaft",
                "front passenger",
                "front driver",
                "rear passenger",
                "rear driver",
                "hub",
                "tire",
                "lug nut",
                "one",
                "two",
                "three",
                "four",
                "drive output",
                "mount",
            ],
            "Part": [
                "Engine",
                "Chassis",
                "Driveshaft",
                "Wheel",
                "Wheel",
                "Wheel",
                "Wheel",
                "Hub",
                "Tire",
                "Lug Nut",
                "Cylinder",
                "Cylinder",
                "Cylinder",
                "Cylinder",
                "Drive Output",
                "Mount",
            ],
        }
        self.evaluator.df = pd.DataFrame(data=data_dict)

    def test_sheets_to_dataframe(self):
        data = (PATTERNS / "Composition.json").read_text()
        data = json.loads(data)

        ex_f = DATA_DIRECTORY / "Composition Example Model Baseline.xlsx"
        translator = MDTranslator(json_data=data)
        evaluator = Evaluator(excel_file=ex_f, translator=translator)
        file_name = "Composition Example Model Baseline.xlsx"
        evaluator.sheets_to_dataframe(excel_file=DATA_DIRECTORY / file_name)
        columns_list = [col for col in evaluator.df.columns]
        self.assertListEqual(["Component", "Position", "Part"], columns_list)

        # 63 ids provided .
        self.assertEqual(63, len(evaluator.df_ids))

        data2 = (PATTERNS / "Composition.json").read_text()
        data2 = json.loads(data2)

        ex_f2 = DATA_DIRECTORY / "Composition Example 2 Model Changed.xlsx"
        tr2 = MDTranslator(json_data=data2)
        eval = Evaluator(excel_file=ex_f2, translator=tr2)

        self.assertFalse(eval.df_renames.empty)
        self.assertFalse(eval.df_ids.empty)

    def test_has_rename(self):
        data = (PATTERNS / "Composition.json").read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        excel_file = DATA_DIRECTORY / "Composition Example Model Changed.xlsx"
        evaluator = Evaluator(excel_file=excel_file, translator=translator)
        self.assertTrue(evaluator.has_rename)
        excel_no_rename = (
            DATA_DIRECTORY / "Composition Example Model Baseline.xlsx"
        )
        evaluator_no_rename = Evaluator(
            excel_file=excel_no_rename, translator=translator
        )
        self.assertFalse(evaluator_no_rename.has_rename)

    def test_rename_df_columns(self):
        # just need to test that the columns are as expected.
        # utils tests the two auxillary functions that rename df entries.
        expected_cols = ["Composite Thing", "component", "Atomic Thing"]
        self.evaluator.rename_df_columns()
        self.assertListEqual(expected_cols, list(self.evaluator.df.columns))
        self.assertEqual(set(), self.evaluator.root_node_attr_columns)

    def test_add_missing_columns(self):
        # TODO: explicitly check that the new columns are made.
        # TODO: remove reliance on excelfile data.
        # TODO: This is an incomplete test because it does not test for
        # the case of no space column to be created.
        evaluator = Evaluator(
            excel_file=DATA_DIRECTORY / "Composition Example.xlsx",
            translator=self.translator,
        )
        evaluator.translator.data["Pattern Graph Edges"].extend(
            [
                ["cardinal", "Atomic Thing", "owner"],
                ["Composite Thing", "component context", "type"],
                [
                    "A_composite owner_component-end1",
                    "A_composite owner_component",
                    "memberEnd",
                ],
            ]
        )

        data_dict = {
            "Composite Thing": ["Car", "Wheel", "Engine"],
            "component": ["chassis", "tire", "mount"],
            "Atomic Thing": ["Chassis", "Tire", "Mount"],
        }
        df = pd.DataFrame(data=data_dict)
        evaluator.df = df
        evaluator.rename_df_columns()
        expected_cols = {
            "Composite Thing",
            "component",
            "Atomic Thing",
            "composite owner",
            "A_composite owner_component",
            "cardinal",
            "component context",
            "A_composite owner_component-end1",
        }
        evaluator.add_missing_columns()

        self.assertSetEqual(expected_cols, set(evaluator.df.columns))

        expected_composite_owner = [
            "car qua chassis context",
            "wheel qua tire context",
            "engine qua mount context",
        ]
        expected_comp_owner_comp = [
            "A_car qua chassis context_chassis",
            "A_wheel qua tire context_tire",
            "A_engine qua mount context_mount",
        ]
        expect_cardinal = [
            "car cardinal",
            "wheel cardinal",
            "engine cardinal",
        ]
        expect_space_in_df = [
            "chassis qua context context",
            "tire qua context context",
            "mount qua context context",
        ]
        expect_dash = [
            "A_car qua chassis context_chassis-end1",
            "A_wheel qua tire context_tire-end1",
            "A_engine qua mount context_mount-end1",
        ]
        self.assertListEqual(
            expected_composite_owner, list(evaluator.df["composite owner"])
        )
        self.assertListEqual(
            expected_comp_owner_comp,
            list(evaluator.df["A_composite owner_component"]),
        )
        self.assertListEqual(expect_cardinal, list(evaluator.df["cardinal"]))
        self.assertListEqual(
            expect_space_in_df, list(evaluator.df["component context"])
        )
        self.assertListEqual(
            expect_dash,
            list(evaluator.df["A_composite owner_component-end1"]),
        )

    def test_to_property_di_graph(self):
        # the goal is to create a graph object.
        # networkx provides the functionality to get the data into the graph
        # the graph itself will be tested so I should just test that a graph
        # obj exists.
        # TODO: create tests for the properties on the Evaluator class.
        json_data = (PATTERNS / "Composition.json").read_text()
        json_data = json.loads(json_data)
        tr = MDTranslator(json_data=json_data)
        file = DATA_DIRECTORY / "Composition Example 2 Model partial_map.xlsx"
        evaluator = Evaluator(excel_file=file, translator=tr)
        df = evaluator.df
        df_ids = evaluator.df_ids
        df_renames = evaluator.df_renames
        evaluator.rename_df_columns()
        evaluator.add_missing_columns()
        evaluator.to_property_di_graph()
        pdg = evaluator.prop_di_graph

        for node in list(pdg):
            self.assertEqual(node, pdg.nodes[node][node].name)

        for edge in list(pdg.edges):
            source_edge = edge[0]
            target_edge = edge[1]
            pdg_edge = pdg.edges[edge]["diedge"]
            source_pdg = pdg_edge.named_edge_triple[0]
            target_pdg = pdg_edge.named_edge_triple[1]
            self.assertEqual(source_edge, source_pdg)
            self.assertEqual(target_edge, target_pdg)

    def tearDown(self):
        pass


class TestMDTranslator(unittest.TestCase):
    def setUp(self):
        # TODO: Note that this relies on Composition.json
        data = (PATTERNS / "Composition.json").read_text()
        data = json.loads(data)

        self.translator = MDTranslator(json_data=data)

    def test_get_root_node(self):
        root_node = "component"
        self.assertEqual(root_node, self.translator.get_root_node())

    def test_get_cols_to_nav_map(self):
        cols_to_nav = ["Component", "Part", "Position"]
        self.assertListEqual(
            cols_to_nav, list(self.translator.get_cols_to_nav_map().keys())
        )

    def test_MD_get_pattern_graph(self):
        data = (PATTERNS / "InterfaceDataFlow.json").read_text()
        data = json.loads(data)
        translator = MDTranslator(json_data=data)
        expect = {
            "A_CompA Context_CompA",
            "Comp A Context",
            "Comp A Context",
            "A_CompA Context_CompA",
            "A_CompA Context_CompA",
            "Comp A",
            "Comp A",
            "A_CompA Context_CompA",
            "Comp A",
            "Component A",
            "Comp A",
            "Context",
            "C_Outport_Inport-end1",
            "C_Outport_Inport",
            "C_Outport_Inport-end1",
            "Outport",
            "C_Outport_Inport",
            "C_Outport_Inport-end1",
            "Outport",
            "Component A",
            "Outport",
            "Common IF",
            "C_Outport_Inport",
            "Context",
            "Comp B",
            "Context",
            "A_CompB Context_CompB",
            "Comp B Context",
            "Comp B Context",
            "A_CompB Context_CompB",
            "A_CompB Context_CompB",
            "Comp B",
            "Comp B",
            "A_CompB Context_CompB",
            "Comp B",
            "Component B",
            "C_Outport_Inport-end2",
            "C_Outport_Inport",
            "C_Outport_Inport",
            "C_Outport_Inport-end2",
            "C_Outport_Inport-end2",
            "Inport",
            "Inport",
            "Component B",
            "Inport",
            "Common IF",
            "Flow",
            "Common IF",
            "Flow",
            "FlowType",
        }
        assert set(translator.get_pattern_graph()) == expect

    def test_get_pattern_graph_edges(self):
        node_pairs_list = self.translator.get_pattern_graph_edges()
        self.assertEqual(6, len(node_pairs_list))

    def test_get_edge_type(self):
        self.assertEqual("type", self.translator.get_edge_type(index=0))

    def test_get_uml_metatype(self):
        metatype = self.translator.get_uml_metatype(
            node_key="Composite Thing"
        )
        self.assertEqual("Class", metatype)

    def test_get_uml_stereotype(self):
        stereotype = self.translator.get_uml_stereotype(
            node_key="Composite Thing"
        )
        self.assertEqual("Block", stereotype)

        stereotype_2 = self.translator.get_uml_stereotype(
            node_key="composite owner"
        )
        self.assertEqual(None, stereotype_2)

    def test_get_uml_settings(self):
        path, setting = self.translator.get_uml_settings(
            node_key="Composite Thing"
        )
        self.assertTupleEqual(("Composite Thing", None), (path, setting))

        path_comp, setting_comp = self.translator.get_uml_settings(
            node_key="component"
        )
        self.assertEqual(
            ("aggregation", "composite"), (path_comp, setting_comp)
        )

    def tearDown(self):
        pass
