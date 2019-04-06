import json
import unittest
from pathlib import Path

import networkx as nx
import pandas as pd

from graph_analysis.graph_creation import Evaluator, MDTranslator
from graph_analysis.graph_objects import DiEdge, PropertyDiGraph, Vertex

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
        self.assertSetEqual(expect_vert_set, self.Graph.named_vertex_set)

    def test_vertex_set(self):
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

        for vertex in self.Graph.vertex_set:
            self.assertIsInstance(vertex, Vertex)
            self.assertIn(vertex.name, expect_vert_set)

    def test_edge_set(self):
        # check each element of edge_set is infact a DiEdge then that it should
        # be an edge at all.
        # TODO: Find a way to use the self.Graph.edges tuples with the
        # edge attr because these show up as source, targ.
        translator = self.translator
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
        Test_Graph = PropertyDiGraph()
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
        car = Vertex(name='Car',
                     successors=[vertex_1_connections[0]],
                     predecessors=[vertex_1_connections[1]])
        engine = Vertex(name='engine',
                        successors=[vertex_2_connections[0]],
                        predecessors=[vertex_2_connections[1]])
        Test_Graph.add_node('Car', **{'Car': car})
        Test_Graph.add_node('engine', **{'engine': engine})
        Test_Graph.add_edge('Car', 'engine',
                            **{'diedge': DiEdge(source=car,
                                                target=engine,
                                                edge_attribute='owner')})
        Test_Graph.add_edge('engine', 'Car',
                            **{'diedge': DiEdge(source=engine,
                                                target=car,
                                                edge_attribute='type'), },)
        assert (Test_Graph.nodes['Car']['Car'].connections ==
                vertex_1_connections)
        assert (Test_Graph.nodes['engine']['engine'].connections ==
                vertex_2_connections)

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
        car_id = translator.get_uml_id(name='Car')
        vertex_car = Vertex(
            name='Car',
            id=car_id,
            node_types=['Atomic Thing', 'Composite Thing'],
            successors=[{'target': 'engine',
                         'source': 'Car',
                         'edge_attribute': 'owner', }, ],
            predecessors=[{'source': 'engine',
                           'target': 'Car',
                           'edge_attribute': 'type', }, ],
            attributes=[{'Notes': 'Test Note'}]
        )
        vertex_car_uml, car_decs, edge_car_uml = vertex_car.create_node_to_uml(
            translator=translator
        )

        engine_id = translator.get_uml_id(name='engine')
        vertex_engine = Vertex(
            name='engine',
            id=engine_id,
            node_types=['component', 'component'],
            successors=[{'target': 'Car',
                         'source': 'engine',
                         'edge_attribute': 'type', }, ],
            predecessors=[{'source': 'Car',
                           'target': 'engine',
                           'edge_attribute': 'owner', }, ],
            settings=[{'aggregation': 'composite'}]
        )
        engine_uml = vertex_engine.create_node_to_uml(
            translator=translator
        )

        car_node_uml = [{
            'id': 'new_' + str(car_id),
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
            'id': 'new_' + str(car_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/owner',
                    'value': 'new_' + str(engine_id),
                }
            ]
        },
            {
            'id': 'new_' + str(engine_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/type',
                    'value': 'new_' + str(car_id),
                }
            ]
        }]

        self.assertListEqual(car_edge_uml, edge_car_uml)

        engine_node_uml = [{
            'id': 'new_' + str(engine_id),
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
            'id': 'new_' + str(engine_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/aggregation',
                    'value': 'composite',
                }
            ]
        },
            {
            'id': 'new_' + str(engine_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/aggregation',
                    'value': 'composite',
                }
            ]
        }]

        self.assertDictEqual(engine_uml[0][0], engine_node_uml[0])
        for count, decs_dict in enumerate(engine_decoration_uml):
            self.assertDictEqual(engine_uml[1][count], decs_dict)

        engine_edge_uml = [{
            'id': 'new_' + str(engine_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/type',
                    'value': 'new_' + str(car_id),
                }
            ]
        },
            {
            'id': 'new_' + str(car_id),
            'ops': [
                {
                    'op': 'replace',
                    'path': '/m2/owner',
                    'value': 'new_' + str(engine_id),
                }
            ]
        }]

        self.assertListEqual(engine_uml[2], engine_edge_uml)

    def test_change_node_to_uml(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)

        translator = MDTranslator(json_data=data)
        car_id = translator.get_uml_id(name='Car')
        vertex_car = Vertex(
            name='Car',
            id=car_id,
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )

        car_rename_uml = [{
            'id': 'new_' + str(car_id),
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
        car_id = translator.get_uml_id(name='Car')
        vertex_car = Vertex(
            name='Car',
            id=car_id,
            node_types=['Atomic Thing', 'Composite Thing'],
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }},
            attributes=[{'Notes': 'Test Note'}]
        )

        car_delete_uml = [{
            'id': 'new_' + str(car_id),
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

        assert uml_id_names[0] == uml_id_names[2]
        assert uml_id_names[0] != uml_id_names[1]

        edge_names = ['type', 'owner', 'type']
        edge_id_names = []
        for edge_name in edge_names:
            edge_id_names.append(translator.get_uml_id(name=edge_name))

        expected_uml_edge_names = ['new_2', 'new_3', 'new_2']
        assert edge_id_names[0] == edge_id_names[2]
        assert edge_id_names[0] != edge_id_names[1]

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
