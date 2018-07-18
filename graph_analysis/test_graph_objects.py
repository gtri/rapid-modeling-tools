import unittest
import json
import os
import pandas as pd
import networkx as nx

from utils import (create_vertex_objects, get_edge_type,
                   get_composite_owner_names,
                   get_a_composite_owner_names)
from test_graph_creation import DATA_DIRECTORY
from graph_objects import (Vertex, PropertyDiGraph, DiEdge,
                           get_uml_id, UML_ID, )


class TestPropertyDiGraph(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'PathMasterExpanded.json')) as f:
            data = json.load(f)

        # Create Baby dataset to deal with manual checking
        data_dict = {'Composite Thing': ['Car', 'Car',
                                         'Wheel', 'Engine'],
                     'component': ['engine', 'rear driver',
                                   'hub', 'drive output'],
                     'Atomic Thing': ['Engine', 'Wheel',
                                      'Hub', 'Drive Output']}
        self.df = pd.DataFrame(data=data_dict)

        columns_to_create = set(data['Pattern Graph Vertices']).difference(
            set(self.df.columns))

        composite_thing_series = self.df['Composite Thing']

        for col in columns_to_create:
            if col == 'composite owner':
                self.df[col] = get_composite_owner_names(
                    prefix=col, data=composite_thing_series)
            elif col == 'A_"composite owner"_component':
                self.df[col] = get_a_composite_owner_names(
                    prefix=col, data=composite_thing_series)

        self.Graph = PropertyDiGraph()
        for index, pair in enumerate(data['Pattern Graph Edges']):
            edge_type = get_edge_type(data=data, index=index)
            self.df[edge_type] = edge_type
            df_temp = self.df[[pair[0], pair[1], edge_type]]
            GraphTemp = nx.DiGraph()
            GraphTemp = nx.from_pandas_edgelist(
                df=df_temp, source=pair[0],
                target=pair[1], edge_attr=edge_type,
                create_using=GraphTemp)
            self.Graph.add_nodes_from(GraphTemp)
            self.Graph.add_edges_from(
                GraphTemp.edges, edge_attribute=edge_type)

    def test_named_vertex_set(self):
        expected_vertex_set = {'composite owner Wheel', 'Car',
                               'composite owner Car', 'Wheel',
                               'composite owner Engine', 'Engine',
                               'engine', 'rear driver', 'hub', 'Hub',
                               'drive output', 'Drive Output',
                               'A_Wheel_component', 'A_Car_component',
                               'A_Engine_component'}
        self.Graph.create_vertex_set(df=self.df)
        self.assertSetEqual(expected_vertex_set, self.Graph.named_vertex_set)

    def test_create_vertex_set(self):
        # idea is to check that the vertex_set contains the vert objects expect
        # check that each element in the vertex_set is a vertex object and
        # then check their names.
        expected_vertex_set = {'composite owner Wheel', 'Car',
                               'composite owner Car', 'Wheel',
                               'composite owner Engine', 'Engine',
                               'engine', 'rear driver', 'hub', 'Hub',
                               'drive output', 'Drive Output',
                               'A_Wheel_component', 'A_Car_component',
                               'A_Engine_component'}
        self.Graph.create_vertex_set(df=self.df)
        for vertex in self.Graph.vertex_set:
            self.assertIsInstance(vertex, Vertex)
            self.assertIn(vertex.name, expected_vertex_set)

        dict_keys_set = set(self.Graph.vertex_dict.keys())
        self.assertSetEqual(expected_vertex_set, dict_keys_set)

    def test_create_edge_set(self):
        # check each element of edge_set is infact a DiEdge then that it should
        # be an edge at all.
        # TODO: Find a way to use the self.Graph.edges tuples with the
        # edge attr because these show up as source, targ.
        self.Graph.create_vertex_set(df=self.df)
        self.Graph.create_edge_set()
        expected_edge_set = {('composite owner Car', 'Car', 'type'),
                             ('composite owner Car', 'A_Car_component',
                              'owner'),
                             ('composite owner Wheel', 'Wheel', 'type'),
                             ('composite owner Wheel',
                              'A_Wheel_component', 'owner'),
                             ('composite owner Engine', 'Engine', 'type'),
                             ('composite owner Engine',
                              'A_Engine_component', 'owner'),
                             ('engine', 'Engine', 'type'),
                             ('engine', 'Car', 'owner'),
                             ('rear driver', 'Wheel', 'type'),
                             ('rear driver', 'Car', 'owner'),
                             ('hub', 'Hub', 'type',),
                             ('hub', 'Wheel', 'owner'),
                             ('drive output', 'Drive Output', 'type'),
                             ('drive output', 'Engine', 'owner'),
                             ('A_Car_component', 'composite owner Car',
                              'memberEnd'),
                             ('A_Car_component', 'engine', 'memberEnd'),
                             ('A_Car_component', 'rear driver', 'memberEnd'),
                             ('A_Wheel_component', 'composite owner Wheel',
                              'memberEnd'),
                             ('A_Wheel_component', 'hub', 'memberEnd'),
                             ('A_Engine_component', 'composite owner Engine',
                              'memberEnd'),
                             ('A_Engine_component', 'drive output',
                              'memberEnd')}
        for edge in self.Graph.edge_set:
            self.assertIsInstance(edge, DiEdge)
            self.assertIn(edge.named_edge_triple, expected_edge_set)

    def tearDown(self):
        pass


class TestVertex(unittest.TestCase):

    def setUp(self):
        pass

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

        vertex_1_connections = [{'node_name': 'engine',
                                 'edge_attribute': 'owner'},
                                {'node_name': 'engine',
                                 'edge_attribute': 'type'}]
        vertex_2_connections = [{'node_name': 'Car',
                                 'edge_attribute': 'type'},
                                {'node_name': 'Car',
                                 'edge_attribute': 'owner'}]
        vertex_connections_dict = {0: vertex_1_connections,
                                   1: vertex_2_connections}
        for index, vertex in enumerate(verticies):
            self.assertListEqual(
                vertex_connections_dict[index], vertex.connections)

    def test_vertex_to_dict(self):
        # This also tests the Vertex.to_dict() method in a round about way
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

        vertex_1_dict = {'name': 'Car',
                         'node types': {'component', 'Atomic Thing'},
                         'successors': {'engine': {'edge_attribute': 'owner'}},
                         'predecessors': {'engine':
                                          {'edge_attribute': 'type'}}}
        vertex_2_dict = {'name': 'engine',
                         'node types': {'component', 'Atomic Thing'},
                         'successors': {'Car': {'edge_attribute': 'type'}},
                         'predecessors': {'Car': {'edge_attribute': 'owner'}}}
        vertex_dicts = [vertex_1_dict, vertex_2_dict]

        for index, vertex in enumerate(verticies):
            self.assertDictEqual(vertex_dicts[index], vertex.to_dict())

    def test_to_uml_json(self):
        vertex_car = Vertex(
            name='Car',
            node_types={'Atomic Thing'},
            successors={'engine': {
                'edge_attribute': 'owner'}},
            predecessors={'engine': {
                'edge_attribute': 'type'
            }}
        )
        vertex_car_uml, edge_car_uml = vertex_car.to_uml_json()

        vertex_engine = Vertex(
            name='engine',
            node_types={'component'},
            successors={'Car': {
                'edge_attribute': 'type'}},
            predecessors={'Car': {
                'edge_attribute': 'owner'}}
        )
        vertex_engine_uml, edge_engine_uml = vertex_engine.to_uml_json()

        car_node_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'create',
                    'name': 'Car',
                    'path': None,
                    'metatype': 'Class',
                }
            ]
        }]

        self.assertListEqual(car_node_uml, vertex_car_uml)

        car_edge_uml = [{
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/owner',
                    'value': 'new_0',
                }
            ]
        },
            {
            'id': 'new_1',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/type',
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
                }
            ]
        }]

        self.assertListEqual(vertex_engine_uml, engine_node_uml)

        engine_edge_uml = [{
            'id': 'new_0',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/type',
                    'value': 'new_1',
                }
            ]
        },
            {
            'id': 'new_0',
            'ops': [
                {
                    'op': 'replace',
                    'path': '/owner',
                    'value': 'new_1',
                }
            ]
        }]

        self.assertListEqual(edge_engine_uml, engine_edge_uml)
        # json_out = []
        # json_out.extend(vertex_car_uml)
        # json_out.extend(vertex_engine_uml)
        # json_out.extend(edge_car_uml)
        # json_out.extend(engine_edge_uml)
        # with open('changes_uml.json', 'w') as outfile:
        #     json.dump(json_out, outfile, indent=4)

    def test_get_uml_id(self):
        node_names = ['Car', 'engine', 'Car']
        uml_id_names = []
        for node_name in node_names:
            uml_id_names.append(get_uml_id(name=node_name))

        expected_uml_names = ['new_0', 'new_1', 'new_0']
        self.assertListEqual(expected_uml_names, uml_id_names)
        self.assertEqual(2, UML_ID['count'])

        edge_names = ['type', 'owner', 'type']
        edge_id_names = []
        for edge_name in edge_names:
            edge_id_names.append(get_uml_id(name=edge_name))

        expected_uml_edge_names = ['new_2', 'new_3', 'new_2']
        self.assertListEqual(
            expected_uml_edge_names, edge_id_names)
        self.assertEqual(4, UML_ID['count'])

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
