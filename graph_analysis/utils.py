import json
import os
from copy import copy
from functools import reduce
from itertools import chain, count
from pathlib import Path
from random import shuffle


# TODO: to selectively import one of the utils is the funtion that needs to do
# the importing.


def associate_node_id(tr, node=""):
    """
    Returns a dictionary with key 'id' and value as the ID associated
    with the node string.
    """
    return {"id": tr.get_uml_id(name=node)}


def associate_successors(graph, node=""):
    """
    Returns a dictionary with outer key 'successors' securing a value list
    of dictionaries associating the source, target and edge_attribute
    with the corresponding Vertex.name strings for each successor to the
    passed node.
    """
    return {
        "successors": [
            {
                "source": node,
                "target": succ,
                "edge_attribute": graph.succ[node][succ]["edge_attribute"],
            }
            for succ in graph.succ[node]
        ]
    }


def associate_predecessors(graph, node=""):
    """
    Returns a dictionary with outer key 'predecessors' securing a value
    list of dictionaries associating the source, target and
    edge_attribute with the corresponding Vertex.name strings for each
    predecessor to the passed node.
    """
    return {
        "predecessors": [
            {
                "source": pred,
                "target": node,
                "edge_attribute": graph.pred[node][pred]["edge_attribute"],
            }
            for pred in graph.pred[node]
        ]
    }


def associate_node_types_settings(df, tr, root_attr_cols, node=""):
    """
    Packages the settings, node types and attribtues of each node if they
    exist.

    Gets the columns where the node shows up and get the attribute
    columns if the node occupies a role as a root node. For each node type
    that the vertex in question posesses, check the settings section of
    the JSON for metadata and associate it to the node if it exists.
    Finally, return the settings, node types and attributes as a
    dictionary to be associated on the vertex object at creation.

    Parameters
    ----------
    df : Panadas DataFrame
        The DataFrame that was read in from the spreadsheet and populated by
        the filling of the subgraph according to the JSON.

    tr : MDTranslator
        MDTranslator associated with the change Evaluator.

    root_attr_cols : set
        Collection of DataFrame columns that do not show up in the JSON
        specification and thus should be interpreted as attributes for the
        root node.

    node : str
        Name of the node to get the types and settings for.

    Returns
    -------
    type_setting_dict : dict
        dictionary containing keys for the settings, node types and a
        list of dicts behind the attributes key.
    """
    node_type_cols, node_attr_dict = get_node_types_attrs(
        df=df,
        node=node,
        root_node_type=tr.get_root_node(),
        root_attr_columns=root_attr_cols,
    )
    node_types = {col for col in node_type_cols}

    settings = []

    for node_type in node_type_cols:
        path_val, settings_val = tr.get_uml_settings(node_key=node_type)
        if settings_val:
            if "id" in settings_val:
                settings_value = get_setting_node_name_from_df(
                    df=df, column=settings_val.split("-")[-1], node=node
                )
                settings.extend(
                    [{path_val: value} for value in settings_value]
                )
            elif isinstance(settings_val, list) and any(
                "id" in item for item in settings_val
            ):  # TODO: Test This
                id_calls = [
                    id.split("-")[-1]
                    for id in filter(lambda x: "id" in x, settings_val)
                ]
                for col in id_calls:
                    settings_value = get_setting_node_name_from_df(
                        df=df, column=col, node=node
                    )
                    settings.extend(
                        [{path_val: [value]} for value in settings_value]
                    )
            else:
                settings.append({path_val: settings_val})
        else:
            settings = []

    type_setting_dict = {"settings": settings, "node_types": list(node_types)}
    type_setting_dict["attributes"] = node_attr_dict
    return type_setting_dict


def associate_renames(df_renames, tr, node):
    """
    If a node has a rename, as identified in the df_renames then associate
    the original name and ID to the renamed node.

    Parameters
    ----------
    df_renames: Pandas DataFrame
        The dataframe corresponding to the renames sheet found in a
        provided change Excel sheet.

    tr : MDTranslator
        MagicDraw Translator object associated to the current Evaluator.

    node : str
        Name of the current node to associate the renames to.

    Returns
    -------
    original_dict : dict
        If node identifies as a rename then return a dictionary of the
        original name and original id. Otherwise return a dict with values
        None.

    Notes
    -----
    If the node argument matches a name in the index of the renames
    dataframe (the new names stored as the index), then get the original
    name and generate the original name using the old name from the
    dataframe and the node string as a string template replacing the new
    name with the old.

    Certain derived names require additional care to ensure that the
    original name generated here matches the original name found in the
    original Evaluator.
    """
    # If any part of the node string is in the index of the rename dataframe
    # then build the original name.
    if any(new_nm.lower() in node.lower() for new_nm in df_renames.index):
        row_index = list(
            filter(lambda x: x.lower() in node, df_renames.index)
        )
        old_name = df_renames.loc[row_index].get_values()
        row_index = [x.lower() for x in row_index]
        old_name = [x.lower() for x in chain(*old_name)]
        new_old_tup = zip(row_index, old_name)
        # take the original name and the current name and use the current name
        # as a template to build up the old name.
        original_name = reduce(
            lambda new, kv: new.replace(*kv), new_old_tup, node
        )
        if node == original_name:
            row_index = list(filter(lambda x: x in node, df_renames.index))
            old_name = df_renames.loc[row_index].get_values()
            new_old_tup = zip(row_index, chain(*old_name))
            original_name = reduce(
                lambda new, kv: new.replace(*kv), new_old_tup, node
            )

        # Get the ID of node and the ID of the original node name that was
        # generated above.
        original_id = tr.get_uml_id(name=original_name)
        tr.uml_id.update({node: original_id})
        return {"original_name": original_name, "original_id": original_id}
    else:
        return {"original_name": None, "original_id": None}


def build_dict(arg):
    """
    Helper function to the Evaluator.to_property_di_graph() method that
    packages the dictionaries returned by the "associate_" family of
    functions and then supplies the master dict (one_dict) to the Vertex
    obj as **kwargs.
    """
    # helper function to the Evaluator.to_property_di_graph() method that
    # packages the dictionaries returned by the "associate_" family of
    # functions and then supplies the master dict (one_dict) to the Vertex
    # obj as **kwargs
    one_dict = {}
    for ar in arg:
        one_dict.update(ar)
    return one_dict


def make_object(obj, kwargs):
    """
    Applies the kwargs to the object, returns obj(**kwargs)
    """
    return obj(**kwargs)


def create_column_values_under(
    prefix=None, first_node_data=None, second_node_data=None, suffix=""
):
    """
    Returns the column values for an inferred dataframe column that has
    underscores in the column name.

    Parameters
    ----------
    prefix : string
        the characters that appear in the column name before the first '_'

    first_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe determined by picking the dataframe column with the same
        name as the string between the first underscore and the second.

    second_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe determined by picking the dataframe column with the same
        name as the string after the second underscore.

    suffix : string
        If the inferred column name contained a '-' followed by additional
        characters then those are treated as the suffix. Otherwise, it
        initalizes the the empty string and does nothing.

    Returns
    -------
    column_values : list of strs
        List with length equal to the length of first_node_data whose
        elements represent the inferred node names for a column name
        that includes underscores.

    Notes
    -----
    This function expects to receive a string like
    'A_composite owner_component-end1' with prefix=A,
    first_node_data=df['composite owner'],
    second_node_data=df['component'], and suffix='-end1'
    To produce the dataframe entires of the form:
    df['A_composite owner_component'] = A_<composite owner>_<component>
    """
    under = "_"
    dash = "-"
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [
            prefix
            + under
            + first_data.lower()
            + under
            + second_node_data[count].lower()
            + suffix
        ]

        column_values.extend(tmp_list)

    return column_values


def create_column_values_space(first_node_data=None, second_node_data=None):
    """
    Returns the column values for an inferred dataframe column that has
    spaces in the column name.

    Parameters
    ----------
    first_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe determined by picking the first dataframe column. This
        will change once a more appropriate rule has been decided.

    second_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe determined by picking the dataframe column with the same
        name as the string after the space.

    Returns
    -------
    column_values : list of strs
        List with length equal to the length of first_node_data whose
        elements represent the inferred node names for a column name
        that includes spaces.

    Notes
    -----
    Up stream in the Evaluator.add_missing_columns() method, the
    Evaluator assumes that the first_node_data should come from the first
    column in the dataframe however, that can change and this function
    will be unaffected. If the first_node_data='CAR' and the
    second_node_data='BOOT' then the value returned would be
    'car qua boot context'
    """
    space = " "
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [
            first_data.lower()
            + space
            + "qua"
            + space
            + second_node_data[count].lower()
            + space
            + "context"
        ]
        column_values.extend(tmp_list)

    return column_values


def create_column_values_singleton(
    first_node_data=None, second_node_data=None
):
    """
    Returns the column values for an inferred dataframe column that is
    only one word.

    Parameters
    ----------
    first_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe determined by picking the dataframe column corresponding
        to the root node. This may change once a more appropriate rule has
        been decided.

    second_node_data : list
        List of data with a length equal to the number of rows in the
        dataframe built by repeating the desired column name until it has
        the same length as first_node_data.

    Returns
    -------
    column_values : list of strs
        List with length equal to the length of first_node_data whose
        elements represent the inferred node names for a column name
        that is one word long with no special characters.

    Notes
    -----
    Up stream in the Evaluator.add_missing_columns() method, the Evaluator
    assumes that the first_node_data should come from the root node of the
    dataframe however, that can change and this function will be
    unaffected. Furthermore, the second_node_data may change but at this
    stage the values are determined as explained above.
    If the first_node_data='CAR' and the second_node_data='context1' then the
    value returned would be 'car context1'
    """
    space = " "
    column_values = []
    for count, first_data in enumerate(first_node_data):
        tmp_list = [
            first_data.lower() + space + second_node_data[count].lower()
        ]
        column_values.extend(tmp_list)

    return column_values


def get_node_types_attrs(
    df=None, node=None, root_node_type=None, root_attr_columns=None
):
    """
    Returns the type of node that specified vertex is acting as and
    returns the attributes associated with that node if the passed node is
    a root node.

    Parameters
    ----------
    df : Pandas DataFrame
        The DataFrame that is read in from Excel and that creates the
        Graph.

    node : str
        The name of the graph vertex object that the node_types should be
        associated with.

    root_node_type : str
        The name of the root node type, which is the same as the column
        header for the DataFrame and the value behind the rootNode key in
        the json file.

    root_attr_columns : list of dicts
        The list of dictionaries created form the additional columns
        present in the excel file that are not part of the
        'Columns to Navigation Map' and that should be associated to a
        node if that node is a root node.

    Returns
    -------
    node_type_columns : set
        Columns that contain the node and are not attribute columns.

    node_attr_dict : list of dicts
        List of dictionaries containing the attributes associated with
        the `node` if the `node` is a root node. Each dictionary within
        the list represents one row of attributes from the DataFrame.

    Notes
    -----
    Columns in the Excel, and by extension the DataFrame, that do not
    correspond directly to a column in the 'Columns to Navigation Map' are
    marked as "Attribute Columns". Attribute columns are associated to the
    root node by row, since all of the data in a row is assumed to be
    related to the root node.
    """
    node_attr_dict = {}
    mask = df == node
    node_mask_columns = df[mask].dropna(axis=1, how="all").columns
    node_type_columns = set(node_mask_columns).difference(root_attr_columns)
    root_attribute_list = list(root_attr_columns)

    # want to check if node in root nodes.values the column not the attrs.
    if node in df[root_node_type].values:
        root_node_df = df.loc[df[root_node_type] == node]
        node_attr_dict = (
            root_node_df[root_attribute_list]
            .dropna(axis=1, how="all")
            .dropna(axis=0, how="all")
            .to_dict("records")
        )

    return node_type_columns, node_attr_dict


def match_changes(change_dict=None):
    """
    Attempts to match the original edge to its changed counter part.

    Accomplished using ideas from the stable marriage algorithm. The first
    part of the for loop skips all keys of type string and allocates the
    added edges to the added pile and the deleted edges to the deleted
    pile. Starting at scores, each original edge that does not show up
    exactly in the changed edge set is paird up with all change edges
    corresponding to the same edge type as the original. Then the list of
    potential matches (change edges) is compared to the original and
    scored based on the match() function. Once scored, only keep the
    highest scores and discard the rest, clean up the data. Return the
    confident matches and the unstable matches.

    Confident match {('Car', 'engine', 'owner'): [(('Vehicle', 'engine',
    'owner'), 2)]}
    Unstable match {('Car', 'engine', 'owner'): [(('Engine', 'engine',
    'owner'), 1)], (('Car', 'wheel', 'owner'), 1), ...}

    Parameters
    ----------
    change_dict: dict
        Each key is an edge from the original graph. The value is a list
        of edges from the change edge set with the same edge attribute as
        the key.

    Returns
    -------
    matched : dict
        Dictionary of matched changes. Two string keys, one for Added and
        one for Deleted nodes; the rest of the keys are DiEdge objects.
        All values consist of lists of DiEdge objects. Furthermore, values
        corresponding to DiEdge object keys have length one while the
        Added and Deleted keys may have multi-element lists.

    unstable_pairing : dict
        Keys are DiEdge objects for which there was no global maximum
        amongst the scores. All objects returned in the value have the
        same score and are left for the user to include or exclude.

    See Also
    -----
    match
    """
    unstable_pairing = {}
    matched = {}
    str_dict = {}

    add_del = ("Added", "Deleted")
    for suitor in change_dict:
        # TODO: generalize key skip method
        if suitor in add_del:
            str_dict[suitor] = change_dict[suitor]
            if not change_dict[suitor] and suitor not in add_del:
                # TODO: I think this will cause issues in the json output.
                deleted_set = set(str_dict["Deleted"]).add(set(suitor))
                update_dict = {"Deleted": list(deleted_set)}
                str_dict.update(update_dict)
            continue
        scores = match(*change_dict[suitor], current=suitor)
        matched[suitor] = list(zip(change_dict[suitor], scores))
        matched[suitor] = sorted(
            matched[suitor], reverse=True, key=lambda elem: elem[1]
        )
        # TODO: Consider using Reduce or filter.
        # Could probably use reduce instead of this if else with a while loop
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
                unstable_pairing[suitor] = [
                    matched[suitor][k][0] for k in range(j)
                ]
                matched.pop(suitor)

    matched.update(str_dict)
    return (matched, unstable_pairing)


def match(*args, current=None):
    """
    Provides the metric for determining the confidence level that a
    current change edge represents a change to the original edge.

    Parameters
    ----------
    args : list
        list of change edges that have the same edge type as the "current"
        edge.

    current : DiEdge
        Edge to which all the edges in `args` will be compared against.

    Returns
    -------
    scores : list of ints
        List of integers corresponding to the confidence level that
        the current list item from args is the changed version of
        current.

    See also
    --------
    match_changes
    """
    # current is the original edge and clone is the change
    # this function should only be getting nodes with the same edges
    # if I change this to assume nodes of the same edge attr then I can
    # send this function "equivalent edges"
    scores = []
    for clone in args:
        if current.edge_attribute == clone.edge_attribute:
            source_condit = (
                clone.source.original_id == current.source.id
                or clone.source.id == current.source.id
            )
            target_condit = (
                clone.target.original_id == current.target.id
                or clone.target.id == current.target.id
            )
            if source_condit and target_condit:
                scores.append(2)
                return scores
            elif source_condit or target_condit:

                scores.append(1)
            else:
                # TODO: check subgraph/call is_similar
                # if subgraph is isomorphic then return 2
                scores.append(0)
        elif len(current.edge_attribute) > len(clone.edge_attribute):
            scores.append(-1)
        else:  # edge attribute of current is shorter than of clone
            scores.append(-2)
    return scores


def is_similar(current=None, clone=None):
    pass
    # can write a function for this in the case that the score will be 1
    # this function will check successors and predecessors for similarity but


def to_excel_df(data_dict=None, column_keys=None):
    """
    Format the changes in the change and unstable pairs dictionary for an
    Excel output through a DataFrame.

    Create the column names and then begin
    unpacking the data_dict. Depending on the key and the length of the
    value, sort the data into the appropriate data column. After sorting
    all of the data, return the DataFrame.

    Parameters
    ----------
    data_dict : dict
        Dictionary with keys for the confidently matched changes and the
        unstable pairs.

    column_keys : list
        list of column names. The names of the edit columns correspond to the
        orginal Evaluator (1) and the change Evaluator (>1).

    Returns
    -------
    df_data : Pandas DataFrame
        DataFrame that can be written to Excel using Pandas.

    Notes
    -----
    Evaluator.changes_to_excel() calls this function to package the
    dictionary into a dataframe to be written out to Excel using the
    builtin Pandas behavior.
    """
    # Idea: df_data = {'Edit 1': [keys for the changes], 'Edit 2': [values for
    # each key], 'Added': [all added data], 'Deleted': [all deleted data]
    edit_1 = column_keys[0]
    edit_2 = column_keys[1]
    unstab_original = "Unstable Matches Original"
    unstab_change = "Unstable Matches Change"
    df_data = {edit_1: [], edit_2: [], unstab_original: [], unstab_change: []}
    for key in data_dict:
        if isinstance(key, str):
            if not data_dict[key]:
                continue
            try:
                check = data_dict[key][0].named_edge_triple
                df_data.update(
                    {key: [val.named_edge_triple for val in data_dict[key]]}
                )
            except AttributeError:
                df_data.update({key: [val.name for val in data_dict[key]]})
        else:
            if len(data_dict[key]) > 1:
                repeat_key = [
                    key.named_edge_triple for i in range(len(data_dict[key]))
                ]
                multiple_vals = [
                    val.named_edge_triple for val in data_dict[key]
                ]
                # multiple_vals = data_dict[key]
                df_data[unstab_original].extend(repeat_key)
                df_data[unstab_change].extend(multiple_vals)
            else:
                df_data[edit_1].append(key.named_edge_triple)
                value = data_dict[key][0].named_edge_triple
                df_data[edit_2].append(value)

    return df_data


def get_setting_node_name_from_df(df=None, column=None, node=None):
    """
    Returns a list of nodes located under the double mask defined first by
    masking the dataframe for the particular node of interest and dropping
    all of the empty rows, then by pulling out the node names from
    non-empty rows that are not equal to the input node.

    In other words we want to find all of
    nodes related to ours for a particular node_type. Since we wanted to
    know all of the nodes related to the input node of a particular node
    type, this was believed to be better than searching the neghiborhood
    and throwing out any nodes that did not have the same typeself.

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

    Returns
    -------
    list_of_names : list
        This function returns a python list of names of nodes that are
        found in the dataframe under the column header 'column' and
        relating to the input node.
    """

    mask = df == node
    masked_df = df[mask].dropna(axis=0, how="all")
    return (
        df.where(masked_df.isnull())
        .dropna(axis=0, how="all")[column]
        .tolist()
    )


def make_string(attr_dict, create=False):
    """
    Create a string from the to_uml_json_<operation> method to aid the
    remove_duplicates method.

    Parameters
    ----------
    attr_dict : dict
        Dictionary output from the Vertex and DiEdge ReporterMixins.

    create : Bool
        Flag to change keys.

    Returns
    -------
    string_representation : str
        String representation of node_id edge_attribute other_node_id

    See Also
    --------
    VertexReporterMixin
    DiEedgeReporterMixin
    """
    # attr_dict follows to to_uml_json_* structure
    if create:
        ops_in_value = "name"
    else:
        ops_in_value = "value"
    if isinstance(attr_dict["ops"][0][ops_in_value], list):
        e_a_value = attr_dict["ops"][0][ops_in_value][0]
    else:
        e_a_value = attr_dict["ops"][0][ops_in_value]
    return (
        str(attr_dict["id"])
        + str(e_a_value)
        + str(attr_dict["ops"][0]["path"])
    )


def remove_duplicates(input, create=False):
    """
    Removes duplicate JSON instructions.

    Parameters
    ----------
    input : list of dicts
        List of dicts containing JSON instructions from the
        to_uml_json_<operation> methods associated to the ReporterMixin
        classes.

    create : Bool
        Flag to pass to the make_string method.

    Returns
    -------
    filtered_list : list of dicts
        Returns input with all duplicate items removed.

    See Also
    --------
    make_string
    VertexReporterMixin
    DiEedgeReporterMixin
    """
    # input is a list of dicts
    seen = set()
    filtered_list = []
    for attr_dict in input:
        str_repr = make_string(attr_dict, create=create)
        if str_repr not in seen:
            seen.add(str_repr)
            filtered_list.append(attr_dict)

    return filtered_list


def to_uml_json_node(**kwargs):
    """
    Create dict to be converted to JSON for consumption by Player Piano.

    See Also
    --------
    VertexReporterMixin
    """
    return {
        "id": kwargs["id"],
        "ops": [
            {
                "op": kwargs["op"],
                "name": kwargs["name"],
                "path": kwargs["path"],
                "metatype": kwargs["metatype"],
                "stereotype": kwargs["stereotype"],
                "attributes": kwargs["attributes"],
            }
        ],
    }


def to_uml_json_decorations(**kwargs):
    """
    Create dict to be converted to JSON for consumption by Player Piano.

    See Also
    --------
    VertexReporterMixin
    """
    return {
        "id": kwargs["id"],
        "ops": [
            {
                "op": kwargs["op"],
                "path": "/m2/" + kwargs["path"],
                "value": kwargs["value"],
            }
        ],
    }


def to_uml_json_edge(**kwargs):
    """
    Create dict to be converted to JSON for consumption by Player Piano.

    See Also
    --------
    DiEdgeReporterMixin
    """
    return {
        "id": kwargs["id"],
        "ops": [
            {
                "op": kwargs["op"],
                "path": "/m2/" + kwargs["path"],
                "value": kwargs["value"],
            }
        ],
    }


def truncate_microsec(curr_time=None):
    """
    Returns Hours Minutes Seconds.
    """
    time_str = curr_time.strftime("%H %M %S %f")
    return time_str[0:-3]
