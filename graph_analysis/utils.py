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
        node_type_columns = df[mask].dropna(
            axis=1, how='all').columns
        node_types = {col for col in node_type_columns}
        vertex = Vertex(name=node, node_types=node_types,
                        successors=graph.succ[node],
                        predecessors=graph.pred[node])
        vertex_list.append(vertex)

    return vertex_list


def aggregate_change_json():
    pass


# def get_spanning_tree(root_node=None,
#                       root_node_type=None,
#                       tree_pattern=None,
#                       tree_edge_pattern=None):
#     pass
#     # assuming that tree_pattern and tree_edge_pattern are the values behind
#     # the JSON keys that describe this pattern
#     # 'Pattern Spanning Tree Edges' and 'Pattern Spanning Tree Edge Labels'
#     span_tree = [(tuple(pair), tree_edge_pattern[index])
#                  for index, pair in enumerate(tree_pattern)]
#     span_tree_set = set(span_tree)
#
#     branch_set = set()

    # for branch in span_tree:
    #     if root_node_type in branch[0][0]:
    #         pass
    #         # then we need to search its sucessors for nodes of the same type
    #         # with the same edge edge_attribute
    #     elif root_node_type in branch[0][1]:
    #         pass
    # then we need to search for predecessors for nodes of the same
    # type with the same edge_attribute as the tuple.
    # find which tuple contains my root node and the position of
    # the deisred root node type in my tuple i.e. is it position 0 or 1
    # position 1 means that I must find the predecessor of this node in the 0
    # position of that has the same edge type as I would have
    # Once I know that I am looking for a predecessor, call back to the vertex
    # object and compare my neghiborhood for verticies of the type i am seeking
    # and for for edges of the specified type given by the span_tree.
    # continue like this until we have iterated the entire spanning tree or
    # we are unable to find any more connected nodes.
