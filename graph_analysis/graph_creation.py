import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from utils import (get_edge_type, get_composite_owner_names,
                   get_a_composite_owner_names)
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
        self.evaluators = []

    def get_json_data(self):
        with open(self.json_path) as f:
            self.json_data = json.load(f)

    def create_evaluators(self):
        for excel_file in self.excel_path:
            self.evaluators.append(
                Evaluator(excel_file=excel_file,
                          json_data=self.json_data))


class Evaluator(object):

    def __init__(self, excel_file=None, json_data=None):
        self.json_data = json_data
        self.df = pd.read_excel(excel_file)
        self.df.dropna(how='all', inplace=True)
        self.prop_di_graph = None

    def rename_excel_columns(self):
        for column in self.df.columns:
            # print(self.json_data['Columns to Navigation Map'])
            new_column_name = self.json_data[
                'Columns to Navigation Map'][column][-1]
            self.df.rename(columns={column: new_column_name}, inplace=True)

    def add_missing_columns(self):
        # TODO: make data agnostic
        columns_to_create = set(self.json_data[
            'Pattern Graph Vertices']).difference(
            set(self.df.columns))
        root_node = self.json_data['Root Node']
        root_node_values = self.df[root_node]

        for col in columns_to_create:
            # TODO: find a better way
            if col == 'composite owner':
                self.df[col] = get_composite_owner_names(
                    prefix=col, data=root_node_values)
            elif col == 'A_"composite owner"_component':
                self.df[col] = get_a_composite_owner_names(
                    prefix=col, data=root_node_values)

    def to_property_di_graph(self):
        self.prop_di_graph = PropertyDiGraph()
        for index, pair in enumerate(self.json_data['Pattern Graph Edges']):
            edge_type = get_edge_type(data=self.json_data, index=index)
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
