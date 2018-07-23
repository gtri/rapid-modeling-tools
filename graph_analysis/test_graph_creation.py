import unittest
import os
import json

from graph_creation import (Manager, Evaluator)
from graph_objects import PropertyDiGraph


DATA_DIRECTORY = '../data/'


# class TestProduceJson(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_json_creation(self):
#         manager = Manager(excel_path=[os.path.join(
#             DATA_DIRECTORY, 'Composition Example.xlsx')],
#             json_path=os.path.join(DATA_DIRECTORY,
#                                    'CompositionGraphMaster.json'))
#         manager.get_json_data()
#         manager.create_evaluators()
#         manager.evaluators[0].rename_excel_columns()
#         manager.evaluators[0].add_missing_columns()
#         manager.evaluators[0].to_property_di_graph()
#         manager.evaluators[0].prop_di_graph.create_vertex_set(
#             df=manager.evaluators[0].df)
#         vert_set = manager.evaluators[0].prop_di_graph.vertex_set
#         json_out = {'modification targets': []}
#         edge_json = []
#         for vertex in vert_set:
#             vert_uml, edge_uml = vertex.to_uml_json()
#             json_out['modification targets'].extend(vert_uml)
#             edge_json.extend(edge_uml)
#
#         json_out['modification targets'].extend(edge_json)
#         with open(os.path.join(DATA_DIRECTORY,
#                                'changes_uml.json'), 'w') as outfile:
#             json.dump(json_out, outfile, indent=4)
#
#     def tearDown(self):
#         pass


class TestManager(unittest.TestCase):

    def setUp(self):
        self.manager = Manager(
            excel_path=[os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx')
                for i in range(3)],
            json_path=os.path.join(DATA_DIRECTORY,
                                   'CompositionGraphMaster.json'))

    def test_get_json_data(self):
        self.manager.get_json_data()
        expected_keys = ['Columns to Navigation Map',
                         'Pattern Graph Vertices',
                         'Pattern Graph Edge Labels',
                         'Pattern Graph Edges',
                         'Pattern Spanning Tree Edges',
                         'Pattern Spanning Tree Edge Labels',
                         'Root Node',
                         'Vertex MetaTypes']

        self.assertListEqual(expected_keys, list(
            self.manager.json_data.keys()))

    def test_create_evaluators(self):
        # weak test
        self.manager.create_evaluators()
        self.assertEqual(3, len(self.manager.evaluators))
        for eval in self.manager.evaluators:
            self.assertIsInstance(eval, Evaluator)

    def tearDown(self):
        pass


class TestEvaluator(unittest.TestCase):
    # TODO: Make sure all additional graph objects that are desired are
    # created by the graph creation logic.
    # TODO: Test the PROCESS of some of these functions.

    def setUp(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        self.evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            json_data=data)

    def test_rename_excel_columns(self):
        # just need to test that the columns are as expected.
        # utils tests the two auxillary functions that rename df entries.
        expected_cols = ['Composite Thing',
                         'component',
                         'Atomic Thing',
                         ]
        self.evaluator.rename_excel_columns()
        self.assertListEqual(expected_cols, list(self.evaluator.df.columns))

    def test_add_missing_columns(self):
        # TODO: explicitly check that the new columns are made.
        self.evaluator.rename_excel_columns()
        expected_cols = {'Composite Thing',
                         'component',
                         'Atomic Thing',
                         'composite owner',
                         'A_"composite owner"_component'}
        self.evaluator.add_missing_columns()
        self.assertSetEqual(expected_cols, set(self.evaluator.df.columns))
        comp_owner = list(self.evaluator.df['composite owner'])
        a_comp_comp = list(self.evaluator.df['A_"composite owner"_component'])
        expected_comp_owner = ['car qua engine context',
                               'car qua chassis context',
                               'car qua driveshaft context',
                               'car qua front passenger context',
                               'car qua front driver context',
                               'car qua rear passenger context',
                               'car qua rear driver context',
                               'wheel qua hub context',
                               'wheel qua tire context',
                               'wheel qua lug nut context',
                               'engine qua one context',
                               'engine qua two context',
                               'engine qua three context',
                               'engine qua four context',
                               'engine qua drive output context',
                               'engine qua mount context']
        expected_a_comp_comp = ['A_car_engine',
                                'A_car_chassis',
                                'A_car_driveshaft',
                                'A_car_front passenger',
                                'A_car_front driver',
                                'A_car_rear passenger',
                                'A_car_rear driver',
                                'A_wheel_hub',
                                'A_wheel_tire',
                                'A_wheel_lug nut',
                                'A_engine_one',
                                'A_engine_two',
                                'A_engine_three',
                                'A_engine_four',
                                'A_engine_drive output',
                                'A_engine_mount']
        self.assertListEqual(expected_comp_owner, comp_owner)
        self.assertListEqual(expected_a_comp_comp, a_comp_comp)

    def test_to_property_di_graph(self):
        # the goal is to create a graph object.
        # networkx provides the functionality to get the data into the graph
        # the graph itself will be tested so I should just test that a graph
        # obj exists.
        self.evaluator.rename_excel_columns()
        self.evaluator.add_missing_columns()
        self.evaluator.to_property_di_graph()
        self.assertTrue(self.evaluator.prop_di_graph)
        self.assertIsInstance(self.evaluator.prop_di_graph,
                              PropertyDiGraph)

        # TODO: create tests for the properties on the Evaluator class.

    def tearDown(self):
        pass
