import unittest
import os
import json
import pandas as pd

from graph_creation import (Manager, Evaluator, MDTranslator)
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
#         translator = manager.translator
#         evaluator = manager.evaluators[0]
#         evaluator.rename_columns()
#         evaluator.add_missing_columns()
#         evaluator.to_property_di_graph()
#         property_di_graph = evaluator.prop_di_graph
#         property_di_graph.create_vertex_set(
#             df=evaluator.df)
#         vert_set = property_di_graph.vertex_set
#         json_out = {'modification targets': []}
#         edge_json = []
#         for vertex in vert_set:
#             vert_uml, edge_uml = vertex.to_uml_json(translator=translator)
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
        expected_keys = ['Columns to Navigation Map',
                         'Pattern Graph Vertices',
                         'Pattern Graph Edge Labels',
                         'Pattern Graph Edges',
                         'Pattern Spanning Tree Edges',
                         'Pattern Spanning Tree Edge Labels',
                         'Root Node',
                         'Vertex MetaTypes',
                         'Vertex Stereotypes',
                         'Vertex Settings']

        self.assertListEqual(expected_keys, list(
            self.manager.json_data.keys()))

    def test_create_evaluators(self):
        # weak test: create_evaluators() run during init
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

        self.translator = MDTranslator(json_data=data)
        self.evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            translator=self.translator)

        data_dict = {
            'Component': ['Car', 'Car', 'Car', 'Car', 'Car', 'Car',
                          'Car', 'Wheel', 'Wheel', 'Wheel', 'Engine',
                          'Engine', 'Engine', 'Engine', 'Engine', 'Engine', ],
            'Position': ['engine', 'chassis', 'driveshaft', 'front passenger',
                         'front driver', 'rear passenger', 'rear driver',
                         'hub', 'tire', 'lug nut', 'one', 'two', 'three',
                         'four', 'drive output', 'mount'],
            'Part': ['Engine', 'Chassis', 'Driveshaft', 'Wheel', 'Wheel',
                     'Wheel', 'Wheel', 'Hub', 'Tire', 'Lug Nut', 'Cylinder',
                     'Cylinder', 'Cylinder', 'Cylinder', 'Drive Output',
                     'Mount']
        }
        self.evaluator.df = pd.DataFrame(data=data_dict)

    def test_rename_columns(self):
        # just need to test that the columns are as expected.
        # utils tests the two auxillary functions that rename df entries.
        expected_cols = ['Composite Thing',
                         'component',
                         'Atomic Thing',
                         ]
        self.evaluator.rename_columns()
        self.assertListEqual(expected_cols, list(self.evaluator.df.columns))

    def test_add_missing_columns(self):
        # TODO: explicitly check that the new columns are made.
        # TODO: remove reliance on excelfile data.
        self.evaluator.rename_columns()
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
        self.evaluator.rename_columns()
        self.evaluator.add_missing_columns()
        self.evaluator.to_property_di_graph()
        self.assertTrue(self.evaluator.prop_di_graph)
        self.assertIsInstance(self.evaluator.prop_di_graph,
                              PropertyDiGraph)

        # TODO: create tests for the properties on the Evaluator class.

    def tearDown(self):
        pass


class TestMDTranslator(unittest.TestCase):

    def setUp(self):
        # TODO: Note that this relies on CompositionGraphMaster.json
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        self.translator = MDTranslator(json_data=data)

    def get_pattern_graph(self):
        pattern_graph = ['Composite Thing',
                         'Atomic Thing',
                         'A_\"compsoite owner\"_component',
                         'composite owner',
                         'component']
        self.assertListEqual(pattern_graph,
                             self.translator.get_pattern_graph())

    def get_pattern_graph_edges(self):
        node_pairs_list = self.translator.get_pattern_graph_edges().keys()
        self.assertEqual(6, node_pairs_list)

    def test_get_edge_type(self):
        self.assertEqual('type', self.translator.get_edge_type(index=0))

    def test_get_uml_metatype(self):
        metatype = self.translator.get_uml_metatype(
            node_key='Composite Thing')
        self.assertEqual('Class', metatype)

    def test_get_uml_stereotype(self):
        stereotype = self.translator.get_uml_stereotype(
            node_key='Composite Thing'
        )
        self.assertEqual('Block', stereotype)

        stereotype_2 = self.translator.get_uml_stereotype(
            node_key='composite owner'
        )
        self.assertEqual(None, stereotype_2)

    def test_get_uml_settings(self):
        path, setting = self.translator.get_uml_settings(
            node_key='Composite Thing'
        )
        self.assertTupleEqual(('Composite Thing', None), (path, setting))

        path_comp, setting_comp = self.translator.get_uml_settings(
            node_key='component'
        )
        self.assertEqual(('aggregation', 'composite'),
                         (path_comp, setting_comp))

    def tearDown(self):
        pass
