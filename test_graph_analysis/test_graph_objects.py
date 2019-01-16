import json
import unittest
from pathlib import Path

import networkx as nx
import pandas as pd

from graph_analysis.graph_creation import Evaluator, MDTranslator
from graph_analysis.graph_objects import (DiEdge, PropertyDiGraph, Vertex,
                                          create_vertex_objects)
from graph_analysis.utils import create_column_values

from . import DATA_DIRECTORY, OUTPUT_DIRECTORY, PATTERNS


class TestPropertyDiGraph(unittest.TestCase):

    def setUp(self):
        data = (PATTERNS / 'Composition.json').read_text(
        )
        data = json.loads(data)

        self.translator = MDTranslator(json_data=data)

        # Create Baby dataset to deal with manual checking
        data_dict = {'Composite Thing': ['Car', 'Car',
                                         'Wheel', 'Engine'],
                     'component': ['engine', 'rear driver',
                                   'hub', 'drive output'],
                     'Atomic Thing': ['Engine', 'Wheel',
                                      'Hub', 'Drive Output']}
        df = pd.DataFrame(data=data_dict)
        self.evaluator = Evaluator(excel_file=(
            DATA_DIRECTORY / 'Composition Example.xlsx'),
            translator=self.translator)
        self.evaluator.df = df
        self.evaluator.rename_df_columns()
        self.evaluator.add_missing_columns()
        self.evaluator.to_property_di_graph()
        self.Graph = self.evaluator.prop_di_graph

    def test_named_vertex_set(self):
        expect_vert_set = {'car qua engine context', 'Car',
                           'car qua rear driver context', 'Wheel',
                           'engine qua drive output context', 'Engine',
                           'engine', 'rear driver', 'hub', 'Hub',
                           'drive output', 'Drive Output',
                           'A_car qua engine context_engine',
                           'A_car qua rear driver context_rear driver',
                           'A_wheel qua hub context_hub',
                           'A_engine qua drive output context_drive output',
                           'wheel qua hub context'}
        self.Graph.create_vertex_set(
            df=self.evaluator.df,
            translator=self.translator)
        self.assertSetEqual(expect_vert_set, self.Graph.named_vertex_set)

    def test_create_vertex_set(self):
        # idea is to check that the vertex_set contains the vert objects expect
        # check that each element in the vertex_set is a vertex object and
        # then check their names.
        expect_vert_set = {'car qua engine context', 'Car',
                           'car qua rear driver context', 'Wheel',
                           'engine qua drive output context', 'Engine',
                           'engine', 'rear driver', 'hub', 'Hub',
                           'drive output', 'Drive Output',
                           'A_car qua engine context_engine',
                           'A_car qua rear driver context_rear driver',
                           'A_wheel qua hub context_hub',
                           'A_engine qua drive output context_drive output',
                           'wheel qua hub context'}
        self.Graph.create_vertex_set(
            df=self.evaluator.df,
            translator=self.translator)
        for vertex in self.Graph.vertex_set:
            self.assertIsInstance(vertex, Vertex)
            self.assertIn(vertex.name, expect_vert_set)

        dict_keys_set = set(self.Graph.vertex_dict.keys())
        self.assertSetEqual(expect_vert_set, dict_keys_set)

    def test_create_edge_set(self):
        # check each element of edge_set is infact a DiEdge then that it should
        # be an edge at all.
        # TODO: Find a way to use the self.Graph.edges tuples with the
        # edge attr because these show up as source, targ.
        translator = self.translator
        self.Graph.create_vertex_set(df=self.evaluator.df,
                                     translator=self.translator)
        self.Graph.create_edge_set()
        data_dict = {'Composite Thing': ['Car', 'Car',
                                         'Wheel', 'Engine'],
                     'component': ['engine', 'rear driver',
                                   'hub', 'drive output'],
                     'Atomic Thing': ['Engine', 'Wheel',
                                      'Hub', 'Drive Output']}
        expected_edge_set = {('car qua engine context', 'Car', 'type'),
                             ('car qua rear driver context', 'Car', 'type'),
                             ('wheel qua hub context', 'Wheel', 'type'),
                             ('engine qua drive output context', 'Engine',
                              'type'),
                             ('engine', 'Engine', 'type'),
                             ('rear driver', 'Wheel', 'type'),
                             ('hub', 'Hub', 'type'),
                             ('drive output', 'Drive Output', 'type'),
                             ('A_car qua rear driver context_rear driver',
                              'car qua rear driver context',
                              'memberEnd'),
                             ('A_car qua engine context_engine',
                              'car qua engine context', 'memberEnd'),
                             ('A_wheel qua hub context_hub',
                              'wheel qua hub context',
                              'memberEnd'),
                             ('A_engine qua drive output context_drive output',
                              'engine qua drive output context', 'memberEnd'),
                             ('A_car qua engine context_engine', 'engine',
                              'memberEnd'),
                             ('A_car qua rear driver context_rear driver',
                              'rear driver', 'memberEnd'),
                             ('A_wheel qua hub context_hub', 'hub',
                              'memberEnd'),
                             ('A_engine qua drive output context_drive output',
                              'drive output', 'memberEnd'),
                             ('engine', 'Car', 'owner'),
                             ('rear driver', 'Car', 'owner'),
                             ('hub', 'Wheel', 'owner'),
                             ('drive output', 'Engine', 'owner'),
                             ('engine qua drive output context',
                              'A_engine qua drive output context_drive output',
                              'owner'),
                             ('car qua rear driver context',
                              'A_car qua rear driver context_rear driver',
                              'owner'),
                             ('wheel qua hub context',
                              'A_wheel qua hub context_hub', 'owner'),
                             ('engine qua drive output context',
                              'A_engine qua drive output context_drive output',
                              'owner'),
                             ('car qua engine context',
                              'A_car qua engine context_engine',
                              'owner')
                             }
        for edge in self.Graph.edge_set:
            self.assertIsInstance(edge, DiEdge)
            self.assertIn(edge.named_edge_triple, expected_edge_set)

    def test_create_vertex_objects(self):
        # This also tests the Vertex.to_dict() method in a round about way
        data_dict = {'Component': ['Car', 'engine'],
                     'Position': ['engine', 'Car'],
                     'edge type': ['owner', 'type']}
        test_graph_df = pd.DataFrame(data=data_dict)
        Test_Graph = nx.DiGraph()
        Temp_Graph = nx.DiGraph()
        Temp_Graph = nx.from_pandas_edgelist(
            df=test_graph_df, source='Component',
            target='Position', edge_attr='edge type',
            create_using=Temp_Graph)
        edge_label_dict = {'edge type': 'owner'}
        Test_Graph.add_nodes_from(Temp_Graph)
        Test_Graph.add_edge('Car', 'engine', edge_attribute='owner')
        Test_Graph.add_edge('engine', 'Car',
                            edge_attribute='type')

        vertices = create_vertex_objects(
            df=test_graph_df, graph=Test_Graph)

        vertex_1_dict = {'name': 'Car',
                         'node types': {'Component', 'Position'},
                         'successors': {'engine': {'edge_attribute': 'owner'}},
                         'predecessors': {'engine':
                                          {'edge_attribute': 'type'}},
                         'attributes': None}

        vertex_2_dict = {'name': 'engine',
                         'node types': {'Component', 'Position'},
                         'successors': {'Car': {'edge_attribute': 'type'}},
                         'predecessors': {'Car': {'edge_attribute': 'owner'}},
                         'attributes': None}

        vertex_dicts = [vertex_1_dict, vertex_2_dict]

        for index, vertex in enumerate(vertices):
            self.assertDictEqual(vertex_dicts[index], vertex.to_dict())

    def tearDown(self):
        pass


class TestVertex(unittest.TestCase):

    def setUp(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        self.translator = MDTranslator(json_data=data)

    def test_connections(self):
        data_dict = {'component': ['Car', 'engine'],
                     'Atomic Thing': ['engine', 'Car'],
                     'edge type': ['owner', 'type']}
        test_graph_df = pd.DataFrame(data=data_dict)
        Test_Graph = nx.DiGraph()
        Temp_Graph = nx.DiGraph()
        Temp_Graph = nx.from_pandas_edgelist(
            df=test_graph_df, source='component',
            target='Atomic Thing', edge_attr='edge type',
            create_using=Temp_Graph)
        edge_label_dict = {'edge type': 'owner'}
        Test_Graph.add_nodes_from(Temp_Graph)
        Test_Graph.add_edge('Car', 'engine', edge_attribute='owner')
        Test_Graph.add_edge('engine', 'Car',
                            edge_attribute='type')

        verticies = create_vertex_objects(
            df=test_graph_df, graph=Test_Graph)

        vertex_1_connections = [{'source': 'Car',
                                 'target': 'engine',
                                 'edge_attribute': 'owner'},
                                {'source': 'engine',
                                 'target': 'Car',
                                 'edge_attribute': 'type'}]
        vertex_2_connections = [{'source': 'engine',
                                 'target': 'Car',
                                 'edge_attribute': 'type'},
                                {'source': 'Car',
                                 'target': 'engine',
                                 'edge_attribute': 'owner'}]
        vertex_connections_dict = {0: vertex_1_connections,
                                   1: vertex_2_connections}
        for index, vertex in enumerate(verticies):
            self.assertListEqual(
                vertex_connections_dict[index], vertex.connections)

    def test_vertex_to_dict(self):
        # This also tests the Vertex.to_dict() method in a round about way
        vertex_car = Vertex(
            name='Car',
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )
        car_dict = vertex_car.to_dict()
        expected_dict = {
            'name': 'Car',
            'node types': ['Atomic Thing', 'Composite Thing'],
            'successors': {'engine': {'edge_attribute': 'owner'}},
            'predecessors': {'engine': {'edge_attribute': 'type'}},
            'attributes': [{'Notes': 'Test Note'}]
        }
        self.assertDictEqual(expected_dict, car_dict)

    def test_create_node_to_uml(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        vertex_car = Vertex(
            name='Car',
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )
        vertex_car_uml, car_decs, edge_car_uml = vertex_car.create_node_to_uml(
            translator=translator
        )

        vertex_engine = Vertex(
            name='engine',
            node_types=['component', 'component'],
            successors={'Car': {
                'edge_attribute': 'type'}},
            predecessors={'Car': {
                'edge_attribute': 'owner'}},
            settings_node=['Car']
        )
        engine_uml = vertex_engine.create_node_to_uml(
            translator=translator
        )

        car_node_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'create',
                    'name': 'Car',
                    'path': None,
                    'metatype': 'Class',
                    'stereotype': 'Block',
                    'attributes': [{'Notes': 'Test Note'}]
                },
            ]
        }]

        self.assertListEqual(car_node_uml, vertex_car_uml)

        car_edge_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/owner',
                    'value': 'new_1',
                }
            ]
        },
            {
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/type',
                    'value': 'new_0',
                }
            ]
        }]

        self.assertListEqual(car_edge_uml, edge_car_uml)

        engine_node_uml = [{
            'id': 'new_1',
            'ops': [
                {
                    'op': 'create',
                    'name': 'engine',
                    'path': None,
                    'metatype': 'Property',
                    'stereotype': 'PartProperty',
                    'attributes': None
                },
            ]
        }]

        engine_decoration_uml = [{
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/aggregation',
                    'value': ['new_0'],
                }
            ]
        },
            {
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/aggregation',
                    'value': ['new_0'],
                }
            ]
        }]

        self.assertDictEqual(engine_uml[0][0], engine_node_uml[0])
        for count, decs_dict in enumerate(engine_decoration_uml):
            self.assertDictEqual(engine_uml[1][count], decs_dict)

        engine_edge_uml = [{
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/type',
                    'value': 'new_0',
                }
            ]
        },
            {
            'id': 'new_0',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/owner',
                    'value': 'new_1',
                }
            ]
        }]

        self.assertListEqual(engine_uml[2], engine_edge_uml)

    def test_change_node_to_uml(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        vertex_car = Vertex(
            name='Car',
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )

        car_rename_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'rename',
                    'name': 'Car',
                    'path': None,
                    'metatype': 'Class',
                    'stereotype': 'Block',
                    'attributes': [{'Notes': 'Test Note'}]
                },
            ]
        }]

        rename_json = vertex_car.change_node_to_uml(
            translator=translator)

        self.assertDictEqual(car_rename_uml[0], rename_json)

    def test_delete_node_to_uml(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        vertex_car = Vertex(
            name='Car',
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )

        car_delete_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'delete',
                    'name': 'Car',
                    'path': None,
                    'metatype': 'Class',
                    'stereotype': 'Block',
                    'attributes': [{'Notes': 'Test Note'}]
                },
            ]
        }]

        delete_json = vertex_car.delete_node_to_uml(
            translator=translator)

        self.assertDictEqual(car_delete_uml[0], delete_json)

    def test_get_uml_id(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        node_names = ['Car', 'engine', 'Car']
        uml_id_names = []
        for node_name in node_names:
            uml_id_names.append(translator.get_uml_id(name=node_name))

        expected_uml_names = ['new_0', 'new_1', 'new_0']
        self.assertListEqual(expected_uml_names, uml_id_names)
        self.assertEqual(2, translator.uml_id['count'])

        edge_names = ['type', 'owner', 'type']
        edge_id_names = []
        for edge_name in edge_names:
            edge_id_names.append(translator.get_uml_id(name=edge_name))

        expected_uml_edge_names = ['new_2', 'new_3', 'new_2']
        self.assertListEqual(
            expected_uml_edge_names, edge_id_names)
        self.assertEqual(4, translator.uml_id['count'])

    def tearDown(self):
        pass


class TestDiEdge(unittest.TestCase):

    def setUp(self):
        pass

    def test_property_edge_triple(self):
        Car = Vertex(name='Car')
        car = Vertex(name='car')
        edge = DiEdge(source=Car,
                      target=car,
                      edge_attribute='owner')
        expected_triple = (Car, car, 'owner')
        self.assertTupleEqual(expected_triple, edge.edge_triple)

    def test_property_edge_vert_type_triple(self):
        Car = Vertex(name='Car', node_types={'Composite Thing'})
        car = Vertex(name='car', node_types={'component'})
        edge = DiEdge(source=Car,
                      target=car,
                      edge_attribute='owner')

        expected_triple = ({'Composite Thing'}, {'component'}, 'owner')
        self.assertTupleEqual(expected_triple, edge.edge_vert_type_triple)

    def test_property_named_edge_triple(self):
        Car = Vertex(name='Car')
        car = Vertex(name='car')
        edge = DiEdge(source=Car,
                      target=car,
                      edge_attribute='owner')

        expected_triple = ('Car', 'car', 'owner')
        self.assertTupleEqual(expected_triple, edge.named_edge_triple)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
