import json
import pprint as pp
import tempfile
import unittest
from copy import copy
from functools import partial
from pathlib import Path
from shutil import copy2

import networkx as nx
import pandas as pd

from graph_analysis.graph_creation import Manager, MDTranslator
from graph_analysis.graph_objects import DiEdge, Vertex
from graph_analysis.utils import (associate_node_id,
                                  associate_node_types_settings,
                                  associate_predecessors, associate_renames,
                                  associate_successors, build_dict,
                                  create_column_values_singleton,
                                  create_column_values_space,
                                  create_column_values_under,
                                  get_node_types_attrs,
                                  get_setting_node_name_from_df, make_object,
                                  match, match_changes, to_excel_df,
                                  to_uml_json_decorations, to_uml_json_edge,
                                  to_uml_json_node)

from . import DATA_DIRECTORY, PATTERNS


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_associate_node_id(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)
        tr = MDTranslator(json_data=data)
        node = 'test node'
        id = tr.get_uml_id(name=node)
        id_dict = associate_node_id(tr, node='test node')
        node_id = tr.uml_id['test node']

        self.assertDictEqual({'id': node_id}, id_dict)

    def test_associate_successors(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(['zero', 'one', 'two'])
        graph.add_edge('zero', 'one', edge_attribute='type')
        graph.add_edge('zero', 'two', edge_attribute='type')
        succs = associate_successors(graph, node='zero')
        succ_dict = {
            'successors': [{'source': 'zero',
                            'target': 'one',
                            'edge_attribute': 'type', },
                           {'source': 'zero',
                            'target': 'two',
                            'edge_attribute': 'type', }, ]
        }
        self.assertDictEqual(succ_dict, succs)

    def test_associate_predecessors(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(['zero', 'one', 'two'])
        graph.add_edge('one', 'zero', edge_attribute='type')
        graph.add_edge('two', 'zero', edge_attribute='type')
        preds = associate_predecessors(graph, node='zero')
        pred_dict = {
            'predecessors': [{'target': 'zero',
                              'source': 'one',
                              'edge_attribute': 'type', },
                             {'target': 'zero',
                              'source': 'two',
                              'edge_attribute': 'type', }, ]
        }
        self.assertDictEqual(pred_dict, preds)

    def test_associate_node_types_settings(self):
        data = (PATTERNS / 'Composition.json').read_text()
        data = json.loads(data)
        tr = MDTranslator(json_data=data)
        # for the test to work
        tr.data['Root Node'] = 'Atomic Thing'
        data_dict = {
            'component': ['car', 'wheel', 'engine'],
            'Atomic Thing': ['Car', 'Wheel', 'Car'],
            'edge attribute': ['owner', 'owner', 'owner'],
            'Notes': ['little car to big Car', 6, 2],
            'Two such Cols': [1, 2, 3],
        }
        df = pd.DataFrame(data=data_dict)

        node_type_cols, node_attr_dict = get_node_types_attrs(
            df=df, node='Car',
            root_node_type='Atomic Thing',
            root_attr_columns={'Notes', 'Two such Cols'})

        type_set_dict = associate_node_types_settings(
            df, tr, {'Notes', 'Two such Cols'}, node='Car'
        )
        expect = {
            'settings': [],
            'attributes': node_attr_dict,
            'node_types': ['Atomic Thing'],
        }
        self.assertDictEqual(expect, type_set_dict)

        type_cols, attr_dict = get_node_types_attrs(
            df=df, node='car', root_node_type='Atomic Thing',
            root_attr_columns={'Notes', 'Two such Cols'},)

        car_settings = associate_node_types_settings(
            df, tr, {}, node='car',)
        car_expect = {
            'settings': [{'aggregation': 'composite'}],
            'attributes': {},
            'node_types': list(type_cols),
        }
        self.assertDictEqual(car_expect, car_settings)

    def test_associate_renames(self):
        tr = MDTranslator()
        name_id_dict = {
            'A_composite owner_component-end1': '_1983',
            'car qua engine context': '_2019',
            'green apple': '_2020',
            'A_core_orange-context1': '_2021',
        }
        tr.uml_id.update(name_id_dict)
        df_renames = pd.DataFrame(data={
            'new name': ['atomic thing', 'composite thing',
                         'vehicle', 'piston engine', 'red',
                         'fruit', 'interior'],
            'old name': ['composite owner', 'component',
                         'car', 'engine', 'green',
                         'apple', 'core'],
        })
        df_renames.set_index('new name', inplace=True)
        changed_names = ['A_atomic thing_composite thing-end1',
                         'vehicle qua piston engine context',
                         'red fruit',
                         'A_interior_orange-context1']
        expect_dict = []
        for k, v in name_id_dict.items():
            expect_dict.append({'original_name': k,
                                'original_id': v})
        partial_rename = partial(associate_renames, df_renames, tr)
        for test_pair in zip(expect_dict, map(partial_rename, changed_names)):
            assert test_pair[0] == test_pair[1]

    def test_build_dict(self):
        arg = [{'id': 1}, {'name': 'Car'}]
        built_dict = build_dict(arg)
        expect = {'id': 1,
                  'name': 'Car'}
        self.assertDictEqual(expect, built_dict)

    def test_make_object(self):
        obj_attrs = {'name': 'Car',
                     'id': '123'}
        vert = Vertex(**obj_attrs)
        self.assertEqual(vert.name, 'Car')
        self.assertEqual(vert.id, '123')

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
        second_node_data = ['apple', 'context1']
        created_cols = create_column_values_singleton(
            first_node_data=first_node_data,
            second_node_data=second_node_data
        )
        expectation = ['green apple', 'blue context1']
        self.assertListEqual(expectation, created_cols)

    def test_get_node_types_attrs(self):
        # TODO: Investigate this test.
        # TODO: Expand functionality, this leaves notes on the floor
        data_dict = {
            'component': ['car', 'wheel', 'engine'],
            'Atomic Thing': ['Car', 'Wheel', 'Car'],
            'edge attribute': ['owner', 'owner', 'owner'],
            'Notes': ['little car to big Car',
                      6,
                      2],
            'Two such Cols': [1, 2, 3],
        }
        df = pd.DataFrame(data=data_dict)

        node_type_cols, node_attr_dict = get_node_types_attrs(
            df=df, node='Car',
            root_node_type='Atomic Thing',
            root_attr_columns={'Notes', 'Two such Cols'})

        attr_list = [{'Notes': 'little car to big Car',
                      'Two such Cols': 1}, {'Notes': 2, 'Two such Cols': 3}]
        # Try with multiple notes cols and a node with two types.
        self.assertEqual({'Atomic Thing'}, node_type_cols)
        self.assertListEqual(attr_list,
                             node_attr_dict)

    def test_match_changes(self):
        manager = Manager(
            excel_path=[
                (DATA_DIRECTORY / 'Composition_Diff_JSON_Baseline.xlsx'),
                (DATA_DIRECTORY / 'Composition_Diff_JSON_Changed.xlsx'),
            ],
            json_path=(PATTERNS / 'Composition.json'),
        )
        tr = manager.translator

        orig_data = {
            'Component': ['Thruster Cluster Assembly',
                          'Propellant Isolation Assembly',
                          'Spacecraft', ],
            'Position': ['Thruster-1', 'LV-3', 'ME', ],
            'Part': ['Small Thruster', 'Latch Valve', 'Main Engine'],
        }
        derived_A_lv3 = 'A_propellant isolation assembly qua lv-3 context_lv-3'
        derived_lv3 = 'propellant isolation assembly qua lv-3 context'
        orig_ids = {
            'Element Name': ['Thruster Cluster Assembly',
                             'Propellant Isolation Assembly',
                             'Spacecraft',
                             'Thruster-1',
                             'LV-3',
                             'ME',
                             'Small Thruster',
                             'Latch Valve',
                             'Main Engine',
                             derived_A_lv3,
                             derived_lv3,
                             ],
            'ID': ['_{0}'.format(num) for num in range(100, 111)]
        }
        change_data = {
            'Component': ['Thruster Cluster Assembly',
                          'Propellant Isolation Assembly',
                          'Space Ship', ],
            'Position': ['Thruster-1', 'SV-5', 'ME', ],
            'Part': ['Big Thruster', 'Solenoid Valve', 'Main Engine'],
        }
        change_renm_data = {
            'new name': ['SV-5', ],
            'old name': ['LV-3', ],
        }
        eval = manager.evaluators[0]
        eval1 = manager.evaluators[-1]
        eval.df = pd.DataFrame(data=orig_data)
        eval.df_ids = pd.DataFrame(data=orig_ids)
        eval.rename_df_columns()
        eval.add_missing_columns()
        eval.to_property_di_graph()
        pdg = eval.prop_di_graph

        eval1.df = pd.DataFrame(data=change_data)
        eval1.df_ids = pd.DataFrame(data=orig_ids)
        eval1.df_renames = pd.DataFrame(data=change_renm_data)
        eval1.df_renames.set_index('new name', inplace=True)
        eval1.rename_df_columns()
        eval1.add_missing_columns()
        eval1.to_property_di_graph()
        pdg1 = eval1.prop_di_graph

        add_edge = DiEdge(source=Vertex(name='b', id='200'),
                          target=Vertex(name='c', id='201'),
                          edge_attribute='orange')
        del_edge = DiEdge(source=Vertex(name='song',),
                          target=Vertex(name='tiger',),
                          edge_attribute='blue')

        eval_1_e_dict = pdg.edge_dict
        eval_1_e_dict.update({del_edge.named_edge_triple: del_edge})
        eval_2_e_dict = pdg1.edge_dict
        eval_2_e_dict.update({add_edge.named_edge_triple: add_edge})

        edge_set_one = eval.edge_set  # get baseline edge set
        edge_set_one.add(del_edge)
        edge_set_two = eval1.edge_set  # get the changed edge set
        edge_set_two.add(add_edge)

        # remove common edges
        # have to do this with named edges.
        edge_set_one_set = {edge.named_edge_triple
                            for edge in edge_set_one}
        edge_set_two_set = {edge.named_edge_triple
                            for edge in edge_set_two}

        # Remove edges common to each but preserve set integrity for
        # each evaluator
        eval_one_unmatched_named = list(edge_set_one_set.difference(
            edge_set_two_set))
        eval_two_unmatched_named = list(edge_set_two_set.difference(
            edge_set_one_set
        ))

        # Organize edges in dictionary based on type (this goes on for
        # multiple lines)
        eval_one_unmatched = [eval_1_e_dict[edge]
                              for edge in eval_one_unmatched_named]
        eval_two_unmatched = [eval_2_e_dict[edge]
                              for edge in eval_two_unmatched_named]

        eval_one_unmatch_map = dict((edge.edge_attribute, list())
                                    for edge in eval_one_unmatched)
        eval_two_unmatch_map = dict((edge.edge_attribute, list())
                                    for edge in eval_two_unmatched)

        for edge in eval_one_unmatched:
            eval_one_unmatch_map[edge.edge_attribute].append(
                edge)
        for edge in eval_two_unmatched:
            eval_two_unmatch_map[edge.edge_attribute].append(
                edge)

        eval_one_unmatch_pref = {}
        eval_two_unmatch_pref = {}

        ance_keys_not_in_base = set(
            eval_two_unmatch_map.keys()).difference(
                set(eval_one_unmatch_map))

        eval_one_unmatch_pref['Added'] = []
        eval_one_unmatch_pref['Deleted'] = []
        for edge_type in ance_keys_not_in_base:
            eval_one_unmatch_pref['Added'].extend(
                eval_two_unmatch_map[edge_type])

        for edge in eval_one_unmatched:
            if edge.edge_attribute not in eval_two_unmatch_map.keys():
                eval_one_unmatch_pref['Deleted'].append(edge)
            else:
                eval_one_unmatch_pref[edge] = copy(eval_two_unmatch_map[
                    edge.edge_attribute])
        for edge in eval_two_unmatched:
            if edge.edge_attribute not in eval_one_unmatch_map.keys():
                eval_two_unmatch_pref[edge] = []
            else:
                eval_two_unmatch_pref[edge] = copy(eval_one_unmatch_map[
                    edge.edge_attribute])

        match_dict = match_changes(change_dict=eval_one_unmatch_pref)

        orig = [('A_propellant isolation assembly qua lv-3 context_lv-3',
                 'propellant isolation assembly qua lv-3 context',
                 'memberEnd'),
                ('LV-3', 'Propellant Isolation Assembly', 'owner'),
                ('propellant isolation assembly qua lv-3 context',
                 'A_propellant isolation assembly qua lv-3 context_lv-3',
                 'owner'),
                ('A_spacecraft qua me context_me', 'ME', 'memberEnd'),
                ('ME', 'Spacecraft', 'owner'),
                ('Thruster-1', 'Small Thruster', 'type'),
                ('propellant isolation assembly qua lv-3 context',
                 'Propellant Isolation Assembly', 'type'),
                ('LV-3', 'Latch Valve', 'type'),
                ('A_propellant isolation assembly qua lv-3 context_lv-3',
                 'LV-3', 'memberEnd'),
                ]
        change = [('A_propellant isolation assembly qua sv-5 context_sv-5',
                   'propellant isolation assembly qua sv-5 context',
                   'memberEnd'),
                  ('SV-5', 'Propellant Isolation Assembly', 'owner'),
                  ('propellant isolation assembly qua sv-5 context',
                   'A_propellant isolation assembly qua sv-5 context_sv-5',
                   'owner'),
                  ('A_space ship qua me context_me', 'ME', 'memberEnd'),
                  ('ME', 'Space Ship', 'owner'),
                  ('Thruster-1', 'Big Thruster', 'type'),
                  ('propellant isolation assembly qua sv-5 context',
                   'Propellant Isolation Assembly', 'type'),
                  ('SV-5', 'Solenoid Valve', 'type'),
                  ('A_propellant isolation assembly qua sv-5 context_sv-5',
                   'SV-5', 'memberEnd'),
                  ]
        expected_matches = {z[0]: z[1]
                            for z in zip(orig, change)}

        expected_matches.update({'Added': [('b', 'c', 'orange'), ],
                                 'Deleted': [('song', 'tiger', 'blue')]})

        expected_unstable = {('s1', 't1', 'type'):
                             [('as1', 't1', 'type'),
                              ('s1', 'at1', 'type')],
                             }
        pairings = match_dict[0]
        unstable_pairs = match_dict[1]
        pairings_str = {}
        pairings_str.update({'Deleted': []})
        pairings_str.update({'Added': []})

        unstable_keys = set(unstable_pairs.keys()).intersection(
            set(pairings.keys()))

        for key in pairings.keys():
            if key in unstable_keys:
                continue
            elif key not in ('Deleted', 'Added'):
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
        car = Vertex(name='Car', id='1')
        engine = Vertex(name='engine', id='2')
        wheel = Vertex(name='wheel', id='3')

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
        match_val = match(*[match_edge], current=og_edge,)
        self.assertEqual(1, match_val[0])

        # case: different source
        match_edge2 = DiEdge(source=wheel, target=engine,
                             edge_attribute='owner')
        match_val = match(*[match_edge2], current=og_edge,)
        self.assertEqual(1, match_val[0])

        # case: same edge type different otherwise
        match_edge3 = DiEdge(source=wheel, target=car,
                             edge_attribute='owner')
        match_val = match(*[match_edge3], current=og_edge,)
        self.assertEqual(0, match_val[0])

        # case: original edge type longer than change
        short_edge = DiEdge(source=car, target=engine, edge_attribute='type')
        match_val = match(*[short_edge], current=og_edge,)
        self.assertEqual(-1, match_val[0])

        # case: original edge type shorter than chagne
        long_edge = DiEdge(source=car, target=engine,
                           edge_attribute='memberEnd')
        match_val = match(*[long_edge], current=og_edge,)
        self.assertEqual(-2, match_val[0])

        # case: rename of Car to Vehicle but actually the same edge.
        vehicle = Vertex(name='Vehicle', id='4', original_id='1',
                         original_name='Car')
        rename_edge = DiEdge(source=vehicle, target=engine,
                             edge_attribute='owner')
        match_rnm = match(*[rename_edge], current=og_edge,)
        self.assertEqual(2, match_rnm[0])

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

    def test_to_excel_df(self):
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
        new_name = Vertex(name='new name')
        old_name = Vertex(name='old name')

        fake_datas = {'0-1': {'Changes': {'Added': [added_edge],
                                          'Deleted': [deleted_edge],
                                          og_edge: [change_edge],
                                          'Rename new name': [new_name],
                                          'Rename old name': [old_name], },
                              'Unstable Pairs': {unstable_key: [
                                  unstable_one,
                                  unstable_two]}}}

        input_data = {}
        inner_dict = fake_datas['0-1']
        input_data.update(inner_dict['Changes'])
        input_data.update(inner_dict['Unstable Pairs'])
        str_keys = ['Edit 1', 'Edit 2', 'Added', 'Deleted']

        expected_data = {'Edit 1': [('green', 'apple', 'fruit'), ],
                         'Edit 2': [('gala', 'apple', 'fruit'), ],
                         'Unstable Matches Original': [
                         ('tomato', 'fruit', 'fruit'),
                         ('tomato', 'fruit', 'fruit'), ],
                         'Unstable Matches Change': [
                         ('tomato', 'vegetable', 'fruit'),
                         ('tomahto', 'fruit', 'fruit'), ],
                         'Added': [('blueberry', 'berry', 'bush')],
                         'Deleted': [('yellow', 'delicious', 'apple')],
                         'Rename new name': ['new name'],
                         'Rename old name': ['old name']}
        expected_df = pd.DataFrame(data=dict([
            (k, pd.Series(v)) for k, v in expected_data.items()]))

        excel_data = to_excel_df(data_dict=input_data, column_keys=str_keys)
        self.assertDictEqual(expected_data, excel_data)

        excel_df = pd.DataFrame(data=dict([
            (k, pd.Series(v)) for k, v in excel_data.items()]))
        self.assertTrue(expected_df.equals(excel_df))

    def test_to_uml_json_node(self):
        in_dict = {
            'id': 0,
            'op': 'create',
            'name': 'test name',
            'path': None,
            'metatype': 'meta meta',
            'stereotype': 'stereo',
            'attributes': None,
        }
        out = {
            'id': 0,
            'ops': [
                {
                    'op': 'create',
                    'name': 'test name',
                    'path': None,
                    'metatype': 'meta meta',
                    'stereotype': 'stereo',
                    'attributes': None,
                }
            ]
        }
        self.assertDictEqual(out, to_uml_json_node(**in_dict))

    def test_to_uml_json_decorations(self):
        info = {
            'id': 'new 0',
            'op': 'decoration',
            'path': 'home',
            'value': 'volume',
        }
        expect = {
            'id': 'new 0',
            'ops': [
                {
                    'op': 'decoration',
                    'path': '/m2/home',
                    'value': 'volume',
                }
            ]
        }
        self.assertDictEqual(expect, to_uml_json_decorations(**info))

    def test_to_uml_json_edge(self):
        edge_info = {
            'id': 'nal3013',
            'op': 'O P',
            'path': 'connector',
            'value': None,
        }
        expect = {
            'id': 'nal3013',
            'ops': [
                {
                    'op': 'O P',
                    'path': '/m2/' + 'connector',
                    'value': None,
                }
            ]
        }
        self.assertDictEqual(expect, to_uml_json_edge(**edge_info))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
