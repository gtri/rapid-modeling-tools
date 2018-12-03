import json
import os
from copy import copy
from itertools import combinations

import networkx as nx
import pandas as pd

from .graph_objects import PropertyDiGraph
from .utils import (associate_node_ids, create_column_values_singleton,
                    create_column_values_space, create_column_values_under,
                    distill_edges_to_nodes, get_new_column_name, match_changes,
                    new_as_old, object_dict_view, to_excel_df,
                    to_nto_rename_dict)

DATA_DIRECTORY = '../data/'


class Manager(object):
    """Class for raw data input and distribution to other classes.

    The Manager takes in a list of n excel filepaths and a single json_path.
    The first Excel file in the excel_path input variable is assumed to be the
    baseline to which all subsequent excel paths will be compared as ancestors.
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
        with open(self.json_path) as f:
            self.json_data = json.load(f)

    def create_evaluators(self):
        for excel_file in self.excel_path:
            self.evaluators.append(
                Evaluator(excel_file=excel_file,
                          translator=self.translator))

    def get_pattern_graph_diff(self):
        evaluator_dict = {evaluator: index for index, evaluator in enumerate(
            self.evaluators
        )}
        self.evaluator_change_dict = {}
        orig_eval = self.evaluators[0]

        for pair in combinations(self.evaluators, 2):
            # recast new names to be old but don't lost that info
            # want to somehow pass back the fact that new names were recast
            # have to update dict with new names
            eval_1_e_dict = pair[0].prop_di_graph.edge_dict
            eval_2_e_dict = pair[1].prop_di_graph.edge_dict

            if pair[0].has_rename and pair[1].has_rename:  # comparing changes
                pass  # so skip it
            elif pair[0].has_rename:  # This shouldn't happen since first
                # pair entry always be baseline based on how combos built
                # rename pair[0]
                # loop eval_1_e_dict and if source is a
                # new_to_old.keys() then make new key and associate the obj
                # do the same if is target. return the new dict and a dict to
                # replace the keys at the end.
                new_name_col = get_new_column_name(
                    original_df=orig_eval.df,
                    rename_df=pair[0].df_renames)
                new_name_dict = pair[0].df_renames.to_dict(orient='list')
                n_t_o, rename_changes = to_nto_rename_dict(
                    new_name=new_name_col,
                    new_name_dict=new_name_dict)
                # iterate through keys in new_to_old changing names edge dict
                eval_1_e_dict, reverse_map, vert_obj_map = new_as_old(
                    main_dict=eval_1_e_dict,
                    new_keys=n_t_o)
            elif pair[1].has_rename:
                # rename pair[1]
                new_name_col = get_new_column_name(
                    original_df=orig_eval.df,
                    rename_df=pair[1].df_renames)
                new_name_dict = pair[1].df_renames.to_dict(orient='list')
                n_t_o, rename_changes = to_nto_rename_dict(
                    new_name=new_name_col,
                    new_name_dict=new_name_dict)
                # iterate through keys in new_to_old changing names edge dict
                eval_2_e_dict, reverse_map, vert_obj_map = new_as_old(
                    main_dict=eval_2_e_dict,
                    new_keys=n_t_o)

            edge_set_one = pair[0].edge_set  # get baseline edge set
            edge_set_two = pair[1].edge_set  # get the changed edge set

            # remove common edges
            # have to do this with named edges.
            edge_set_one_set = {edge.named_edge_triple
                                for edge in edge_set_one}
            edge_set_two_set = {edge.named_edge_triple
                                for edge in edge_set_two}

            eval_one_unmatched_named = list(edge_set_one_set.difference(
                edge_set_two_set))
            eval_two_unmatched_named = list(edge_set_two_set.difference(
                edge_set_one_set
            ))
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

            eval_one_matches = match_changes(
                change_dict=eval_one_unmatch_pref)

            if pair[0].has_rename and pair[1].has_rename:  # comparing changes
                pass  # so nothing happened above.
            elif pair[0].has_rename:
                # Put stuff back how it was
                eval_1_e_dict, new_to_old, old_v_obj_map = new_as_old(
                    main_dict=eval_1_e_dict,
                    new_keys=reverse_map)
                vert_dict = pair[1].prop_di_graph.vertex_dict
                for key in old_v_obj_map.keys():
                    old_v_obj_map.update({key: vert_dict[key]})
                vert_obj_map.update(old_v_obj_map)
                n_t_o, rename_changes = to_nto_rename_dict(
                    new_name=new_name_col,
                    new_name_dict=new_name_dict,
                    str_to_obj_map=vert_obj_map)
                eval_one_matches[0].update(rename_changes)
            elif pair[1].has_rename:
                # undo change to nodes for comparisson purpose
                eval_2_e_dict, new_to_old, old_v_obj_map = new_as_old(
                    main_dict=eval_2_e_dict,
                    new_keys=reverse_map)
                vert_dict = pair[0].prop_di_graph.vertex_dict
                for key in old_v_obj_map.keys():
                    old_v_obj_map.update({key: vert_dict[key]})
                vert_obj_map.update(old_v_obj_map)
                n_t_o, rename_changes = to_nto_rename_dict(
                    new_name=new_name_col,
                    new_name_dict=new_name_dict,
                    str_to_obj_map=vert_obj_map)
                eval_one_matches[0].update(rename_changes)

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
                                          change_dict=eval_one_matches[0],
                                          evaluators=key)
            self.evaluator_change_dict.update(
                {key: changes_and_unstable})

        return self.evaluator_change_dict

    def changes_to_excel(self):
        # TODO: Find a more secure method.
        # If multiple files created in one
        # session than data will be lost and only the most recent changes
        # will be kept.
        # does create multiple sheets for each Manager.

        for key in self.evaluator_change_dict:
            outfile = 'Graph Model Differences {0}.xlsx'.format(key)
            outpath = os.path.join(DATA_DIRECTORY, outfile)
            writer = pd.ExcelWriter(outpath)
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
            df_output.to_excel(writer, sheet_name=key, index=False)

        writer.save()

    def graph_difference_to_json(self, new_col='',
                                 change_dict=None, evaluators=''):
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
        translator = self.translator
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
            elif isinstance(key, str):
                continue
            else:
                del_edge_json = key.edge_to_uml(op='delete',
                                                translator=translator)
                edge_del.append(del_edge_json)
                add_edge_json = value[0].edge_to_uml(op='replace',
                                                     translator=translator)
                edge_add.append(add_edge_json)

        change_list.extend(edge_del)
        change_list.extend(edge_add)
        change_list.extend(node_renames)

        json_out = {'modification targets': []}
        json_out['modification targets'].extend(change_list)
        with open(os.path.join(DATA_DIRECTORY,
                               'graph_difference_changes_{0}.json'.format(
                                   evaluators)),
                  'w') as outfile:
            json.dump(json_out, outfile, indent=4)

        return change_list


class Evaluator(object):
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
        # TODO: Why did I do this? save the file off as self.file then
        # call sheets_to_dataframe on self.
        self.sheets_to_dataframe(excel_file=excel_file)
        # self.df.dropna(how='all', inplace=True)
        self.prop_di_graph = None
        self.root_node_attr_columns = set()

    # def validate_cols_keys_map(self):
    #     df_cols = set(self.df.columns)
    #     data_keys = set(translator.get_cols_to_nav_map())
    #     try:
    #         df_cols == data_keys

    @property
    def has_rename(self):
        if not self.df_renames.empty:
            return True
        else:
            return False

    def sheets_to_dataframe(self, excel_file=None):
        # TODO: Generalize/Standardize this function
        xls = pd.ExcelFile(excel_file, on_demand=True)
        if len(xls.sheet_names) > 1:
            for sheet in sorted(xls.sheet_names):
                if 'composition' == sheet.lower():
                    self.df = pd.read_excel(excel_file, sheet_name=sheet)
                    self.df.dropna(how='all', inplace=True)
                elif 'composition ids' == sheet.lower():
                    self.df_ids = pd.read_excel(excel_file, sheet_name=sheet)
                    self.df_ids.set_index(self.df_ids.columns[0], inplace=True)
                    self.translator.uml_id.update(
                        self.df_ids.to_dict(
                            orient='dict')[self.df_ids.columns[0]])
                elif 'renames' == sheet.lower():
                    # TODO: Write test for this!
                    self.df_renames = pd.read_excel(excel_file,
                                                    sheet_name=sheet)
                    for row in self.df_renames.itertuples(index=False):
                        if row[0] in self.translator.uml_id.keys():
                            # then replace instances of this with those in 1
                            self.df.replace(to_replace=row[0], value=row[1],
                                            inplace=True)
                        elif row[1] in self.translator.uml_id.keys():
                            # same as above in other direction
                            self.df.replace(to_replace=row[1], value=row[0],
                                            inplace=True)
        else:
            self.df = pd.read_excel(excel_file)
            self.df.dropna(how='all', inplace=True)

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
                                        for i in range(len(first_node_data))]
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
            if self.df_ids is not None:
                nodes_to_add = associate_node_ids(
                    nodes=GraphTemp.nodes(),
                    attr_df=self.df_ids,
                    uml_id_dict=self.translator.get_uml_id)
            else:
                nodes_to_add = [
                    (node, {'ID': self.translator.get_uml_id(name=node)})
                    for node in GraphTemp.nodes()
                ]
            self.prop_di_graph.add_nodes_from(nodes_to_add)
            self.prop_di_graph.add_edges_from(GraphTemp.edges,
                                              edge_attribute=edge_type)

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


class MDTranslator(object):
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
