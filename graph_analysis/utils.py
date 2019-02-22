import json
import os
from copy import copy
from functools import reduce
from itertools import chain, count
from pathlib import Path
from random import shuffle

UML_ID = {
    'count': 0
}


# TODO: to selectively import one of the utils is the funtion that needs to do
# the importing.


def associate_node_id(tr, node=''):
    return {'id': tr.get_uml_id(name=node)}


def associate_successors(graph, node=''):
    return {'successors': [{'source': node,
                            'target': succ} for succ in graph.succ[node]]}


def associate_predecessors(graph, node=''):
    return {'predecessors': [{'source': pred,
                              'target': node}
                             for pred in graph.pred[node]]}


def associate_node_types_settings(
        df, tr, root_node_type, root_attr_cols, node=''):
    node_type_cols, node_attr_dict = get_node_types_attrs(
        df=df, node=node,
        root_node_type=tr.get_root_node(),
        root_attr_columns=root_attr_cols)
    node_types = {col for col in node_type_cols}

    settings_value = []

    for node_type in node_type_cols:
        vert_type, settings_val = tr.get_uml_settings(
            node_key=node_type)
        if settings_val and 'id' in settings_val:
            settings_value = get_setting_node_name_from_df(
                df=df, column=settings_val.split('-')[-1], node=node)
            settings = True
        else:
            settings_value = []

    type_setting_dict = {'settings_node': settings_value}
    type_setting_dict['attributes'] = node_attr_dict
    return type_setting_dict


def associate_renames(df_renames, tr, node):
    if any(new_nm.lower() in node.lower() for new_nm in df_renames.index):
        row_index = list(filter(lambda x: x in node, df_renames.index))
        old_name = df_renames.loc[row_index].get_values()
        new_old_tup = zip(row_index, chain(*old_name))
        original_name = reduce(
            lambda new, kv: new.replace(*kv), new_old_tup, node)
        original_id = tr.get_uml_id(name=original_name)
        return {'original_name': original_name,
                'original_id': original_id}
    else:
        return {'original_name': None,
                'original_id': None}


def build_dict(arg):
    one_dict = {}
    for ar in arg:
        one_dict.update(ar)
    return one_dict


def make_object(obj, kwargs):
    return obj(**kwargs)


def get_uml_id(name=None):
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
    new_<ith new number> key and the value behind that will be the UUID created
    by MagicDraw.
    """
    # TODO: make this a generator function
    if name in UML_ID.keys():
        return UML_ID[name]
    else:
        UML_ID.update({name: 'new_{0}'.format(UML_ID['count'])})
        UML_ID['count'] += 1
        return UML_ID[name]


def create_column_values_under(prefix=None, first_node_data=None,
                               second_node_data=None, suffix=''):
    """Returns the column values for an inferred dataframe column that has
    underscores in the column name.

    Parameters
    ----------
    prefix : string
        the characters that appear in the column name before the first '_'

    first_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        determined by picking the dataframe column with the same name as the
        string between the first underscore and the second.

    second_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        determined by picking the dataframe column with the same name as the
        string after the second underscore.

    suffix : string
        If the inferred column name contained a '-' followed by additional
        characters then those are treated as the suffix. Otherwise, it
        initalizes the the empty string and does nothing.

    Notes
    -----
    This function expects to receive a string like
    'A_composite owner_component-end1' with prefix=A,
    first_node_data=df['composite owner'], second_node_data=df['component'],
    and suffix='-end1'
    To produce the dataframe entires of the form:
    df['A_composite owner_component'] = A_<composite owner>_<component>
    """
    under = '_'
    dash = '-'
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [prefix
                    + under
                    + first_data.lower()
                    + under
                    + second_node_data[count].lower()
                    + suffix
                    ]

        column_values.extend(tmp_list)

    return column_values


def create_column_values_space(first_node_data=None,
                               second_node_data=None):
    """Returns the column values for an inferred dataframe column that has
    spaces in the column name.

    Parameters
    ----------
    first_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        determined by picking the first dataframe column. This will change
        once a more appropriate rule has been decided.

    second_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        determined by picking the dataframe column with the same name as the
        string after the space.

    Notes
    -----
    Up stream in the Evaluator.add_missing_columns() method, the Evaluator
    assumes that the first_node_data should come from the first column in the
    dataframe however, that can change and this function will be unaffected.
    If the first_node_data='CAR' and the second_node_data='BOOT' then the
    value returned would be 'car qua boot context'
    """
    space = ' '
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [first_data.lower()
                    + space
                    + 'qua'
                    + space
                    + second_node_data[count].lower()
                    + space
                    + 'context'
                    ]
        column_values.extend(tmp_list)

    return column_values


def create_column_values_singleton(
        first_node_data=None, second_node_data=None):
    """Returns the column values for an inferred dataframe column that is only
    one word.

    Parameters
    ----------
    first_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        determined by picking the dataframe column corresponding to the
        root node. This may change once a more appropriate rule has been
        decided.

    second_node_data : list
        List of data with a length equal to the number of rows in the dataframe
        built by repeating the desired column name until it has
        the same length as first_node_data.

    Notes
    -----
    Up stream in the Evaluator.add_missing_columns() method, the Evaluator
    assumes that the first_node_data should come from the root node of the
    dataframe however, that can change and this function will be unaffected.
    Furthermore, the second_node_data may change but at this stage the values
    are determined as explained above.
    If the first_node_data='CAR' and the second_node_data='context1' then the
    value returned would be 'car context1'
    """
    space = ' '
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [first_data.lower()
                    + space
                    + second_node_data[count].lower()
                    ]
        column_values.extend(tmp_list)

    return column_values


def create_column_values(col_name=None, data=None, aux_data=None):
    """Deprecated, I believe this may be removed without consequence."""
    column_values = []
    # check prefix for an underscore
    if '_' in col_name:
        # for the A_composite owner_component column and any with an _
        under = '_'
        chopped_str = col_name.split(sep='_')
        for count, item in enumerate(data):
            tmp_list = [chopped_str[0]
                        + under
                        + item.lower()
                        + under
                        + aux_data[count]]
            column_values.extend(tmp_list)
        return column_values
    else:
        # for the composite owner column and i guess all others...
        space = ' '
        for count, item in enumerate(data):
            tmp_list = [item.lower()
                        + space
                        + 'qua'
                        + space
                        + aux_data[count].lower()
                        + space
                        + 'context']
            column_values.extend(tmp_list)
        return column_values


def get_node_types_attrs(df=None, node=None,
                         root_node_type=None, root_attr_columns=None):
    """Returns the type of node that specified vertex is acting as and
    returns the attributes associated with that node if the passed node is
    a root node.

    Parameters
    ----------
    df : Pandas DataFrame
        The DataFrame that is read in from Excel and that creates the Graph.

    node : string
        The name of the graph vertex object that the node_types should be
        associated with.

    root_node_type : string
        The name of the root node type, which is the same as the column
        header for the DataFrame and the value behind the rootNode key in the
        json file.

    root_attr_columns : list of dictionaries
        The list of dictionaries created form the additional columns present
        in the excel file that are not part of the 'Columns to Navigation
        Map' and that should be associated to a node if that node is a root
        node.
    """
    node_attr_dict = {}
    mask = df == node
    node_mask_columns = df[mask].dropna(axis=1, how='all').columns
    node_type_columns = set(node_mask_columns).difference(
        root_attr_columns)

    root_attribute_list = list(root_attr_columns)

    # want to check if node in root nodes.values the column not the attrs.
    if node in df[root_node_type].values:
        root_node_df = df.loc[df[root_node_type] == node]
        node_attr_dict = root_node_df[root_attribute_list].dropna(
            axis=1, how='all').dropna(axis=0, how='all').to_dict('records')

    return node_type_columns, node_attr_dict


def match_changes(change_dict=None):
    # count = 0
    unstable_pairing = {}
    matched = {}
    str_dict = {}

    add_del = ('Added', 'Deleted')
    for suitor in change_dict:
        # TODO: generalize key skip method
        if suitor in add_del:
            str_dict[suitor] = change_dict[suitor]
            if not change_dict[suitor] and suitor not in add_del:
                deleted_set = set(
                    str_dict['Deleted']).add(set(suitor.named_edge_triple))
                update_dict = {'Deleted': list(deleted_set)}
                str_dict.update(update_dict)
            continue
        scores = match(*change_dict[suitor], current=suitor)
        matched[suitor] = [(item, scores[j])
                           for j, item in enumerate(change_dict[suitor])]
        matched[suitor] = sorted(matched[suitor],
                                 reverse=True, key=lambda elem: elem[1])
        if len(matched[suitor]) == 1:
            matched[suitor] = [matched[suitor][0][0]]
        elif len(matched[suitor]) > 1:
            first = matched[suitor][0][1]
            second = matched[suitor][1][1]
            if first > second:
                matched[suitor] = [matched[suitor][0][0]]
            else:
                i = 0
                j = 1
                while matched[suitor][i][1] == matched[suitor][j][1]:
                    i += 1
                    j += 1
                    if j >= len(matched[suitor]):
                        break
                unstable_pairing[suitor] = [matched[suitor][k][0]
                                            for k in range(j)]
                matched.pop(suitor)

    matched.update(str_dict)
    return (matched, unstable_pairing)


def match(*args, current=None):
    # current is the original edge and clone is the change
    # this function should only be getting nodes with the same edges
    # if I change this to assume nodes of the same edge attr then I can
    # send this function "equivalent edges"
    scores = []
    for clone in args:
        if current.edge_attribute == clone.edge_attribute:
            if ((current.source.id == clone.source.original_id)
                    or (current.target.id == clone.target.original_id)):
                scores.append(2)
            elif ((current.source.id == clone.source.id)
                    or (current.target.id == clone.target.id)):
                # TODO: check subgraph
                # if subgraph is isomorphic then return 2
                scores.append(1)
            else:
                scores.append(0)
        elif len(current.edge_attribute) > len(clone.edge_attribute):
            scores.append(-1)
        else:  # edge attribute of current is shorter than of clone
            scores.append(-2)
    return scores


def recast_new_names_as_old(edge_dict=None, rename_df=None, new_name=None):
    pass
    for key in edge_dict.keys():
        if key[0] in rename_df[new_name]:
            pass
            # replace key.source.name with the old name
            # record that the change has been made
        if key[1] in rename_df[new_name]:
            pass
            # replace key.target.name with old name
            # record that the change has been made
        # do nothing


# def associate_node_ids(nodes=None, attr_df=None, uml_id_dict=None):
#     # return a list of tuples with (node name, {id: <node id>})
#     # TODO: this function should do more. Need something for the else
#     # otherwise this silently corrupts data.
#     # This could be expanded to add attrs but its really only adding ids.
#     nodes_to_add = []
#     for node in nodes:
#         if node in attr_df.index:
#             attr = attr_df.loc[node].to_dict()
#             nodes_to_add.append((node, attr))
#         else:
#             attr = {'id': uml_id_dict(name=node)}
#             nodes_to_add.append((node, attr))
#
#     return nodes_to_add


def to_excel_df(data_dict=None, column_keys=None):
    # Idea: df_data = {'Edit 1': [keys for the changes], 'Edit 2': [values for
    # each key], 'Added': [all added data], 'Deleted': [all deleted data]
    edit_1 = column_keys[0]
    edit_2 = column_keys[1]
    df_data = {edit_1: [],
               edit_2: [], }
    for key in data_dict:
        if isinstance(key, str):
            if not data_dict[key]:
                continue
            try:
                check = data_dict[key][0].named_edge_triple
                df_data.update({key: [val.named_edge_triple
                                      for val in data_dict[key]]})
            except AttributeError:
                df_data.update({key: [val.name
                                      for val in data_dict[key]]})
        else:
            if len(data_dict[key]) > 1:
                repeat_key = [key.named_edge_triple for i in range(
                    len(data_dict[key]))]
                multiple_vals = [
                    val.named_edge_triple for val in data_dict[key]]
                # multiple_vals = data_dict[key]
                df_data[edit_1].extend(repeat_key)
                df_data[edit_2].extend(multiple_vals)
            else:
                df_data[edit_1].append(key.named_edge_triple)
                value = data_dict[key][0].named_edge_triple
                df_data[edit_2].append(value)

    return df_data


def object_dict_view(cipher=None):
    """ Just to make my life easier
    """
    decoded = {}
    for key in cipher.keys():
        if type(key) is str:
            try:
                decoded.update({key: [
                    item.named_edge_triple for item in cipher[key]]})
            except AttributeError:
                decoded.update({key: cipher[key]})
        else:
            decoded.update({key.named_edge_triple:
                            [item.named_edge_triple
                             for item in cipher[key]]})

    return decoded


def get_setting_node_name_from_df(df=None, column=None, node=None):
    """Returns a list of nodes located under the double mask defined first by
    masking the dataframe for the particular node of interest and dropping all
    of the empty rows, then by pulling out the node names from non-empty rows
    that are not equal to the input node. In other words we want to find all of
    nodes related to ours for a particular node_type. Since we wanted to know
    all of the nodes related to the input node of a particular node type, this
    was believed to be better than searching the neghiborhood and throwing out
    any nodes that did not have the same typeself.

    Parameters
    ----------
    df : Pandas DataFrame
        The DataFrame that is read in from Excel and that creates the Graph.

    node : string
        The name of the graph vertex object that we are interested in locating
        the related nodes of, of a particular type.

    column : string
        The name of the column of interest that we are interested in.
        The name of that column was stript from a vertex settings key asking
        for an id<column name>.

    Notes
    -----
    This function returns a python list of names of nodes that are found in the
    dataframe under the column header 'column' and relating to the input
    node.
    """

    mask = df == node
    masked_df = df[mask].dropna(axis=0, how='all')
    return df.where(
        masked_df.isnull()).dropna(axis=0, how='all')[column].tolist()


def get_new_column_name(original_df=None, rename_df=None):
    for column in rename_df.columns:
        new_vals = rename_df[column].tolist()
        masked = original_df.isin(new_vals)
        if not masked.any().any():
            return column


def replace_new_with_old_name(changed_df=None, rename_df=None, new_name=None):
    old_col = set(rename_df.columns).difference({new_name})
    old_col = list(old_col)[0]  # what happens if list of more than 2 entries?
    for node_name in rename_df[new_name]:
        idx = rename_df.index[rename_df[new_name] == node_name]
        old_name = rename_df.loc[idx, old_col]
        mask = changed_df == node_name
        changed_df[mask] = old_name.tolist()[0]

    return changed_df


def new_as_old(main_dict=None, new_keys=None):
    reverse_map = {}
    new_key_set = {key for key in new_keys.keys()}
    vert_obj_map = {}
    for key in main_dict:
        if key[0] in new_key_set:
            old_name = new_keys[key[0]]
            new_key = list(copy(key))
            new_key[0] = old_name
            new_key = tuple(new_key)
            vert_obj_map[key[0]] = main_dict[key].source
            main_dict[key].source.name = old_name
            reverse_map.update({old_name: key[0]})
            main_dict[new_key] = main_dict.pop(key)
        elif key[1] in new_key_set:
            old_name = new_keys[key[1]]
            new_key = list(copy(key))
            new_key[1] = old_name
            new_key = tuple(new_key)
            vert_obj_map[key[1]] = main_dict[key].target
            main_dict[key].target.name = old_name
            reverse_map.update({old_name: key[1]})
            main_dict[new_key] = main_dict.pop(key)

    return main_dict, reverse_map, vert_obj_map


def to_nto_rename_dict(new_name=None, new_name_dict=None,
                       str_to_obj_map=None):
    new_names_list = new_name_dict[new_name]
    # old_names_list = [
    #     value
    #     for key, value in new_name_dict.items() if key is not new_name
    #     ]
    # Why does the above work in jupyter but not here?
    old_obj_list = []
    new_obj_list = []
    for key, value in new_name_dict.items():
        if key is not new_name:
            if str_to_obj_map:
                for val in value:
                    if val in str_to_obj_map.keys():
                        old_obj_list.append(str_to_obj_map[val])
                    else:
                        continue
                for val in new_names_list:
                    if val in str_to_obj_map.keys():
                        new_obj_list.append(str_to_obj_map[val])
                    else:
                        continue

            old_names_list = value
            old_key = key

    new_to_old_dict = dict(zip(new_names_list, old_names_list))

    if str_to_obj_map:
        rename_changes = {'Rename {0}'.format(new_name): new_obj_list,
                          'Rename {0}'.format(old_key): old_obj_list}
    else:
        rename_changes = {'Rename {0}'.format(new_name): new_names_list,
                          'Rename {0}'.format(old_key): old_names_list}

    return new_to_old_dict, rename_changes


def distill_edges_to_nodes(edge_matches=None):
    for key in edge_matches:
        if not isinstance(key, str):
            source_cond = key.source.name == edge_matches[key][0].source.name
            target_cond = key.target.name == edge_matches[key][0].target.name
            if source_cond and target_cond:
                source_value = edge_matches[key][0].source
                target_value = edge_matches[key][0].target
                source_key = key.source
                target_key = key.target
                edge_matches[key] = source_value
                edge_matches[source_key] = edge_matches.pop(key)
                edge_matches[target_key] = target_value
            elif source_cond:
                # replace the key here with key.target and val with
                # value.target
                target_value = edge_matches[key][0].target
                nk = key.target
                edge_matches[key] = target_value
                edge_matches[nk] = edge_matches.pop(key)
            elif target_cond:
                # replace key with key.source and value with
                # with value.target
                source_value = edge_matches[key][0].source
                nk = key.source
                edge_matches[key] = source_value
                edge_matches[nk] = edge_matches.pop(key)
    return edge_matches


def to_uml_json_node(**kwargs):
    return {
        'id': kwargs['id'],
        'ops': [
            {
                'op': kwargs['op'],
                'name': kwargs['name'],
                'path': kwargs['path'],
                'metatype': kwargs['metatype'],
                'stereotype': kwargs['stereotype'],
                'attributes': kwargs['attributes'],
            }
        ]
    }


def to_uml_json_decorations(**kwargs):
    return {
        'id': kwargs['id'],
        'ops': [
            {
                'op': kwargs['op'],
                'path': '/' + kwargs['path'],
                'value': kwargs['value'],
            }
        ]
    }


def to_uml_json_edge(**kwargs):
    return {
        'id': kwargs['id'],
        'ops': [
            {
                'op': kwargs['op'],
                'path': '/m2/' + kwargs['path'],
                'value': kwargs['value']
            }
        ]
    }


def truncate_microsec(curr_time=None):
    time_str = curr_time.strftime('%H %M %S %f')
    return time_str[0:-3]
