import unittest
import pandas as pd
import networkx as nx

from graph_analysis.utils import (create_column_values_under,
                                  create_column_values_space,
                                  create_column_values_singleton,
                                  create_column_values,
                                  get_node_types_attrs,
                                  get_setting_node_name_from_df)
from graph_analysis.graph_objects import UML_ID, Vertex, get_uml_id


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_column_values_under(self):
        data_dict = {
            'blockValue': ['Apple', 'Orange'],
            'value': ['Core', 'Skin'],
        }
        df = pd.DataFrame(data=data_dict)
        column_vals = create_column_values_under(
            prefix='C',
            first_node_data=df.loc[:, 'value'],
            second_node_data=df.loc[:, 'blockValue'],
        )
        expect_no_suffix = ['C_core_apple', 'C_skin_orange']
        self.assertListEqual(expect_no_suffix, column_vals)

        col_vals_suff = create_column_values_under(
            prefix='A',
            first_node_data=df.loc[:, 'value'],
            second_node_data=df.loc[:, 'blockValue'],
            suffix='-end1'
        )
        expect_suffix = ['A_core_apple-end1', 'A_skin_orange-end1']
        self.assertListEqual(expect_suffix, col_vals_suff)

    def test_create_column_values_space(self):
        data_dict = {
            'composite owner': ['Car', 'Wheel'],
            'component': ['chassis', 'hub']
        }
        df = pd.DataFrame(data=data_dict)
        created_cols = create_column_values_space(
            first_node_data=df.loc[:, 'composite owner'],
            second_node_data=df.loc[:, 'component']
        )
        expect_space = ['car qua chassis context',
                        'wheel qua hub context']
        self.assertListEqual(expect_space, created_cols)

    def test_create_column_values_singleton(self):
        first_node_data = ['green', 'blue']
        second_node_data = ['context1', 'context1']
        created_cols = create_column_values_singleton(
            first_node_data=first_node_data,
            second_node_data=second_node_data
        )
        expectation = ['green context1', 'blue context1']
        self.assertListEqual(expectation, created_cols)

    def test_create_column_values(self):
        data = ['Car', 'Wheel', 'Engine']
        data_2 = ['chassis', 'hub', 'drive output']
        columns = ['A_"composite owner"_component', 'composite owner']
        expected_output = {'A_"composite owner"_component':
                           ['A_car_chassis', 'A_wheel_hub',
                            'A_engine_drive output'],
                           'composite owner':
                           ['car qua chassis context',
                            'wheel qua hub context',
                            'engine qua drive output context']
                           }
        for col in columns:
            list_out = create_column_values(col_name=col, data=data,
                                            aux_data=data_2)
            self.assertListEqual(expected_output[col], list_out)

    def test_get_node_types_attrs(self):
        data_dict = {
            'component': ['car', 'wheel', 'engine'],
            'Atomic Thing': ['Car', 'Wheel', 'Car'],
            'edge attribute': ['owner', 'owner', 'owner'],
            'Notes': ['little car to big Car',
                      6,
                      2]
        }
        df = pd.DataFrame(data=data_dict)

        node_type_cols, node_attr_dict = get_node_types_attrs(
            df=df, node='Car',
            root_node_type='Atomic Thing',
            root_attr_columns={'Notes'})

        attr_list = [{'Notes': 'little car to big Car'}, {'Notes': 2}]
        self.assertEqual({'Atomic Thing'}, node_type_cols)
        self.assertListEqual(attr_list,
                             node_attr_dict)

    def test_get_setting_node_name_from_df(self):
        data_dict = {
            'component': ['car', 'wheel', 'engine'],
            'Atomic Thing': ['Car', 'Wheel', 'Car'],
            'edge attribute': ['owner', 'owner', 'owner'],
            'Notes': ['little car to big Car',
                      6,
                      2]
        }
        df = pd.DataFrame(data=data_dict)
        setting_node = get_setting_node_name_from_df(df=df,
                                                     column='Atomic Thing',
                                                     node='wheel')

        self.assertListEqual(['Wheel'], setting_node)

    # def test_get_spanning_tree(self):
    #     # So far incomplete test and subject to change.
    #     span_nodes = self.data['Pattern Spanning Tree Edges']
    #     span_edges = self.data['Pattern Spanning Tree Edge Labels']
    #     span_tree = [(tuple(pair), span_edges[index])
    #                  for index, pair in enumerate(span_nodes)]
    #     span_tree_set = set(span_tree)
    #
    #     node_attr_dict = {
    #         'A': 'Composite Thing',
    #         'B': 'component',
    #         'C': 'Atomic Thing',
    #         'D': 'A_"composite owner"_component',
    #         'E': 'composite owner'
    #     }
    #     Tree_Graph = nx.DiGraph()
    #
    #     for key in node_attr_dict:
    #         Tree_Graph.add_node(key, vertex_attribute=node_attr_dict[key])
    #
    #     Tree_Graph.add_edge('B', 'A', edge_attribute='owner')
    #     Tree_Graph.add_edge('B', 'C', edge_attribute='type')
    #     Tree_Graph.add_edge('D', 'B', edge_attribute='memberEnd')
    #     Tree_Graph.add_edge('E', 'D', edge_attribute='owner')
    #
    #     # vertex_list = []
    #     for vertex in Tree_Graph.nodes:
    #         vert = Vertex(
    #             name=vertex,
    #             node_types=nx.get_node_attributes(Tree_Graph,
    #                                               'vertex_attribute')[
    #                                               vertex],
    #             successors=Tree_Graph.succ[vertex],
    #             predecessors=Tree_Graph.pred[vertex])
    #         # vertex_list.append(vert)
    #
    #     # root_node_a = next((
    #     #   node for node in vertex_list if node.name == 'A'))
    #     spanning_tree = get_spanning_tree(
    #         root_node='A',
    #         root_node_type='Composite Thing',
    #         tree_pattern=span_nodes,
    #         tree_edge_pattern=span_edges)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
