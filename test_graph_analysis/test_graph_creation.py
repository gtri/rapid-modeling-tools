import unittest
import os
import json
import pandas as pd

from graph_analysis.graph_creation import (Manager, Evaluator, MDTranslator)
from graph_analysis.graph_objects import DiEdge, PropertyDiGraph, Vertex
from graph_analysis.utils import object_dict_view


DATA_DIRECTORY = '../data/'


# class TestProduceJson(unittest.TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_json_creation(self):
#         manager = Manager(excel_path=[os.path.join(
#             DATA_DIRECTORY, 'Sample Equations.xlsx')],
#             json_path=os.path.join(DATA_DIRECTORY,
#                                    'ParametricGraphMaster.json'))
#         translator = manager.translator
#         evaluator = manager.evaluators[0]
#         evaluator.rename_df_columns()
#         evaluator.add_missing_columns()
#         evaluator.to_property_di_graph()
#         property_di_graph = evaluator.prop_di_graph
#         property_di_graph.create_vertex_set(
#             df=evaluator.df, root_node_type=translator.get_root_node())
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
#     def test_change_excel_json_creation(self):
#         excel_files = [os.path.join(DATA_DIRECTORY,
#                                     'Composition Example Model Baseline.xlsx'),
#                        os.path.join(DATA_DIRECTORY,
#                                     'Composition Example Model Changed.xlsx')]
#         manager = Manager(excel_path=excel_files,
#                           json_path=os.path.join(DATA_DIRECTORY,
#                                                  'CompositionGraphMaster.json')
#                           )
#
#         translator = manager.translator
#         for evaluator in manager.evaluators:
#             evaluator.rename_df_columns()
#             evaluator.add_missing_columns()
#             evaluator.to_property_di_graph()
#             property_di_graph = evaluator.prop_di_graph
#             property_di_graph.create_vertex_set(
#                 df=evaluator.df, translator=translator)
#             property_di_graph.create_edge_set()
#             vertex_set = property_di_graph.vertex_set
#
#         manager.get_pattern_graph_diff()
#         manager.changes_to_excel()
#
#     def tearDown(self):
#         pass


class TestManager(unittest.TestCase):

    def setUp(self):
        # instead of making objects that go through all these tests
        # make the data the instance variables that I can access to make
        # instances of the classes locally within the function scope.
        self.manager = Manager(
            excel_path=[os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx')
                for i in range(2)],
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
        self.assertEqual(2, len(self.manager.evaluators))
        for eval in self.manager.evaluators:
            self.assertIsInstance(eval, Evaluator)

    def test_get_pattern_graph_diff(self):
        # this is a bad function and an improper test.
        # The test ignores the obvious problem of non-unique matchings
        manager = Manager(
            excel_path=[os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx')
                for i in range(2)],
            json_path=os.path.join(DATA_DIRECTORY,
                                   'CompositionGraphMaster.json'))
        base_inputs = [('s1', 't1', 'type'),
                       ('s12', 't12', 'memberEnd'),
                       ('song', 'tiger', 'blue'), ]
        base_df = pd.DataFrame(data={
            'source': ['s1', 's12', 'song'],
            'target': [edge[1] for edge in base_inputs],
            'type': ['type' for i in range(3)],
            'memberEnd': ['memberEnd' for i in range(3)],
            'blue': ['blue' for i in range(3)]
        })

        ancestor = [('as1', 't1', 'type'),
                    ('s12', 'at12', 'memberEnd'), ('b', 'c', 'orange')]

        base_edges = []
        base_dict = {}
        ancestor_edges = []
        ancestor_dict = {}

        for edge_tuple in base_inputs:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            base_dict[edge_tuple] = edge
            base_edges.append(edge)

        for edge_tuple in ancestor:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            ancestor_dict[edge_tuple] = edge
            ancestor_edges.append(edge)

        manager.evaluators[0].df = base_df
        manager.evaluators[0].prop_di_graph = PropertyDiGraph()
        manager.evaluators[1].prop_di_graph = PropertyDiGraph()
        manager.evaluators[0].prop_di_graph.edge_set = set(base_edges)
        manager.evaluators[1].prop_di_graph.edge_set = set(ancestor_edges)
        manager.evaluators[0].prop_di_graph.edge_dict = base_dict
        manager.evaluators[1].prop_di_graph.edge_dict = ancestor_dict
        df_data = {'new name': ['at12'],
                   'old name': ['t12']}
        msg = ('Broke the new as old fn because it wants to receive a dict'
               + ' of new_name: old_name and not a list or something else.')
        self.assertFalse(True, msg='Broke the new as old fn because it wants')
        manager.evaluators[1].df_renames = pd.DataFrame(data=df_data)
        self.assertTrue(manager.evaluators[1].has_rename)

        match_dict = manager.get_pattern_graph_diff()

        match_dict_str = {}
        added_to_str = []
        deleted_to_str = []
        add_del = ('Added', 'Deleted')
        for key in match_dict['0-1']['Changes']:
            if key not in add_del:
                if not match_dict['0-1']['Changes'][key]:
                    no_match_to_str.append(key.named_edge_triple)
                    continue
                try:
                    key_trip = key.named_edge_triple
                    val_trip = match_dict[
                        '0-1']['Changes'][key][0].named_edge_triple
                    match_dict_str.update({key_trip: val_trip})
                except AttributeError:
                    key_vert = key
                    val_vert = match_dict[
                        '0-1']['Changes'][key]
                    print(key_vert, val_vert)
                    match_dict_str.update({key_vert: val_vert})

        for value in match_dict['0-1']['Changes']['Added']:
            added_to_str.append(value.named_edge_triple)
        for value in match_dict['0-1']['Changes']['Deleted']:
            deleted_to_str.append(value.named_edge_triple)

        match_dict_str.update({'Added': added_to_str,
                               'Deleted': deleted_to_str})

        expected_matches = {('s1', 't1', 'type'): ('as1', 't1', 'type'),
                            't12': 'at12',
                            'Added': [('b', 'c', 'orange'), ],
                            'Deleted': [('song', 'tiger', 'blue'), ], }
        self.assertDictEqual(expected_matches, match_dict_str)

    def test_changes_to_excel(self):
        manager = Manager(
            excel_path=[os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx')
                for i in range(1)],
            json_path=os.path.join(DATA_DIRECTORY,
                                   'CompositionGraphMaster.json'))
        og_edge = DiEdge(source=Vertex(name='green'),
                         target=Vertex(name='apple'),
                         edge_attribute='fruit')
        change_edge = DiEdge(source=Vertex(name='gala'),
                             target=Vertex(name='apple'),
                             edge_attribute='fruit')
        added_edge = DiEdge(source=Vertex(name='blueberry'),
                            target=Vertex(name='berry'),
                            edge_attribute='bush')
        deleted_edge = DiEdge(source=Vertex(name='yellow'),
                              target=Vertex(name='delicious'),
                              edge_attribute='apple')
        unstable_key = DiEdge(source=Vertex(name='tomato'),
                              target=Vertex(name='fruit'),
                              edge_attribute='fruit')
        unstable_one = DiEdge(source=Vertex(name='tomato'),
                              target=Vertex(name='vegetable'),
                              edge_attribute='fruit')
        unstable_two = DiEdge(source=Vertex(name='tomahto'),
                              target=Vertex(name='fruit'),
                              edge_attribute='fruit')

        fake_datas = {'0-1': {'Changes': {'Added': [added_edge],
                                          'Deleted': [deleted_edge],
                                          og_edge: [change_edge],
                                          't12': 'at12', },
                              'Unstable Pairs': {unstable_key: [
                                  unstable_one,
                                  unstable_two]}}}
        manager.evaluator_change_dict = fake_datas
        manager.changes_to_excel()
        created_file_name = 'Graph Model Differences.xlsx'
        created_file = os.path.join(DATA_DIRECTORY, created_file_name)
        created_df = pd.read_excel(created_file)
        created_dict = created_df.to_dict()

        expected_data = {'Edit 1': ["('green', 'apple', 'fruit')",
                                    "t12",
                                    "('tomato', 'fruit', 'fruit')",
                                    "('tomato', 'fruit', 'fruit')", ],
                         'Edit 2': ["('gala', 'apple', 'fruit')",
                                    "at12",
                                    "('tomato', 'vegetable', 'fruit')",
                                    "('tomahto', 'fruit', 'fruit')", ],
                         'Added': ["('blueberry', 'berry', 'bush')"],
                         'Deleted': ["('yellow', 'delicious', 'apple')"]}

        expected_df = pd.DataFrame(data=dict([
            (k, pd.Series(v)) for k, v in expected_data.items()]))
        expected_dict = expected_df.to_dict()

        self.assertDictEqual(expected_dict, created_dict)
        self.assertTrue(expected_df.equals(created_df))

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

    def test_sheets_to_dataframe(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        translator = MDTranslator(json_data=data)
        evaluator = Evaluator(
            excel_file=os.path.join(DATA_DIRECTORY,
                                    'Composition Example Model Baseline.xlsx'),
            translator=translator
        )
        file_name = 'Composition Example Model Baseline.xlsx'
        evaluator.sheets_to_dataframe(excel_file=os.path.join(DATA_DIRECTORY,
                                                              file_name))
        columns_list = [col for col in evaluator.df.columns]
        self.assertListEqual(
            ['Component', 'Position', 'Part'], columns_list)

        # 63 ids provided and 1 key for the new_i counter ids.
        self.assertEqual(64, len(translator.uml_id))

    def test_has_rename(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        translator = MDTranslator(json_data=data)
        evaluator = Evaluator(
            excel_file=os.path.join(DATA_DIRECTORY,
                                    'Composition Example Model Changed.xlsx'),
            translator=translator
        )
        self.assertTrue(evaluator.has_rename)
        evaluator_no_rename = Evaluator(
            excel_file=os.path.join(DATA_DIRECTORY,
                                    'Composition Example Model Baseline.xlsx'),
            translator=translator
        )
        self.assertFalse(evaluator_no_rename.has_rename)

    def test_rename_df_columns(self):
        # just need to test that the columns are as expected.
        # utils tests the two auxillary functions that rename df entries.
        expected_cols = ['Composite Thing',
                         'component',
                         'Atomic Thing',
                         ]
        self.evaluator.rename_df_columns()
        self.assertListEqual(expected_cols, list(self.evaluator.df.columns))
        self.assertEqual(set(), self.evaluator.root_node_attr_columns)

    def test_add_missing_columns(self):
        # TODO: explicitly check that the new columns are made.
        # TODO: remove reliance on excelfile data.
        # TODO: This is an incomplete test because it does not test for
        # the case of no space column to be created.
        evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            translator=self.translator)
        evaluator.translator.get_pattern_graph().append('cardinal')
        evaluator.translator.get_pattern_graph().append('component context')
        evaluator.translator.get_pattern_graph().append(
            'A_composite owner_component-end1'
        )
        # self.assertTrue(False, msg='Extend this to get the if case in space')
        data_dict = {
            'Composite Thing': ['Car', 'Wheel', 'Engine'],
            'component': ['chassis', 'tire', 'mount'],
            'Atomic Thing': ['Chassis', 'Tire', 'Mount']
        }
        df = pd.DataFrame(data=data_dict)
        evaluator.df = df
        evaluator.rename_df_columns()
        expected_cols = {'Composite Thing',
                         'component',
                         'Atomic Thing',
                         'composite owner',
                         'A_composite owner_component',
                         'cardinal',
                         'component context',
                         'A_composite owner_component-end1', }
        evaluator.add_missing_columns()

        self.assertSetEqual(expected_cols, set(evaluator.df.columns))

        expected_composite_owner = ['car qua chassis context',
                                    'wheel qua tire context',
                                    'engine qua mount context']
        expected_comp_owner_comp = ['A_car qua chassis context_chassis',
                                    'A_wheel qua tire context_tire',
                                    'A_engine qua mount context_mount']
        expect_cardinal = ['car cardinal', 'wheel cardinal',
                           'engine cardinal']
        expect_space_in_df = ['chassis qua context context',
                              'tire qua context context',
                              'mount qua context context']
        expect_dash = ['A_car qua chassis context_chassis-end1',
                       'A_wheel qua tire context_tire-end1',
                       'A_engine qua mount context_mount-end1']
        self.assertListEqual(expected_composite_owner,
                             list(evaluator.df['composite owner']))
        self.assertListEqual(expected_comp_owner_comp,
                             list(evaluator.df[
                                 'A_composite owner_component']))
        self.assertListEqual(expect_cardinal,
                             list(evaluator.df['cardinal']))
        self.assertListEqual(expect_space_in_df,
                             list(evaluator.df['component context']))
        self.assertListEqual(expect_dash,
                             list(evaluator.df[
                                 'A_composite owner_component-end1']))

    def test_to_property_di_graph(self):
        # the goal is to create a graph object.
        # networkx provides the functionality to get the data into the graph
        # the graph itself will be tested so I should just test that a graph
        # obj exists.
        # self.evaluator.rename_df_columns()
        # self.evaluator.add_missing_columns()
        # self.evaluator.to_property_di_graph()
        # self.assertTrue(self.evaluator.prop_di_graph)
        # self.assertIsInstance(self.evaluator.prop_di_graph,
        #                       PropertyDiGraph)

        # TODO: create tests for the properties on the Evaluator class.
        data_dict = {
            'Composite Thing': ['blueberry', ],
            'component': ['pie', ],
            'Atomic Thing': ['milk']
        }
        data_id_dict = {
            'Element Names': ['blueberry', 'pie', 'milk'],
            'ID': [123, 234, 345]
        }
        evaluator = Evaluator(excel_file=os.path.join(
            DATA_DIRECTORY,
            'Composition Example Model Baseline.xlsx'),
            translator=self.translator)
        evaluator.df = pd.DataFrame(data=data_dict)
        df_ids = pd.DataFrame(data=data_id_dict)
        df_ids.set_index(df_ids.columns[0], inplace=True)
        evaluator.df_ids = df_ids
        evaluator.translator.uml_id.update(
            evaluator.df_ids.to_dict(
                orient='dict')[evaluator.df_ids.columns[0]]
        )
        evaluator.rename_df_columns()
        evaluator.add_missing_columns()
        evaluator.to_property_di_graph()

        graph_node_data = list(evaluator.prop_di_graph.nodes().data())
        expected_node_ids = [('blueberry qua pie context', {'ID': 'new_0'}),
                             ('blueberry', {'ID': 123}),
                             ('pie', {'ID': 234}),
                             ('milk', {'ID': 345}),
                             ('A_blueberry qua pie context_pie',
                              {'ID': 'new_1'})]

        self.assertListEqual(expected_node_ids, graph_node_data)

    def tearDown(self):
        pass


class TestMDTranslator(unittest.TestCase):

    def setUp(self):
        # TODO: Note that this relies on CompositionGraphMaster.json
        with open(os.path.join(DATA_DIRECTORY,
                               'CompositionGraphMaster.json')) as f:
            data = json.load(f)

        self.translator = MDTranslator(json_data=data)

    def test_get_root_node(self):
        root_node = 'component'
        self.assertEqual(root_node, self.translator.get_root_node())

    def test_get_cols_to_nav_map(self):
        cols_to_nav = ['Component', 'Position', 'Part']
        self.assertListEqual(
            cols_to_nav, list(self.translator.get_cols_to_nav_map().keys()))

    def test_get_pattern_graph(self):
        pattern_graph = ['Composite Thing',
                         'Atomic Thing',
                         'A_composite owner_component',
                         'composite owner',
                         'component']
        self.assertListEqual(pattern_graph,
                             self.translator.get_pattern_graph())

    def test_get_pattern_graph_edges(self):
        node_pairs_list = self.translator.get_pattern_graph_edges()
        self.assertEqual(6, len(node_pairs_list))

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
