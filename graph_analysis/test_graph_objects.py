import unittest
import json
import pandas as pd
import networkx as nx

from utils import create_vertex_objects
from graph_creation import DATA_DIRECTORY
from graph_objects import Vertex, get_uml_id, UML_ID


class TestPropertyDiGraph(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(DATA_DIRECTORY,
                               'PathMasterExpanded.json')) as f:
            data = json.load(f)

        self.evaluator = Evaluator(
            excel_file=os.path.join(
                DATA_DIRECTORY, 'Composition Example.xlsx'),
            json_data=data)
        self.evaluator.rename_excel_columns()
        self.evaluator.add_missing_columns()
        self.evaluator.to_property_di_graph()
        self.property_di_draph = self.evaluator.prop_di_graph

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
        #     json.dump(json_out, outfile)

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


if __name__ == '__main__':
    unittest.main()
