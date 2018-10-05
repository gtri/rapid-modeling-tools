import unittest
import pandas as pd
import networkx as nx

from copy import copy

from graph_analysis.utils import (create_column_values_under,
                                  create_column_values_space,
                                  create_column_values_singleton,
                                  create_column_values,
                                  get_node_types_attrs,
                                  match,
                                  match_changes)
from graph_analysis.graph_objects import DiEdge, UML_ID, Vertex, get_uml_id


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

    def test_match_changes(self):
        base_inputs = [('s1', 't1', 'type'), ('s2', 't2', 'type'),
                       ('s3', 't3', 'owner'), ('s4', 't4', 'owner'),
                       ('s5', 't5', 'memberEnd'),
                       ('s6', 't6', 'memberEnd'),
                       ('s7', 't7', 'type'), ('s8', 't8', 'type'),
                       ('s9', 't9', 'owner'), ('s10', 't10', 'owner'),
                       ('s11', 't11', 'memberEnd'),
                       ('s12', 't12', 'memberEnd'),
                       ('song', 'tiger', 'blue'), ]

        ancestor = [('as1', 't1', 'type'), ('s2', 'at2', 'type'),
                    ('as3', 't3', 'owner'), ('s4', 'at4', 'owner'),
                    ('as5', 't5', 'memberEnd'),
                    ('s6', 'at6', 'memberEnd'),
                    ('as7', 't7', 'type'), ('s8', 'at8', 'type'),
                    ('as9', 't9', 'owner'), ('s10', 'at10', 'owner'),
                    ('as11', 't11', 'memberEnd'),
                    ('s12', 'at12', 'memberEnd'), ('b', 'c', 'orange'),
                    ('s1', 'at1', 'type')]

        base_edges = []
        ancestor_edges = []

        for edge_tuple in base_inputs:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            base_edges.append(edge)

        for edge_tuple in ancestor:
            source = Vertex(name=edge_tuple[0])
            target = Vertex(name=edge_tuple[1])
            edge = DiEdge(source=source, target=target,
                          edge_attribute=edge_tuple[2])
            ancestor_edges.append(edge)

        base_map = dict((ea.edge_attribute, list()) for ea in base_edges)

        ance_map = dict((ea.edge_attribute, list())
                        for ea in ancestor_edges)

        for edge in base_edges:
            base_map[edge.edge_attribute].append(edge)
        for edge in ancestor_edges:
            ance_map[edge.edge_attribute].append(edge)

        base_preference = {}
        ancestor_preference = {}

        ance_keys_not_in_base = set(
            ance_map.keys()).difference(set(base_map.keys()))

        base_preference['no matching'] = []
        for edge_type in ance_keys_not_in_base:
            base_preference['no matching'].extend(ance_map[edge_type])

        for edge in base_edges:
            if edge.edge_attribute not in ance_map.keys():
                base_preference['no matching'].append(edge)
            else:
                base_preference[edge] = copy(
                    ance_map[edge.edge_attribute])

        for edge in ancestor_edges:
            if edge.edge_attribute not in base_map.keys():
                ancestor_preference[edge] = []
            else:
                ancestor_preference[edge] = copy(
                    base_map[edge.edge_attribute])

        match_dict = match_changes(change_dict=base_preference, score={},
                                   match_ancestors={})

        expected_matches = {('s2', 't2', 'type'): ('s2', 'at2', 'type'),
                            ('s3', 't3', 'owner'): ('as3', 't3', 'owner'),
                            ('s4', 't4', 'owner'): ('s4', 'at4', 'owner'),
                            ('s5', 't5', 'memberEnd'):
                                ('as5', 't5', 'memberEnd'),
                            ('s6', 't6', 'memberEnd'):
                                ('s6', 'at6', 'memberEnd'),
                            ('s7', 't7', 'type'): ('as7', 't7', 'type'),
                            ('s8', 't8', 'type'): ('s8', 'at8', 'type'),
                            ('s9', 't9', 'owner'): ('as9', 't9', 'owner'),
                            ('s10', 't10', 'owner'):
                                ('s10', 'at10', 'owner'),
                            ('s11', 't11', 'memberEnd'):
                                ('as11', 't11', 'memberEnd'),
                            ('s12', 't12', 'memberEnd'):
                                ('s12', 'at12', 'memberEnd'),
                            'no matching': [('b', 'c', 'orange'),
                                            ('song', 'tiger', 'blue')]}

        expected_unstable = {('s1', 't1', 'type'):
                             [('as1', 't1', 'type'),
                              ('s1', 'at1', 'type')],
                             }
        pairings = match_dict[0]
        unstable_pairs = match_dict[1]
        pairings_str = {}
        pairings_str.update({'no matching': []})

        unstable_keys = set(unstable_pairs.keys()).intersection(
            set(pairings.keys()))

        for key in pairings.keys():
            if key in unstable_keys:
                continue
            elif key is not "no matching":
                pairings_str.update({key.named_edge_triple:
                                     pairings[key][0].named_edge_triple})
            else:
                for edge in pairings[key]:
                    pairings_str[key].append(edge.named_edge_triple)

        self.assertDictEqual(expected_matches, pairings_str)

        for key in unstable_keys:
            unstable_key_vals = {
                edge.named_edge_triple for edge in unstable_pairs[key]}
            self.assertEqual(
                set(expected_unstable[key.named_edge_triple]),
                unstable_key_vals)

    def test_match(self):
        # TODO: Remove string or obj tests depending on which match uses.
        # # Case 1: Rename
        # current = ('source', 'target', 'type')
        # clone = ('new source', 'target', 'type')
        # self.assertEqual(1, match(current=current, clone=clone))
        # # Case 2: Same edge different otherwise
        # current = ('source', 'target', 'type')
        # clone = ('new source', 'new target', 'type')
        # self.assertEqual(0, match(current=current, clone=clone))
        # # Case 3: Edge of current longer than edge of clone
        # current = ('source', 'target', 'owner')
        # clone = ('new source', 'new target', 'type')
        # self.assertEqual(-1, match(current=current, clone=clone))
        # # Case 4: Edge of current shorter than edge of clone
        # current = ('source', 'target', 'type')
        # clone = ('new source', 'new target', 'memberEnd')
        # self.assertEqual(-2, match(current=current, clone=clone))
        car = Vertex(name='Car')
        engine = Vertex(name='engine')
        wheel = Vertex(name='wheel')

        # need a test for when I implement the 'edge type equivalence'
        # This would address a case: Suppose the edge attribtue 'type'
        # was in the edge set of Original_edge_attributes but 'type'not
        # in the edge set of Change_edge_attribtues and instead 'new type' was
        # there. Then I would want a way to say type -> new type.
        og_edge = DiEdge(source=car, target=engine,
                         edge_attribute='owner')

        # case: different target
        match_edge = DiEdge(source=car, target=wheel,
                            edge_attribute='owner')
        match_val = match(current=og_edge, clone=match_edge)
        self.assertEqual(1, match_val)

        # case: different source
        match_edge2 = DiEdge(source=wheel, target=engine,
                             edge_attribute='owner')
        match_val = match(current=og_edge, clone=match_edge2)
        self.assertEqual(1, match_val)

        # case: same edge type different otherwise
        match_edge3 = DiEdge(source=wheel, target=car,
                             edge_attribute='owner')
        match_val = match(current=og_edge, clone=match_edge3)
        self.assertEqual(0, match_val)

        # case: original edge type longer than change
        short_edge = DiEdge(source=car, target=engine, edge_attribute='type')
        match_val = match(current=og_edge, clone=short_edge)
        self.assertEqual(-1, match_val)

        # case: original edge type shorter than chagne
        long_edge = DiEdge(source=car, target=engine,
                           edge_attribute='memberEnd')
        match_val = match(current=og_edge, clone=long_edge)
        self.assertEqual(-2, match_val)

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
