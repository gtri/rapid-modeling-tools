from graph_objects import Vertex


def get_edge_type(data=None, index=None):
    return data['Pattern Graph Edge Labels'][index]


def get_composite_owner_names(prefix=None, data=None):
    # This seems like column_values will remember the items on multiple calls
    # tested and this is not an issue
    column_values = []
    for index, count in enumerate(data):
        tmp_list = [prefix + ' ' + str(data.keys()[
            index]) for i in range(count)]
        column_values.extend(tmp_list)
    return column_values


def get_a_composite_owner_names(prefix=None, data=None):
    # This seems like column_values will remember the items on multiple calls
    column_values = []
    under = '_'
    chopped_str = prefix.split(sep='_')
    for index, count in enumerate(data):
        tmp_list = [chopped_str[0] + under
                    + str(data.keys()[index]) + under
                    + chopped_str[-1] for i in range(count)]
        column_values.extend(tmp_list)
    return column_values


def create_vertex_objects(df=None, graph=None):
    vertex_list = []
    for node in graph.nodes:
        mask = df == node
        print(df[mask])
        node_type_columns = df[mask].dropna(
            axis=1, how='all').columns
        node_types = {col for col in node_type_columns}
        successors = graph.succ[node]
        predecessors = graph.succ[node]
        vertex = Vertex(name=node, node_types=node_types,
                        successors=successors, predecessors=predecessors)
        vertex_list.append(vertex)

    return vertex_list
