import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from utils import (get_edge_type, get_composite_owner_names,
                   get_a_composite_owner_names)


with open('../data/PathMasterExpanded.json') as f:
    data = json.load(f)

df_original = pd.read_excel('../data/Composition Example.xlsx')
df_original.dropna(how='all', inplace=True)
# probably needs generalizing
original_first_col_header = list(data[
    'Columns to Navigation Map'].keys())[0]
principal_component_set = set(df_original[original_first_col_header])

for column in df_original.columns:
    new_column_name = data['Columns to Navigation Map'][column][-1]
    df_original.rename(columns={column: new_column_name}, inplace=True)

columns_to_create = set(data['Pattern Graph Vertices']).difference(
    set(df_original.columns))

composite_thing_series = df_original['Composite Thing'].value_counts(
    sort=False)

for col in columns_to_create:
    if col == 'composite owner':
        df_original[col] = get_composite_owner_names(
            prefix=col, data=composite_thing_series)
    elif col == 'A_"composite owner"_component':
        df_original[col] = get_a_composite_owner_names(
            prefix=col, data=composite_thing_series)

plt.figure(num=1, figsize=(30, 30))
G = nx.DiGraph()

for index, pair in enumerate(data['Pattern Graph Edges']):
    edge_type = get_edge_type(data=data, index=index)
    df_original[edge_type] = edge_type
    df_temp = df_original[[pair[0], pair[1], edge_type]]
    Graph_temp = nx.from_pandas_edgelist(
        df=df_temp, source=pair[0],
        target=pair[1], edge_attr=edge_type)
    edge_label_dict = {'edge type': edge_type}
    G.add_nodes_from(Graph_temp)
    G.add_edges_from(Graph_temp.edges, attr=edge_label_dict)

# print(len(G.nodes))
# pos = nx.spring_layout(G)
nx.draw_networkx(G, arrowsize=50, node_size=1000)
# edge_labels = nx.get_edge_attributes(G, 'edge type')
# nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
# plt.savefig('TestGraph.png')
# print(G['hub'])
print(G.get_edge_data('Car', 'hub'))
plt.show()
