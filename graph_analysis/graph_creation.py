import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from utils import (create_column_values_under,
                   create_column_values_space,
                   create_column_values_singleton)
from graph_objects import PropertyDiGraph


class Manager(object):
    """Assume the first filepath in excel_path is the "baseline" and all
    subsequent list indecies are ancestors of the baseline. The json_path
    contains the map to associate the columns of the Excel sheet to the
    dataframe columns, edge types and any missing columns."""

    def __init__(self, excel_path=[], json_path=None):
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


class Evaluator(object):

    # TODO: Consider moving function calls into init since they should be run
    # then
    def __init__(self, excel_file=None, translator=None):
        self.translator = translator
        self.df = pd.read_excel(excel_file)
        self.df.dropna(how='all', inplace=True)
        self.prop_di_graph = None
        self.root_node_attr_columns = set()

    # def validate_cols_keys_map(self):
    #     df_cols = set(self.df.columns)
    #     data_keys = set(translator.get_cols_to_nav_map())
    #     try:
    #         df_cols == data_keys

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
                        first_node_data=first_node_type,
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
                # TODO: Update this with rule from Bjorn.
                first_node_data = self.df.iloc[:, 0]
                second_node_data = self.df.loc[:, root_col_name]
                self.df[col] = create_column_values_space(
                    first_node_data=first_node_data,
                    second_node_data=second_node_data
                )
            else:
                col_data_vals = col
                root_col_name = self.translator.get_root_node()
                first_node_data = self.df.loc[:, root_col_name]
                second_node_data = [
                    col for count in range(len(first_node_data))]
                self.df[col] = create_column_values_singleton(
                    first_node_data=first_node_data,
                    second_node_data=second_node_data
                )

    def to_property_di_graph(self):
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
            self.prop_di_graph.add_nodes_from(GraphTemp)
            self.prop_di_graph.add_edges_from(GraphTemp.edges,
                                              edge_attribute=edge_type)

    @property
    def named_vertex_set(self):
        return self.prop_di_graph.get_vertex_set_named(df=self.df)

    @property
    def vertex_set(self):
        return self.prop_di_graph.vertex_set


class MDTranslator(object):

    def __init__(self, json_data=None):
        self.data = json_data

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
