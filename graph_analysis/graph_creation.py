import json
from copy import copy, deepcopy
from datetime import datetime
from functools import partial
from glob import glob
from itertools import chain, combinations
from pathlib import Path
from warnings import warn

import networkx as nx
import pandas as pd

from . import OUTPUT_DIRECTORY, PATTERNS
from .graph_objects import PropertyDiGraph, Vertex, DiEdge
from .utils import (associate_node_id, associate_node_types_settings,
                    associate_predecessors, associate_renames,
                    associate_successors, build_dict,
                    create_column_values_singleton, create_column_values_space,
                    create_column_values_under, distill_edges_to_nodes,
                    get_new_column_name, make_object, match_changes,
                    new_as_old, object_dict_view, to_excel_df,
                    to_nto_rename_dict, truncate_microsec)


class Manager:
    """
    Class for raw data input and distribution to other classes.

    The Manager takes in a list of n excel filepaths and a single json_path.
    The first Excel file in the excel_path input variable is assumed to be the
    baseline to which all subsequent excel paths will be compared as ancestors.
    If a comparison is not desired then each Excel file will be analyzed
    independently to produce create instructions for the Player Piano.

    A single json_path is taken because all of the input excel files are
    assumed to be of the same type and thus to correspond to the same set of
    data keys.

    Attribtues
    ----------
    excel_path : list
        list of paths to Excel Files.

    json_path : string
        string representing a path to a *.json file that is the key to decoding
        the Excel inputs into MagicDraw compatiable outputs.

    json_data : dictionary
        The json data associated with the json_path.

    translator : MDTranslator
        The MDTranslator object which can be passed to classes that require its
        functionality.

    evaluators : Evaluator
        list of the Evaluators created for each Excel file in the excel_path.
        len(evaluators) == len(excel_path)
    """

    def __init__(self, excel_path=None, json_path=None):
        self.excel_path = excel_path
        self.json_path = json_path
        self.json_data = None
        self.get_json_data()
        self.translator = MDTranslator(json_data=self.json_data)
        self.evaluators = []
        self.create_evaluators()

    def get_json_data(self):
        json_path = Path(self.json_path)
        data = (json_path).read_text()
        data = json.loads(data)
        self.json_data = data

    def create_evaluators(self):
        # TODO: Give baseline translator to change files but also to create
        # files if multiple create files in a create command. Issue?
        path_name = [excel_file.name for excel_file in self.excel_path]

        for count, excel_file in enumerate(self.excel_path):
            if count != 0:
                translator = self.evaluators[0].translator
            else:
                translator = self.translator
            self.evaluators.append(
                Evaluator(excel_file=excel_file,
                          translator=deepcopy(translator)))

    def get_pattern_graph_diff(self, out_directory=''):
        """
        Compares the graph describing an Original MagicDraw model to the graph
        describing an Updated MagicDraw model. If neither of the graphs is an
        original graph then the function will not compare them.

        This function

        Parameters
        ----------
        out_directory : string
            Desired directory for the output files. The directory specified
            here will be pushed to the json and excel writing functions.

        Notes
        -----
        For each pair of Evaluators such that one Evaluator is the original and
        the other Evaluator has a Rename DataFrame the function compares their
        graphs for differences. First, the function identifies the updated
        file and gets the new name information and builds a rename dictionary
        to then replace the objects that have changed names with the names
        from the original file.

        After masking the new names with their corresponding old name the edges
        from both graphs are arranged into dictionary by edge type; removing
        edges shared by both the original and changed alon gthe way.

        Once prepared, the match_changes function preforms a version of the
        stable marriage algorithm to pair off the changes and identify any
        changes where the desired change is unclear.

        Finally, the algorithm puts everything back in place and sends the
        changes to JSON creation and Excel creation.

        See Also
        --------
        get_new_column_name

        to_nto_rename_dict

        new_as_old

        match_changes
        """
        evaluator_dict = {evaluator: index for index, evaluator in enumerate(
            self.evaluators
        )}
        self.evaluator_change_dict = {}
        orig_eval = self.evaluators[0]

        for pair in combinations(self.evaluators, 2):
            eval_1_e_dict = pair[0].prop_di_graph.edge_dict
            eval_2_e_dict = pair[1].prop_di_graph.edge_dict
            # print(eval_1_e_dict)

            # Checking if Evaluator has a rename dataframe
            if pair[0].has_rename and pair[1].has_rename:  # comparing changes
                continue  # skip because this is comparing diff to diff
            # elif pair[0].has_rename:  # This shouldn't happen since first
            #     # pair entry always be baseline based on how combos built
            #     # rename pair[0]
            #     # loop eval_1_e_dict and if source is a
            #     # new_to_old.keys() then make new key and associate the obj
            #     # do the same if is target. return the new dict and a dict to
            #     # replace the keys at the end.
            #     new_translator = pair[0].translator
            #     # Do not need get_new_column_name, it is the index of renames
            #     new_name_col = get_new_column_name(
            #         original_df=orig_eval.df,
            #         rename_df=pair[0].df_renames)
            #     new_name_dict = pair[0].df_renames.to_dict(orient='list')
            #     n_t_o, rename_changes = to_nto_rename_dict(
            #         new_name=new_name_col,
            #         new_name_dict=new_name_dict)
            #     # iterate through keys in new_to_old changing names edge dict
            #     eval_1_e_dict, reverse_map, vert_obj_map = new_as_old(
            #         main_dict=eval_1_e_dict,
            #         new_keys=n_t_o)
            # elif pair[1].has_rename:
            #     # rename pair[1]
            #     new_translator = pair[1].translator
            #     new_name_col = get_new_column_name(
            #         original_df=orig_eval.df,
            #         rename_df=pair[1].df_renames)
            #     new_name_dict = pair[1].df_renames.to_dict(orient='list')
            #     n_t_o, rename_changes = to_nto_rename_dict(
            #         new_name=new_name_col,
            #         new_name_dict=new_name_dict)
            #     eval_2_obj_names = {key for key in n_t_o}
            #     # iterate through keys in new_to_old changing names edge dict
            #     eval_2_e_dict, reverse_map, vert_obj_map = new_as_old(
            #         main_dict=eval_2_e_dict,
            #         new_keys=n_t_o)

            edge_set_one = pair[0].edge_set  # get baseline edge set
            edge_set_two = pair[1].edge_set  # get the changed edge set
            # print(edge_set_one)

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

            # Run the matching algorithm
            eval_one_matches = match_changes(
                change_dict=eval_one_unmatch_pref)

            # Chagnes the names back to how they were before this function
            if pair[0].has_rename and pair[1].has_rename:  # comparing changes
                continue  # so nothing happened above.
            # elif pair[0].has_rename:
            #     # Put stuff back how it was
            #     eval_1_e_dict, new_to_old, old_v_obj_map = new_as_old(
            #         main_dict=eval_1_e_dict,
            #         new_keys=reverse_map)
            #     vert_dict = pair[1].prop_di_graph.vertex_dict
            #     for key in old_v_obj_map.keys():
            #         old_v_obj_map.update({key: vert_dict[key]})
            #     vert_obj_map.update(old_v_obj_map)
            #     n_t_o, rename_changes = to_nto_rename_dict(
            #         new_name=new_name_col,
            #         new_name_dict=new_name_dict,
            #         str_to_obj_map=vert_obj_map)
            #     eval_one_matches[0].update(rename_changes)
            # elif pair[1].has_rename:
            #     # undo change to nodes for comparisson purpose
            #     eval_2_e_dict, new_to_old, old_v_obj_map = new_as_old(
            #         main_dict=eval_2_e_dict,
            #         new_keys=reverse_map)
            #     vert_dict = pair[0].prop_di_graph.vertex_dict
            #     for key in old_v_obj_map.keys():
            #         old_v_obj_map.update({key: vert_dict[key]})
            #     vert_obj_map.update(old_v_obj_map)
            #     n_t_o, rename_changes = to_nto_rename_dict(
            #         new_name=new_name_col,
            #         new_name_dict=new_name_dict,
            #         str_to_obj_map=vert_obj_map)
            #     eval_one_matches[0].update(rename_changes)

            new_name_objs = ''
            for key in eval_one_matches[0]:
                if isinstance(key, str):
                    if new_name_col in key:
                        new_name_objs = key
            changes_and_unstable = {'Changes': eval_one_matches[0],
                                    'Unstable Pairs': eval_one_matches[1]}

            key = '{0}-{1}'.format(evaluator_dict[pair[0]],
                                   evaluator_dict[pair[1]])

            self.graph_difference_to_json(new_col=new_name_objs,
                                          new_name_dict=new_to_old,
                                          change_dict=eval_one_matches[0],
                                          translator=new_translator,
                                          evaluators=key,
                                          out_directory=out_directory)
            self.evaluator_change_dict.update(
                {key: changes_and_unstable})

        return self.evaluator_change_dict

    def changes_to_excel(self, out_directory=''):
        """

        Parameters
        ----------

        Notes
        -----

        See Also
        --------
        """
        for key in self.evaluator_change_dict:
            outfile = Path(
                'Model Diffs {0}-{1}.xlsx'.format(
                    key, truncate_microsec(curr_time=datetime.now().time())))

            if out_directory:
                outdir = out_directory
            else:
                outdir = OUTPUT_DIRECTORY

            difference_dict = self.evaluator_change_dict[key]
            input_dict = {}
            evals_comp = key.split('-')
            edit_left_dash = 'Edit {0}'.format(str(int(evals_comp[0]) + 1))
            edit_right_dash = 'Edit {0}'.format(str(int(evals_comp[-1]) + 1))
            column_headers = [edit_left_dash, edit_right_dash]

            for in_key in difference_dict:
                if not difference_dict[in_key]:
                    continue
                column_headers.append(in_key)
                input_dict.update(difference_dict[in_key])
            df_data = to_excel_df(data_dict=input_dict,
                                  column_keys=column_headers)

            df_output = pd.DataFrame(data=dict([
                (k, pd.Series(v)) for k, v in df_data.items()
            ]))

            df_output.to_excel(
                (outdir / outfile), sheet_name=key, index=False)

    def graph_difference_to_json(self, new_col='', new_name_dict=None,
                                 change_dict=None, translator=None,
                                 evaluators='',
                                 out_directory='', ):
        # need to strip off the keys that are strings and use them to
        # determine what kinds of ops I need to preform.
        # Naked Key: Value pairs mean delete edge key and add value key.
        # Purposefully excluding unstable pairs because the Human can make
        # those changes so they are clear.
        static_keys = ['Added', 'Deleted', new_col]
        change_list = []
        edge_del = []
        edge_add = []
        node_renames = []
        create_new_name_node = []
        rename_nodes = {n.name for n in change_dict[new_col]}

        for key, value in change_dict.items():
            if key == 'Added':
                for edge in change_dict[key]:
                    edge_add.append(edge.edge_to_uml(op='replace',
                                                     translator=translator))
            elif key == 'Deleted':
                for edge in change_dict[key]:
                    edge_del.append(edge.edge_to_uml(op='delete',
                                                     translator=translator))
            elif key == new_col:
                for node in change_dict[key]:
                    node_renames.append(
                        node.change_node_to_uml(translator=translator)
                    )
            elif isinstance(key, str) and key != new_col:
                continue
            else:
                source, target = value[0].source, value[0].target
                if 'new' in translator.uml_id[source.name]:
                    # create then add
                    node_cr, node_dec, node_edge = source.create_node_to_uml(
                        translator=translator
                    )
                    # extend here and below was previously append
                    # will have to do some crazy work to remove duplicates
                    create_new_name_node.extend(node_cr)
                    if node_dec:
                        create_new_name_node.extend(node_dec)
                    if node_edge:
                        edge_add.extend(node_edge)
                elif 'new' in translator.uml_id[target.name]:
                    # create then add
                    node_cr, node_dec, node_edge = target.create_node_to_uml(
                        translator=translator
                    )
                    create_new_name_node.extend(node_cr)
                    if node_dec:
                        create_new_name_node.extend(node_dec)
                    if node_edge:
                        edge_add.extend(node_edge)

                renm_source = any(source.name in nm for nm in rename_nodes)
                renm_target = any(target.name in nm for nm in rename_nodes)
                if renm_source or renm_target:
                    # replace the key.source with value.source
                    # replace key.target with value.target
                    del_edge_json = key.edge_to_uml(op='delete',
                                                    translator=translator)
                    edge_del.append(del_edge_json)

                    add_edge_json = value[0].edge_to_uml(op='replace',
                                                         translator=translator)
                    edge_add.append(add_edge_json)
                else:
                    # rename node was not in either of change items
                    source_id = translator.uml_id[source.name]
                    target_id = translator.uml_id[target.name]
                    if 'new' in source_id and target_id:
                        # if 'new' in source.id and target.id
                        # create both value.source and value.target
                        # create then add
                        s_cr, s_dec, s_edge = source.create_node_to_uml(
                            translator=translator
                        )
                        # extend here and below was previously append
                        # will have to do some crazy work to remove duplicates
                        create_new_name_node.extend(s_cr)
                        if s_dec:
                            create_new_name_node.extend(s_dec)
                        if s_edge:
                            edge_add.extend(s_edge)
                        # create then add
                        t_cr, t_dec, t_edge = target.create_node_to_uml(
                            translator=translator
                        )
                        create_new_name_node.extend(t_cr)
                        if t_dec:
                            create_new_name_node.extend(t_dec)
                        if t_edge:
                            edge_add.extend(t_edge)
                    elif 'new' in source_id:
                        s_cr, s_dec, s_edge = source.create_node_to_uml(
                            translator=translator
                        )
                        # extend here and below was previously append
                        # will have to do some crazy work to remove duplicates
                        create_new_name_node.extend(s_cr)
                        if s_dec:
                            create_new_name_node.extend(s_dec)
                        if s_edge:
                            edge_add.extend(s_edge)
                        # elif 'new' in source.id
                        # create node for value.source
                    elif 'new' in target_id:
                        # create then add
                        t_cr, t_dec, t_edge = target.create_node_to_uml(
                            translator=translator
                        )
                        create_new_name_node.extend(t_cr)
                        if t_dec:
                            create_new_name_node.extend(t_dec)
                        if t_edge:
                            edge_add.extend(t_edge)
                        # elif 'new' in target.id
                        # create node for value.target
                    else:
                        del_edge_json = key.edge_to_uml(op='delete',
                                                        translator=translator)
                        edge_del.append(del_edge_json)

                        add_edge_json = value[0].edge_to_uml(
                            op='replace',
                            translator=translator
                        )
                        edge_add.append(add_edge_json)
                    # else
                    # replace key (edge) with target (edge)

        seen_id = set()
        for nn_d in create_new_name_node:
            if not nn_d['id'] in seen_id:
                seen_id.add(nn_d['id'])
                change_list.append(nn_d)
            else:
                continue
        change_list.extend(edge_del)
        change_list.extend(edge_add)
        change_list.extend(node_renames)

        json_out = {'modification targets': []}
        json_out['modification targets'].extend(change_list)
        outfile = Path('graph_diff_changes_{0}({1}).json'.format(
            evaluators, truncate_microsec(curr_time=datetime.now())))

        if out_directory:
            outdir = out_directory
        else:
            outdir = OUTPUT_DIRECTORY

        (outdir / outfile).write_text(
            json.dumps(json_out, indent=4, sort_keys=True))

        return change_list


class Evaluator:
    """Class for creating the PropertyDiGraph from the Excel data with the help
    of the MDTranslator.

    Evaluator produces a Pandas DataFrame from the Excel path provided by the
    Manager. The Evaluator then updates the DataFrame with column headers
    compliant with MagidDraw and infers required columns from the data stored
    in the MDTranslator. With the filled out DataFrame the Evaluator produces
    the PropertyDiGraph.

    Parameters
    ----------
    excel_file : string
        String to an Excel File

    translator : MDTranslator
        MDTranslator object that holds the data from the *.json file
        associated with this type of Excel File.

    Attributes
    ----------
    df : Pandas DataFrame
        DataFrame constructed from reading the Excel File.

    prop_di_graph : PropertyDiGraph
        PropertyDiGraph constructed from the data in the df.

    root_node_attr_columns : set
        Set of column names in the initial read of the Excel file that do not
        appear as Vertices in the MDTranslator definition of the expected
        Vertices. The columns collected here will later be associated to the
        corresponding root node as additional attributes.

    Properties
    ----------
    named_vertex_set : set
        Returns the named vertex set from the PropertyDiGraph.

    vertex_set : set
        Returns the vertex set from the PropertyDiGraph
    """

    # TODO: Consider moving function calls into init since they should be run
    # then
    def __init__(self, excel_file=None, translator=None):
        self.translator = translator
        self.df = pd.DataFrame()
        self.df_ids = pd.DataFrame()
        self.df_renames = pd.DataFrame()
        self.excel_file = excel_file
        # TODO: Why did I do this? save the file off as self.file then
        # call sheets_to_dataframe on self.
        self.sheets_to_dataframe(excel_file=excel_file)
        # self.df.dropna(how='all', inplace=True)
        self.prop_di_graph = None
        self.root_node_attr_columns = set()

    @property
    def has_rename(self):
        if not self.df_renames.empty:
            return True
        else:
            return False

    def sheets_to_dataframe(self, excel_file=None):
        # TODO: Generalize/Standardize this function
        patterns = [pattern.name.split('.')[0].lower()
                    for pattern in PATTERNS.glob('*.json')]
        ids = ['id', 'ids', 'identification number',
               'id number', 'uuid', 'mduuid', 'magicdraw id',
               'magic draw id', 'magicdraw identification',
               'identification numbers', 'id_numbers', 'id_number']
        renames = ['renames', 'rename', 'new names', 'new name', 'newnames',
                   'newname', 'new_name', 'new_names', 'changed names',
                   'changed name', 'change names', 'changed_names',
                   'changenames', 'changed_names']
        xls = pd.ExcelFile(excel_file, on_demand=True)
        for sheet in sorted(xls.sheet_names):  # Alphabetical sort
            # Find the Pattern Sheet
            if any(pattern in sheet.lower() for pattern in patterns):
                # Maybe you named the ids sheet Pattern IDs I will find it
                if any(id_str in sheet.lower() for id_str in ids):
                    self.df_ids = pd.read_excel(
                        excel_file, sheet_name=sheet)
                    self.df_ids.set_index(
                        self.df_ids.columns[0], inplace=True)
                    self.translator.uml_id.update(
                        self.df_ids.to_dict(
                            orient='dict')[self.df_ids.columns[0]])
                # elif sheet.lower() in renames:
                # Maybe you named the rename sheet Pattern Renames
                elif any(renm_str in sheet.lower() for renm_str in renames):
                    self.df_renames = pd.read_excel(
                        excel_file, sheet_name=sheet)
                    self.df_renames.dropna(
                        how='all', inplace=True)
                    for row in self.df_renames.itertuples(index=False):
                        if row[0] in self.translator.uml_id.keys():
                            # replace instances of this with those in 1
                            if len(row) == 2:
                                if not self.df_renames.index.is_object():
                                    # do the thing set the index as new name
                                    old_mask = self.df_renames == row[0]
                                    old_masked_df = self.df_renames[
                                        old_mask].dropna(how='all', axis=0)
                                    # should return new names col and nan
                                    new_names = self.df_renames.T.index.where(
                                        old_masked_df.isnull()).tolist()
                                    new_col = list(
                                        chain.from_iterable(new_names))
                                    new_name = list(
                                        filter(
                                            lambda x: isinstance(
                                                x, str), new_col))
                                    self.df_renames.set_index(
                                        new_name, inplace=True)
                            else:
                                raise RuntimeError(
                                    'Unexpected columns in Rename Sheet. \
                                     Expected 2 but found more than 2.')
                            self.df.replace(to_replace=row[0],
                                            value=row[1],
                                            inplace=True)
                            self.translator.uml_id.update({
                                row[1]: self.translator.uml_id[row[0]]
                            })
                        elif row[1] in self.translator.uml_id.keys():
                            if len(row) == 2:
                                if not self.df_renames.index.is_object():
                                    # do the thing set the index as new name
                                    old_mask = self.df_renames == row[1]
                                    old_masked_df = self.df_renames[
                                        old_mask].dropna(how='all', axis=0)
                                    # should return new names col and nan
                                    new_names = self.df_renames.T.index.where(
                                        old_masked_df.isnull()).tolist()
                                    new_col = list(
                                        chain.from_iterable(new_names))
                                    new_name = list(
                                        filter(
                                            lambda x: isinstance(
                                                x, str), new_col))
                                    self.df_renames.set_index(
                                        new_name, inplace=True)
                            else:
                                raise RuntimeError(
                                    'Unexpected columns in Rename Sheet. \
                                     Expected 2 but found more than 2.')
                            # same as above in other direction
                            self.df.replace(to_replace=row[1],
                                            value=row[0],
                                            inplace=True)
                            self.translator.uml_id.update(
                                {row[0]: self.translator.uml_id[row[1]]}
                            )
                else:
                    self.df = pd.read_excel(excel_file, sheet_name=sheet)
                    self.df.dropna(how='all', inplace=True)
            # elif sheet.lower() in renames:
            # Hopefully you explcitly named the Rename sheet
            elif any(renm_str in sheet.lower() for renm_str in renames):
                self.df_renames = pd.read_excel(excel_file,
                                                sheet_name=sheet)
                self.df_renames.dropna(
                    how='all', inplace=True)
                index_name = ''
                for row in self.df_renames.itertuples(index=False):
                    if all(row[i] in self.translator.uml_id.keys()
                            for i in (0, 1)):
                        raise RuntimeError('Both old and new in keys')
                    elif row[0] in self.translator.uml_id.keys():
                        # then replace instances of this with those in 1
                        if len(row) == 2:
                            if not self.df_renames.index.is_object():
                                # do the thing set the index as new name
                                old_mask = self.df_renames == row[0]
                                old_masked_df = self.df_renames[
                                    old_mask].dropna(how='all', axis=0)
                                # should return name of new names col and nan
                                new_names = self.df_renames.T.index.where(
                                    old_masked_df.isnull()).tolist()
                                new_col = list(
                                    chain.from_iterable(new_names))
                                new_name = list(
                                    filter(
                                        lambda x: isinstance(x, str), new_col))
                                self.df_renames.set_index(
                                    new_name, inplace=True)
                        else:
                            raise RuntimeError(
                                'Unexpected columns in Rename Sheet. \
                                 Expected 2 but found more than 2.')
                        self.df.replace(to_replace=row[0], value=row[1],
                                        inplace=True)
                        self.translator.uml_id.update({
                            row[1]: self.translator.uml_id[row[0]]
                        })
                        continue
                    elif row[1] in self.translator.uml_id.keys():
                        # row[1] is old, row[0] is new
                        if len(row) == 2:
                            if not self.df_renames.index.is_object():
                                # do the thing set the index as new name
                                old_mask = self.df_renames == row[1]
                                old_masked_df = self.df_renames[
                                    old_mask].dropna(how='all', axis=0)
                                # should return name of new names col and nan
                                new_names = self.df_renames.T.index.where(
                                    old_masked_df.isnull()).tolist()
                                new_col = list(
                                    chain.from_iterable(new_names))
                                new_name = list(
                                    filter(
                                        lambda x: isinstance(x, str), new_col))
                                self.df_renames.set_index(
                                    new_name, inplace=True)
                        else:
                            raise RuntimeError(
                                'Unexpected columns in Rename Sheet. \
                                 Expected 2 but found more than 2.')
                        # same as above in other direction
                        self.df.replace(to_replace=row[1], value=row[0],
                                        inplace=True)
                        self.translator.uml_id.update(
                            {row[0]: self.translator.uml_id[row[1]]}
                        )
                        continue
            elif any(id_str in sheet.lower() for id_str in ids) and \
                    not any(pattern in sheet.lower() for pattern in patterns):
                self.df_ids = pd.read_excel(
                    excel_file, sheet_name=sheet)
                self.df_ids.set_index(
                    self.df_ids.columns[0], inplace=True)
                self.translator.uml_id.update(
                    self.df_ids.to_dict(
                        orient='dict')[self.df_ids.columns[0]])
            else:
                raise RuntimeError(
                    'Unrecognized sheet names for: {0}'.format(
                        excel_file.name
                    ))

    def rename_df_columns(self):
        """Returns renamed DataFrame columns from their Excel name to their
        MagicDraw name. Any columns in the Excel DataFrame that are not in the
        json are recorded as attribute columns.
        """
        for column in self.df.columns:
            try:
                new_column_name = self.translator.get_col_uml_names(
                    column=column)
                self.df.rename(columns={column: new_column_name}, inplace=True)
            except KeyError:
                # We continue because these columns are additional data
                # that we will associate to the Vertex as attrs.
                self.root_node_attr_columns.add(column)

    def add_missing_columns(self):
        """Adds the missing column to the dataframe. These columns are ones
        required to fillout the pattern in the MDTranslator that were not
        specified by the user. The MDTranslator provides a template for naming
        these inferred columns.

        Notes
        -----
        Stepping through the function, first a list of column names that
        appear in the JSON but not the Excel are compiled by computing the
        difference between the expected column set from the Translator and the
        initial dataframe columns. Then those columns are sorted by length
        to ensure that longer column names constructed of multiple shorter
        columns do not fail when searching the dataframe.
            e.g. Suppose we need to construct the column
            A_composite owner_component. Sorting by length ensures that
            columns_to_create = ['component', 'composite owner',
            'A_composite owner_component']
        Then for each column name in columns to create, the column name is
        checked for particular string properties and the inferred column values
        are determined based on the desired column name.
        """
        # from a collection of vertex pairs, create all of the columns for
        # for which data is required but not present in the excel.
        columns_to_create = list(set(
            self.translator.get_pattern_graph()).difference(
            set(self.df.columns)))
        # TODO: Weak solution to the creation order problem.
        columns_to_create = sorted(columns_to_create, key=len)

        under = '_'
        space = ' '
        dash = '-'
        if columns_to_create:
            for col in columns_to_create:
                if under in col:
                    if dash in col:
                        col_data_vals = col.split(sep=under)
                        suffix = col_data_vals[-1].split(sep=dash)
                        first_node_data = self.df.loc[:, col_data_vals[1]]
                        second_node_data = self.df.loc[:, suffix[0]]
                        suff = dash + suffix[-1]
                        self.df[col] = create_column_values_under(
                            prefix=col_data_vals[0],
                            first_node_data=first_node_data,
                            second_node_data=second_node_data,
                            suffix=suff
                        )
                    else:
                        col_data_vals = col.split(sep=under)
                        first_node_data = self.df.loc[:, col_data_vals[1]]
                        second_node_data = self.df.loc[:, col_data_vals[2]]
                        self.df[col] = create_column_values_under(
                            prefix=col_data_vals[0],
                            first_node_data=first_node_data,
                            second_node_data=second_node_data,
                            suffix=''
                        )
                elif space in col:
                    col_data_vals = col.split(sep=space)
                    root_col_name = self.translator.get_root_node()
                    if col_data_vals[0] in self.df.columns:
                        first_node_data = self.df.loc[:, col_data_vals[0]]
                        second_node_data = [col_data_vals[-1]
                                            for i in range(
                                                len(first_node_data))]
                    else:
                        first_node_data = self.df.iloc[:, 0]
                        second_node_data = self.df.loc[:, root_col_name]
                    self.df[col] = create_column_values_space(
                        first_node_data=first_node_data,
                        second_node_data=second_node_data
                    )
                else:
                    col_data_vals = col
                    root_col_name = self.translator.get_root_node()
                    first_node_data = self.df.iloc[:, 0]
                    second_node_data = [
                        col for count in range(len(first_node_data))]
                    self.df[col] = create_column_values_singleton(
                        first_node_data=first_node_data,
                        second_node_data=second_node_data
                    )

    def to_property_di_graph(self):
        """Creates a PropertyDiGraph from the completely filled out dataframe.
        To achieve this, we loop over the Pattern Graph Edges defined in the
        JSON and take each pair of columns and the edge type as a source,
        target pair with the edge attribute corresponding to the edge type
        defined in the JSON.
        """
        self.prop_di_graph = PropertyDiGraph(
            root_attr_columns=self.root_node_attr_columns
        )
        for index, pair in enumerate(
                self.translator.get_pattern_graph_edges()):
            edge_type = self.translator.get_edge_type(index=index)
            self.df[edge_type] = edge_type
            df_temp = self.df[[pair[0], pair[1], edge_type]]
            GraphTemp = nx.DiGraph()
            GraphTemp = nx.from_pandas_edgelist(
                df=df_temp, source=pair[0],
                target=pair[1], edge_attr=edge_type,
                create_using=GraphTemp)
            self.prop_di_graph.add_nodes_from(GraphTemp.nodes)
            self.prop_di_graph.add_edges_from(GraphTemp.edges,
                                              edge_attribute=edge_type)

        pdg = self.prop_di_graph
        tr = self.translator

        # Est list of lists with dict for each node contaiing its name
        # node is already a string because of networkx functionality
        # idea is to build up kwargs to instantiate a vertex object.
        node_atters = [[{'name': node}
                        for node in list(pdg)]]

        # various functions required to get different vertex attrs
        # partialy instantiate each function so that each fn only needs node
        associate_funs = [partial(associate_node_id, tr),
                          partial(associate_successors, pdg),
                          partial(associate_predecessors, pdg),
                          partial(associate_node_types_settings, self.df,
                                  tr, self.root_node_attr_columns),
                          partial(associate_renames, self.df_renames, tr), ]

        # apply each function to each node.
        # map(function, iterable)
        for fun in associate_funs:
            fun_map = map(fun, list(pdg))
            node_atters.append(fun_map)

        # Partially bake a Vertex object to make it act like a function when
        # passed the attr dict. Atter dict built using map(build_dict, zip())
        # zip(*node_atters) unpacks the nested lists then takes one of ea attr
        # from the map obj stored there (map objs are iterables)
        vertex = partial(make_object, Vertex)
        for mp in map(vertex, map(build_dict, zip(*node_atters))):
            vert_tup = (mp.name, {mp.name: mp})
            # overwrites the original node in the graph to add an attribute
            # {'<name>': <corresponding vertex object>}
            pdg.add_node(vert_tup[0], **vert_tup[1])

        # build edges container
        edges = []
        for edge, data in pdg.edges.items():
            diedge = DiEdge(source=pdg.nodes[edge[0]][edge[0]],
                            target=pdg.nodes[edge[1]][edge[1]],
                            edge_attribute=data['edge_attribute'])
            edges.append((edge, {'diedge': diedge}))
        for edge in edges:
            # unpack each edge and the edge attribute dict for the add_edge fn
            pdg.add_edge(*edge[0], **edge[1])

        # pdg has associated vertex obj and associated edge obj in edj dict.
        return pdg

    @property
    def named_vertex_set(self):
        return self.prop_di_graph.get_vertex_set_named(df=self.df)

    @property
    def vertex_set(self):
        return self.prop_di_graph.vertex_set

    @property
    def named_edge_set(self):
        return self.prop_di_graph.named_edge_set

    @property
    def edge_set(self):
        return self.prop_di_graph.edge_set


class MDTranslator:
    """
    Class to serve as the Rosetta Stone for taking column headers from the
    Excel input to the MagicDraw compatible output. More specifically, this
    class provides access to data in the JSON file allowing the Evaluator to
    determine which columns are required to fill out the pattern that are
    missing in the input Excel and to associate edge types along the directed
    edges. Furthermore, while the Vertex is packaged in to_uml_json() the
    translator provides metadata information required by MagicDraw for block
    creation keyed by the node_type.

    Parameters
    ----------
    data : dictionary
        The JSON data saved off when the Manager accessed the JSON file.
    """

    def __init__(self, json_data=None):
        self.data = json_data
        self.uml_id = {'count': 0}
        # print('MDTranslator Number of Keys on INIT')
        # print(len(self.uml_id.keys()))

    def get_uml_id(self, name=None):
        """Returns the UML_ID for the corresponding vertex name provided. If the
        name provided does not exist as a key in the UML_ID dictionary than a
        new key is created using that name and the value increments with
        new_<ith new number>.

        Parameters
        ----------
        name : string
            The Vertex.name attribute

        Notes
        -----
        This will be updated to become a nested dictionary
        with the first key being the name and the inner key will be the
        new_<ith new number> key and the value will be the UUID created
        by MagicDraw.
        """
        # TODO: write test function for this
        # if name == 'Miniature Inertial Measurement Unit':
        #     print('found one')
        #     print(self.uml_id[name])
        if name in self.uml_id.keys():
            return self.uml_id[name]
        else:
            self.uml_id.update({name: 'new_{0}'.format(self.uml_id['count'])})
            self.uml_id['count'] += 1
            return self.uml_id[name]

    def get_root_node(self):
        return self.data['Root Node']

    def get_cols_to_nav_map(self):
        return self.data['Columns to Navigation Map']

    def get_pattern_graph(self):
        return self.data['Pattern Graph Vertices']

    def get_pattern_graph_edges(self):
        return self.data['Pattern Graph Edges']

    def get_edge_type(self, index=None):
        return self.data['Pattern Graph Edge Labels'][index]

    def get_col_uml_names(self, column=None):
        return self.data['Columns to Navigation Map'][column][-1]

    def get_uml_metatype(self, node_key=None):
        return self.data['Vertex MetaTypes'][node_key]

    def get_uml_stereotype(self, node_key=None):
        return self.data['Vertex Stereotypes'][node_key]

    def get_uml_settings(self, node_key=None):
        uml_phrase = self.data['Vertex Settings'][node_key]

        try:
            uml_phrase.keys()
        except AttributeError:
            return node_key, uml_phrase

        key = next(iter(uml_phrase))
        return key, uml_phrase[key]
