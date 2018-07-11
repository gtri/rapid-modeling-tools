import unittest
import json
import pandas as pd
import networkx as nx

from utils import (get_edge_type, get_composite_owner_names,
                   get_a_composite_owner_names,
                   create_vertex_objects)
from graph_objects import Vertex


class TestUtils(unittest.TestCase):

    def setUp(self):
        with open('../data/PathMasterExpanded.json') as f:
            self.data = json.load(f)

    def test_edge_type(self):
        self.assertEqual('type',
                         get_edge_type(data=self.data, index=0))

    def test_get_composite_owner_names(self):
        composite_data = pd.Series({'Car': 1, 'Wheel': 1, 'Engine': 1})
        composite_owner_output = get_composite_owner_names(
            prefix='composite owner', data=composite_data)
        composite_data_list = ['composite owner Car',
                               'composite owner Wheel',
                               'composite owner Engine']
        self.assertListEqual(composite_data_list, composite_owner_output)
        new_composite_names = get_composite_owner_names(
            prefix='composite owner', data=composite_data)
        self.assertEqual(3, len(new_composite_names))

    def test_get_a_composite_owner_name(self):
        composite_data = pd.Series({'Car': 1, 'Wheel': 1, 'Engine': 1})
        composite_owner_output = get_a_composite_owner_names(
            prefix='A_thing_component', data=composite_data)
        composite_data_list = ['A_Car_component',
                               'A_Wheel_component',
                               'A_Engine_component']
        self.assertListEqual(composite_data_list, composite_owner_output)

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


if __name__ == '__main__':
    unittest.main()
