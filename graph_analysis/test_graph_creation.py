import unittest
import pandas as pd
import networkx as nx

from utils import create_vertex_objects
from graph_objects import Vertex, get_uml_id, UML_ID


class TestGraphCreation(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_uml_id(self):
        node_names = ['zeroth', 'first', 'second', 'zeroth']
        uml_id_names = []
        for node_name in node_names:
            uml_id_names.append(get_uml_id(name=node_name))

        expected_uml_names = ['new_0', 'new_1', 'new_2', 'new_0']
        self.assertListEqual(expected_uml_names, uml_id_names)
        self.assertEqual(3, UML_ID['count'])

        edge_names = ['type', 'owner', 'type']
        edge_id_names = []
        for edge_name in edge_names:
            edge_id_names.append(get_uml_id(name=edge_name))

        expected_uml_edge_names = ['new_3', 'new_4', 'new_3']
        self.assertListEqual(
            expected_uml_edge_names, edge_id_names)
        self.assertEqual(5, UML_ID['count'])

    def test_connections(self):
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

        verticies = create_vertex_objects(
            df=test_graph_df, graph=Test_Graph)

        vertex_1_dict = {'name': 'Car',
                         'node types': {'Component', 'Position'},
                         'successors': {'engine': {'edge_attribute': 'owner'}},
                         'predecessors': {'engine':
                                          {'edge_attribute': 'type'}}}
        vertex_2_dict = {'name': 'engine',
                         'node types': {'Component', 'Position'},
                         'successors': {'Car': {'edge_attribute': 'type'}},
                         'predecessors': {'Car': {'edge_attribute': 'owner'}}}
        vertex_dicts = [vertex_1_dict, vertex_2_dict]

        for index, vertex in enumerate(verticies):
            self.assertDictEqual(vertex_dicts[index], vertex.to_dict())

    def test_to_uml_json(self):
        pass
        UML_METATYPE = {
            'Composite Thing': 'Class',
            'Atomic Thing': 'Class',
            'composite owner': 'Property',
            'component': 'Property',
            'A_"composite owner"_component': 'Association'
        }

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
