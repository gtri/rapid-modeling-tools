import json
import os


def create_column_values_under(prefix=None,
                               first_node_data=None,
                               second_node_data=None,
                               suffix=''):
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


def create_column_values_singleton(first_node_data=None,
                                   second_node_data=None):
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


def aggregate_change_json():
    pass
