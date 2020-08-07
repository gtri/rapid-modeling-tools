"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""


import json
import uuid
from copy import copy, deepcopy
from datetime import datetime
from functools import partial
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

from . import OUTPUT_DIRECTORY, PATTERNS
from .graph_objects import DiEdge, PropertyDiGraph, Vertex
from .utils import (
    associate_node_id,
    associate_node_types_settings,
    associate_predecessors,
    associate_renames,
    associate_successors,
    build_dict,
    create_column_values_singleton,
    create_column_values_space,
    create_column_values_under,
    make_object,
    match_changes,
    remove_duplicates,
    set_newname_as_rename_index,
    to_excel_df,
    truncate_microsec,
)


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

    Parameters
    ----------
    excel_path : list
        list of paths to Excel Files, parsed from the command line.

    json_path : list
        string indicating which JSON file to load from the patterns
        directory.

    Attributes
    ----------
    json_data : dict
        The json data associated with the json_path.

    translator : MDTranslator
        The MDTranslator object created from the json_data

    evaluators : Evaluator
        list of the Evaluators created for each Excel file in the excel_path.
        len(evaluators) == len(excel_path)
    """

    def __init__(self, excel_path=None, json_path=None):
        self.excel_path = excel_path
        self.json_path = json_path
        self.json_data = None
        self.translator = None
        if self.json_path:
            self.get_json_data()
        self.evaluators = []
        if self.excel_path:
            self.create_evaluators()

    def get_json_data(self):
        """ Load the json data using the json_path"""
        self.json_data = []
        self.translator = []
        if len(self.json_path) >= 1:
            for data_file in self.json_path:
                data = json.loads(Path(data_file).read_text())
                self.json_data.append(data)
                self.translator.append(
                    MDTranslator(json_path=Path(data_file), json_data=data)
                )

    def create_evaluators(self):
        """
        Create an Evaluator object for each excel file in the excel_path
        """
        if len(self.translator) > 1 and len(self.excel_path) == 1:
            for tr in self.translator:
                self.evaluators.append(
                    Evaluator(excel_file=self.excel_path[0], translator=tr)
                )
        elif len(self.translator) == 1 and len(self.excel_path) >= 1:
            # TODO: Include a flag from the commands to the manager to pass to
            # this method that indicates create vs compare
            # TODO: Give baseline translator to change files but also to create
            # files if multiple create files in a create command. Issue?
            path_name = [excel_file.name for excel_file in self.excel_path]

            # For compare each changed excel file gets a copy of the original
            # translator.
            for count, excel_file in enumerate(self.excel_path):
                if count != 0:  # TODO: flag to indicate create or compare
                    translator = self.evaluators[0].translator
                else:
                    translator = self.translator[0]
                self.evaluators.append(
                    Evaluator(
                        excel_file=excel_file, translator=deepcopy(translator)
                    )
                )
        else:
            msg = (
                "unsupported input: Multiple Excel Files and Multiple "
                + "Patterns Requested"
            )
            raise RuntimeError(msg)

    def get_pattern_graph_diff(self, out_directory=""):
        """
        Compares the graph describing an Original MagicDraw model to the
        graph describing an Updated MagicDraw model, ignoring change
        to change comparisons.

        Uses a stable marriage approach to compare edges from the original
        that do not exist in the change to edges in the change that do not
        exist int he original and assigns a score to each based
        on the likely hood that the original edge was altered to match a
        certain change. Only compares changes of the same edge type to a
        particular original edge and adds additional emphasis on edges
        with matching renames.

        After matching, generates a json file and places it in the
        out_directory if specified, otherwise drops it in the same
        directory as the original file.

        Parameters
        ----------
        out_directory : str
            Desired directory for the output files. Directory specified
            here shared with the json and excel writing functions.

        Returns
        -------
        evaluator_change_dict : dict of dict
            Outer key for the identified changes and the unstable changes.
            Inner keys for the identified changes include an Added key,
            Deleted and the remaining represent an Original
            DiEdge paired with its Change DiEdge.

        Notes
        -----
        For each pair of Evaluators (Original, Change), compare the edge
        sets removing the common edges. Then with the edge sets fashion
        a dictionary with original edge objects as keys securing a value
        list of all change edges of the same type. Run a version of the
        stable marriage algorithm over this dictionary by scoring each
        value edge on its likeliness to be the updated key. Any key
        that makes it through the matching algorithm with more than one
        potential match becomes an unstable pair (borrowed language
        from the unstable marriage algorithm). With all of the edges
        analyzed, the function sends the edges to JSON and Excel creation.

        See Also
        --------
        utils.match_changes
        changes_to_excel
        graph_difference_to_json
        """
        evaluator_dict = {
            evaluator: index
            for index, evaluator in enumerate(self.evaluators)
        }
        self.evaluator_change_dict = {}
        orig_eval = self.evaluators[0]

        for pair in combinations(self.evaluators, 2):
            # Checking if Evaluator has a rename dataframe
            if evaluator_dict[pair[0]] != 0 and evaluator_dict[pair[1]] != 0:
                continue  # skip because this is comparing diff to diff

            eval_1_e_dict = pair[0].prop_di_graph.edge_dict
            eval_2_e_dict = pair[1].prop_di_graph.edge_dict

            edge_set_one = pair[0].edge_set  # get baseline edge set
            edge_set_two = pair[1].edge_set  # get the changed edge set

            # remove common edges
            # have to do this with named edges.
            # TODO: implement __eq__ and __neq__ methods to the DiEdge then
            # these set operations can be done without casting to str then
            # casting back.
            edge_set_one_set = {
                edge.named_edge_triple for edge in edge_set_one
            }
            edge_set_two_set = {
                edge.named_edge_triple for edge in edge_set_two
            }

            # Remove edges common to each but preserve set integrity for
            # each evaluator
            eval_one_unmatched_named = list(
                edge_set_one_set.difference(edge_set_two_set)
            )
            eval_two_unmatched_named = list(
                edge_set_two_set.difference(edge_set_one_set)
            )

            # Organize edges in dictionary based on type (this goes on for
            # multiple lines)
            eval_one_unmatched = [
                eval_1_e_dict[edge] for edge in eval_one_unmatched_named
            ]
            eval_two_unmatched = [
                eval_2_e_dict[edge] for edge in eval_two_unmatched_named
            ]

            eval_one_unmatch_map = dict(
                (edge.edge_attribute, list()) for edge in eval_one_unmatched
            )
            eval_two_unmatch_map = dict(
                (edge.edge_attribute, list()) for edge in eval_two_unmatched
            )

            for edge in eval_one_unmatched:
                eval_one_unmatch_map[edge.edge_attribute].append(edge)
            for edge in eval_two_unmatched:
                eval_two_unmatch_map[edge.edge_attribute].append(edge)

            eval_one_unmatch_pref = {}
            eval_two_unmatch_pref = {}

            ance_keys_not_in_base = set(
                eval_two_unmatch_map.keys()
            ).difference(set(eval_one_unmatch_map.keys()))

            eval_one_unmatch_pref["Added"] = []
            eval_one_unmatch_pref["Deleted"] = []
            # TODO: Find new edges if the edge type is new but also
            # if the edge is composed of new model elements.
            for edge_type in ance_keys_not_in_base:
                eval_one_unmatch_pref["Added"].extend(
                    eval_two_unmatch_map[edge_type]
                )
            for edge in edge_set_two:
                src, trg = edge.source, edge.target
                if isinstance(src.id, type(uuid.uuid4())):
                    eval_one_unmatch_pref["Added"].append(edge)
                elif isinstance(trg.id, type(uuid.uuid4())):
                    eval_one_unmatch_pref["Added"].append(edge)

            # builds main dict used for matching and determines add/del edges
            for edge in eval_one_unmatched:
                if edge.edge_attribute not in eval_two_unmatch_map.keys():
                    eval_one_unmatch_pref["Deleted"].append(edge)
                else:
                    eval_one_unmatch_pref[edge] = copy(
                        eval_two_unmatch_map[edge.edge_attribute]
                    )
            for edge in eval_two_unmatched:
                if edge.edge_attribute not in eval_one_unmatch_map.keys():
                    eval_two_unmatch_pref[edge] = []
                else:
                    eval_two_unmatch_pref[edge] = copy(
                        eval_one_unmatch_map[edge.edge_attribute]
                    )

            # Run the matching algorithm
            # Always expect the input dict to be Original: Changes.
            # Functions down the line hold this expectation.
            eval_one_matches = match_changes(
                change_dict=eval_one_unmatch_pref
            )

            changes_and_unstable = {
                "Changes": eval_one_matches[0],
                "Unstable Pairs": eval_one_matches[1],
            }

            key = "{0}-{1}".format(
                evaluator_dict[pair[0]], evaluator_dict[pair[1]]
            )

            self.graph_difference_to_json(
                change_dict=eval_one_matches[0],
                translator=pair[1].translator,
                evaluators=key,
                out_directory=out_directory,
            )
            self.evaluator_change_dict.update({key: changes_and_unstable})

        return self.evaluator_change_dict

    def changes_to_excel(self, out_directory=""):
        """
        Write the changes from the get_pattern_graph_diff method to an
        Excel file.

        The changes displayed in the file are intended to inform the user
        of the changes that the change_json will make to the model when
        implemented in MagicDraw and to display the changes that the user
        will have to make on their own to bring the model up to date.
        In other words the Excel file generated here displays the complete
        set of differences between the original and the change file and
        the likely changes that update the original file to be equivalent
        with the specified change file. This method produces an Excel file
        by flattening the evaluator_change_dict variable and writing it to
        a Python dictionary, which can be interpreted as a
        Pandas DataFrame and written out to an Excel file.

        Parameters
        ----------
        out_directory : str
            string representation of the desired output directory. If
            out_directory is not specified then the output directory will
            by the same as the input directory.

        Returns
        -------
        df_output : Excel File
            !!This is not actually returned!! Creates an Excel File in the
            `out_directory` if provided otherwise it places the generated
            file in the same directory as the input file.

        Notes
        -----
        This function could be expanded to produce a more "readable" Excel
        file. Currently it just produces a "raw" Excel file, which becomes
        particularly apparent when viewing the Unstable Matches Original
        and Unstable Matches Change columns of the Excel, as a background on
        the idea of the Stable Marriage Algorithm helps interpret the displayed
        data.

        See Also
        --------
        get_pattern_graph_diff
        to_excel_df
        """
        # TODO: When length of value > 1 put these changes into
        # Unstable Original: [key*len(value)] Unstable Change: [value]
        for key in self.evaluator_change_dict:
            outfile = Path(
                "Model Diffs {0}-{1}.xlsx".format(
                    key, truncate_microsec(curr_time=datetime.now().time())
                )
            )

            if out_directory:
                outdir = out_directory
            else:
                outdir = OUTPUT_DIRECTORY

            difference_dict = self.evaluator_change_dict[key]
            input_dict = {}
            evals_comp = key.split("-")
            edit_left_dash = "Edit {0}".format(str(int(evals_comp[0]) + 1))
            edit_right_dash = "Edit {0}".format(str(int(evals_comp[-1]) + 1))
            # Outer dict keys
            column_headers = [edit_left_dash, edit_right_dash]

            for in_key in difference_dict:
                if not difference_dict[in_key]:
                    continue
                column_headers.append(in_key)
                # flatten evaluator_change_dict from nested struct to flat dict
                input_dict.update(difference_dict[in_key])
            df_data = to_excel_df(
                data_dict=input_dict, column_keys=column_headers
            )

            df_output = pd.DataFrame(
                data=dict([(k, pd.Series(v)) for k, v in df_data.items()])
            )

            df_output.to_excel(
                (outdir / outfile), sheet_name=key, index=False
            )

    def graph_difference_to_json(
        self,
        change_dict=None,
        translator=None,
        evaluators="",
        out_directory="",
    ):
        """
        Produce MagicDraw JSON instruction for Player Piano from the
        confidently identified changes.

        This method returns a change list, Python list of dictionaries
        containing MagicDraw instructions, and a JSON file in the
        out_directory, if provided otherwise in the same directory as the
        input files. JSON instructions created for Added edges, Deleted
        edges and changed edges. For Added edges, if the source and target
        nodes have already been created during this function call then
        just provide instructions to create the new edges, otherwise
        create the source and target nodes then link them with an edge. For
        all Deleted edges, each edge in the list receives a delete operation
        intentionally leaving the source and target nodes in the model in case
        they fulfill other roles. Changed edges have two main categories with
        three subcategories. First, a change edge can either involve a renamed
        source or target node or a newly created source or target node. Once
        identified as a rename (respectively newly created), the edge is
        sorted into three scenarios, both the source and target node represent
        renamed (respectively new) nodes, or the source or target node
        corresponds to a rename (respectively new) node operation. After
        identifying all of the changes and producing the associated
        dictionaries, the operations are sorted to place created nodes and
        their decorations first, followed by deleted edges, renamed nodes and
        ending with added edges.

        Parameters
        ----------
        change_dict : dict
            Dictionary of confident changes. Two static keys 'Added' and
            'Deleted' with associated lists of added and deleted nodes
            respectively. The remaining key value pairs in the change_dict
            represent confident changes with the key being an edge from the
            original Evaluator and the value being a list comprised of the
            likely change edge.

        translator : MDTranslator
            MagicDraw Translator object associated with the current update
            evaluator.

        evaluators : str
            Number of the two evaluators under consideration. The original
            evaluator always receives the number 0 while each change evaluator
            has a number 1-n with n being the nth evaluator.

        out_directory : str
            String specifying the output directory

        Returns
        -------
        change_list : list of dicts
            The list of change instructions. NOTE: This function also
            generates a JSON file and places it in the `out_directory`
            if specified otherwise it places the JSON file in the same
            directory as the input file.

        Notes
        -----
        Any edge not meeting one of the eight criteria defined will fall
        through to the else case and become an edge replace operation.
        The `get_pattern_graph_diff()` method automatically calls this method.

        See Also
        --------
        get_pattern_graph_diff
        """
        # need to strip off the keys that are strings and use them to
        # determine what kinds of ops I need to preform.
        # Naked Key: Value pairs mean delete edge key and add value key.
        # Purposefully excluding unstable pairs because the Human can make
        # those changes so they are clear.
        static_keys = ["Added", "Deleted"]
        change_list = []
        edge_del = []
        edge_add = []
        node_renames = []
        create_node = []
        node_dec = []

        # initially populates with translator ids that are not uuid objs.
        # TODO: This ignores renames
        seen_ids = set()
        for k, v in translator.uml_id.items():
            if isinstance(v, str):
                seen_ids.add(v)

        for key, value in change_dict.items():
            if key == "Added":
                # Create added edges if have not been created yet
                for edge in value:
                    edge_source, edge_target = edge.source, edge.target
                    if edge_source.id not in seen_ids:
                        seen_ids.add(edge_source.id)
                        s_cr, s_dec, s_edg = edge_source.create_node_to_uml(
                            translator=translator
                        )
                        create_node.extend(s_cr)
                        node_dec.extend(s_dec)
                        edge_add.extend(s_edg)
                    if edge_target.id not in seen_ids:
                        seen_ids.add(edge_target.id)
                        t_cr, t_dec, t_edg = edge_target.create_node_to_uml(
                            translator=translator
                        )
                        create_node.extend(t_cr)
                        node_dec.extend(t_dec)
                        edge_add.extend(t_edg)
                    edge_add.append(
                        edge.edge_to_uml(op="replace", translator=translator)
                    )
            elif key == "Deleted":
                # deleted edges, this is the only command to issue a delete op
                for edge in value:
                    edge_del.append(
                        edge.edge_to_uml(op="delete", translator=translator)
                    )
            else:  # All other keys are <DiEdge>: [<DiEdge>]
                source_val, target_val = value[0].source, value[0].target
                # Using filter as mathematical ~selective~ or.
                # TODO: rewrite this to be more explicit, google style does
                # not approve of this approach.
                eligible = list(
                    filter(
                        lambda x: x.id not in seen_ids,
                        [source_val, target_val],
                    )
                )
                # List consisting of at most 2 items s.t. has_rename returns T
                has_rename = list(
                    filter(lambda x: x.has_rename, [source_val, target_val])
                )
                # List consisting of at most 2 items s.t. id is type uuid
                is_new = list(
                    filter(
                        lambda x: isinstance(x.id, type(uuid.uuid4())),
                        [source_val, target_val],
                    )
                )

                if has_rename:
                    for node in has_rename:
                        seen_ids.add(node.id)
                        node_renames.append(
                            node.change_node_to_uml(translator=translator)
                        )
                    else:  # Create edge since the change node uml does not
                        edge_add.append(
                            value[0].edge_to_uml(
                                op="replace", translator=translator
                            )
                        )
                if is_new:
                    for node in is_new:
                        seen_ids.add(node.id)
                        n_cr, n_dec, n_edg = node.create_node_to_uml(
                            translator=translator
                        )
                        create_node.extend(n_cr)
                        node_dec.extend(n_dec)
                        edge_add.extend(n_edg)
                    else:
                        edge_add.append(
                            value[0].edge_to_uml(
                                op="replace", translator=translator
                            )
                        )
                # if both source and target are known just replace the edge
                if not has_rename and not is_new:
                    edge_add.append(
                        value[0].edge_to_uml(
                            op="replace", translator=translator
                        )
                    )

        # remove_duplicates only has local knowledge
        if create_node:
            change_list.extend(remove_duplicates(create_node, create=True))
            change_list.extend(remove_duplicates(node_dec))
        change_list.extend(remove_duplicates(edge_del))
        change_list.extend(remove_duplicates(node_renames, create=True))
        change_list.extend(remove_duplicates(edge_add))

        json_out = {"modification targets": []}
        json_out["modification targets"].extend(change_list)
        outfile = Path(
            "graph_diff_changes_{0}({1}).json".format(
                evaluators, truncate_microsec(curr_time=datetime.now())
            )
        )

        if out_directory:
            outdir = out_directory
        else:
            outdir = OUTPUT_DIRECTORY

        (outdir / outfile).write_text(
            json.dumps(json_out, indent=4, sort_keys=True)
        )

        return change_list


class Evaluator:
    """
    Class for creating the `PropertyDiGraph` from the Excel data with the
    help of the `MDTranslator`.

    `Evaluator` produces a `Pandas DataFrame` from the Excel path provided
    by the `Manager`. The `Evaluator` then updates the DataFrame with
    column headers compliant with MagicDraw and infers required columns
    from the data stored in the `MDTranslator`. With the filled out
    DataFrame the `Evaluator` produces the `PropertyDiGraph`.

    Parameters
    ----------
    excel_file : str or Path
        String to an Excel File

    translator : MDTranslator
        `MDTranslator` object that holds the data from the JSON file
        associated with this type of Excel File.

    Attributes
    ----------
    df : Pandas DataFrame
        DataFrame constructed from reading the Excel Pattern Sheet.

    df_ids : Pandas DataFrame
        DataFrame constructed from reading the Excel Ids Sheet, if exists.

    df_renames : Pandas DataFrame
        DataFrame constructed from reading the Excel Renames Sheet,
        if exists.

    prop_di_graph : PropertyDiGraph
        `PropertyDiGraph` constructed from the data in the `df`. Nodes
        keyed by string of the node name. The value corresponding to the
        node is the `Vertex` object. Similarly for edges, edges keyed by
        strings with the corresponding `DiEdge` object associated as an
        attribute. See NetworkX for more information on the dict of dicts
        structure of NX Graphs.

    root_node_attr_columns : set
        Set of column names in the initial read of the Excel file that
        do not appear as `Vertices` in the `MDTranslator` definition of
        the expected `Vertices`. The columns collected here will later be
        associated to the corresponding root node as additional attributes.
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
        """
        :noindex:
        """
        if not self.df_renames.empty:  # if renames sheet exists and nonempty
            return True
        else:
            return False

    @property
    def named_vertex_set(self):
        """
        :noindex:
        """
        return self.prop_di_graph.get_vertex_set_named(df=self.df)

    @property
    def vertex_set(self):
        """
        :noindex:
        """
        return self.prop_di_graph.vertex_set

    @property
    def named_edge_set(self):
        """
        :noindex:
        """
        return self.prop_di_graph.named_edge_set

    @property
    def edge_set(self):
        """
        :noindex:
        """
        return self.prop_di_graph.edge_set

    def sheets_to_dataframe(self, excel_file=None):
        """
        Parse Excel sheet name and assign them to corresponding Evaluator
        dataframes.

        Iterate over sheets and associate the sheet data to the relevant
        `Evaluator` dataframe (`df`, `df_ids`, `df_renames`). Upon
        encountering the ids sheet, update the `MDTranslator.uml_id`
        dictionary with the provided ids. For the rename sheet, set the
        columns containing the updated names to be the index of the
        dataframe.

        Parameters
        ----------
        excel_file : str or Path
            string representation or path to Excel file.

        Raises
        ------
        RuntimeError
            The rename sheet does not have exactly two columns.
            Renames has both old names in both the old and new columns.
            Unrecognized sheet name.
        """
        # TODO: Generalize/Standardize this function
        pattern = self.translator.pattern_name
        ids = [
            "id",
            "ids",
            "identification number",
            "id number",
            "uuid",
            "mduuid",
            "magicdraw id",
            "magic draw id",
            "magicdraw identification",
            "identification numbers",
            "id_numbers",
            "id_number",
        ]
        renames = [
            "renames",
            "rename",
            "new names",
            "new name",
            "newnames",
            "newname",
            "new_name",
            "new_names",
            "changed names",
            "changed name",
            "change names",
            "changed_names",
            "changenames",
            "changed_names",
        ]
        if not excel_file and self.excel_file:
            excel_file = self.excel_file
        excel_sheets = pd.read_excel(excel_file, sheet_name=None)
        # what if the pattern is zzzzzzz, ids, renames
        for sheet in sorted(excel_sheets):  # Alphabetical sort
            # Find the Pattern Sheet
            if pattern in sheet.lower():
                # Maybe you named the ids sheet Pattern IDs I will find it
                if any(id_str in sheet.lower() for id_str in ids):
                    self.df_ids = excel_sheets[sheet]
                    self.df_ids.set_index(
                        self.df_ids.columns[0], inplace=True
                    )
                    self.translator.uml_id.update(
                        self.df_ids.to_dict(orient="dict")[
                            self.df_ids.columns[0]
                        ]
                    )
                # Maybe you named the rename sheet Pattern Renames
                elif any(renm_str in sheet.lower() for renm_str in renames):
                    self.df_renames = excel_sheets[sheet]
                    self.df_renames.dropna(how="all", inplace=True)
                    for row in self.df_renames.itertuples(index=False):
                        if row[0] in self.translator.uml_id.keys():
                            # replace instances of this with those in 1
                            if len(row) == 2:
                                if not self.df_renames.index.is_object():
                                    # set the index as new name
                                    df_renm = set_newname_as_rename_index(
                                        self.df_renames, row, 0
                                    )
                                    self.df_renames = df_renm
                            else:
                                raise RuntimeError(
                                    "Unexpected columns in Rename Sheet. \
                                     Expected 2 but found more than 2."
                                )
                            self.df.replace(
                                to_replace=row[0], value=row[1], inplace=True
                            )
                            self.translator.uml_id.update(
                                {row[1]: self.translator.uml_id[row[0]]}
                            )
                        elif row[1] in self.translator.uml_id.keys():
                            if len(row) == 2:
                                if not self.df_renames.index.is_object():
                                    # set the index as new name
                                    df_renm = set_newname_as_rename_index(
                                        self.df_renames, row, 1
                                    )
                                    self.df_renames = df_renm
                            else:
                                raise RuntimeError(
                                    "Unexpected columns in Rename Sheet. \
                                     Expected 2 but found more than 2."
                                )
                            # same as above in other direction
                            self.df.replace(
                                to_replace=row[1], value=row[0], inplace=True
                            )
                            self.translator.uml_id.update(
                                {row[0]: self.translator.uml_id[row[1]]}
                            )
                else:  # What triggers this, if there is a Pattern sheet and
                    # a Pattern ID or a Pattern Rename then does the main data
                    # ever get read in??
                    # TODO: Break this function down and test edge cases.
                    self.df = excel_sheets[sheet]
                    self.df.dropna(how="all", inplace=True)
            # Hopefully you explicitly named the Rename sheet
            elif any(renm_str in sheet.lower() for renm_str in renames):
                self.df_renames = excel_sheets[sheet]
                self.df_renames.dropna(how="all", inplace=True)
                index_name = ""
                for row in self.df_renames.itertuples(index=False):
                    if all(
                        row[i] in self.translator.uml_id.keys()
                        for i in (0, 1)
                    ):
                        raise RuntimeError("Both old and new in keys")
                    elif row[0] in self.translator.uml_id.keys():
                        # then replace instances of this with those in 1
                        if len(row) == 2:
                            if not self.df_renames.index.is_object():
                                # do the thing set the index as new name
                                df_renm = set_newname_as_rename_index(
                                    self.df_renames, row, 0
                                )
                                self.df_renames = df_renm
                        else:
                            raise RuntimeError(
                                "Unexpected columns in Rename Sheet. \
                                 Expected 2 but found more than 2."
                            )
                        self.df.replace(
                            to_replace=row[0], value=row[1], inplace=True
                        )
                        self.translator.uml_id.update(
                            {row[1]: self.translator.uml_id[row[0]]}
                        )
                        continue
                    elif row[1] in self.translator.uml_id.keys():
                        # row[1] is old, row[0] is new
                        if len(row) == 2:
                            if not self.df_renames.index.is_object():
                                # do the thing set the index as new name
                                df_renm = set_newname_as_rename_index(
                                    self.df_renames, row, 1
                                )
                                self.df_renames = df_renm
                        else:
                            raise RuntimeError(
                                "Unexpected columns in Rename Sheet. \
                                 Expected 2 but found more than 2."
                            )
                        # same as above in other direction
                        self.df.replace(
                            to_replace=row[1], value=row[0], inplace=True
                        )
                        self.translator.uml_id.update(
                            {row[0]: self.translator.uml_id[row[1]]}
                        )
                        continue
            elif any(id_str in sheet.lower() for id_str in ids) and not (
                pattern in sheet.lower()
            ):
                self.df_ids = excel_sheets[sheet]
                self.df_ids.set_index(self.df_ids.columns[0], inplace=True)
                self.translator.uml_id.update(
                    self.df_ids.to_dict(orient="dict")[self.df_ids.columns[0]]
                )
            else:
                raise RuntimeError(
                    "Unrecognized sheet names for: {0}".format(
                        excel_file.name
                    )
                )

    def rename_df_columns(self):
        """
        Returns renamed DataFrame columns from their Excel name to their
        MagicDraw name. Any columns in the Excel DataFrame that are not in
        the json are recorded as attribute columns.
        """
        for column in self.df.columns:
            try:
                new_column_name = self.translator.get_col_uml_names(
                    column=column
                )
                self.df.rename(
                    columns={column: new_column_name}, inplace=True
                )
            except KeyError:
                # We continue because these columns are additional data
                # that we will associate to the Root Vertex as attrs.
                self.root_node_attr_columns.add(column)

    def add_missing_columns(self):
        """Add derived nodes to the dataframe.

        These columns are ones required to fillout the pattern in the
        `MDTranslator` that were not specified by the user. The
        `MDTranslator` provides a template for naming these inferred
        columns.

        Notes
        -----
        Stepping through the function, first a list of column names that
        appear in the JSON but not the Excel are compiled by computing
        the difference between the expected column set from the
        Translator and the initial dataframe columns. Then those columns
        are sorted by length to ensure that longer column names
        constructed of multiple shorter columns do not fail when searching
        the dataframe.

            e.g. Suppose we need to construct the column
            A_composite owner_component. Sorting by length ensures that
            columns_to_create = ['component', 'composite owner',
            'A_composite owner_component']

        Then for each column name in columns to create, the column name is
        checked for particular string properties and the inferred column
        values are determined based on the desired column name.

        See Also
        --------
        create_column_values_under
        create_column_values_space
        create_column_values_singleton
        """
        # from a collection of vertex pairs, create all of the columns for
        # for which data is required but not present in the excel.
        columns_to_create = list(
            set(self.translator.get_pattern_graph()).difference(
                set(self.df.columns)
            )
        )
        # TODO: Weak solution to the creation order problem.
        columns_to_create = sorted(columns_to_create, key=len)

        under = "_"
        space = " "
        dash = "-"
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
                            suffix=suff,
                        )
                    elif len(col.split(sep=under)) > 2:
                        col_data_vals = col.split(sep=under)
                        first_node_data = self.df.loc[:, col_data_vals[1]]
                        second_node_data = self.df.loc[:, col_data_vals[2]]
                        self.df[col] = create_column_values_under(
                            prefix=col_data_vals[0],
                            first_node_data=first_node_data,
                            second_node_data=second_node_data,
                            suffix="",
                        )
                    else:
                        col_data_vals = col.split(sep=under)
                        first_node_data = self.df.loc[:, col_data_vals[1]]
                        second_node_data = self.df.loc[:, col_data_vals[1]]
                        self.df[col] = create_column_values_under(
                            prefix=col_data_vals[0],
                            first_node_data=first_node_data,
                            second_node_data=second_node_data,
                            suffix="",
                        )
                elif space in col:
                    col_data_vals = col.split(sep=space)
                    root_col_name = self.translator.get_root_node()
                    if col_data_vals[0] in self.df.columns:
                        first_node_data = self.df.loc[:, col_data_vals[0]]
                        second_node_data = [
                            col_data_vals[-1]
                            for i in range(len(first_node_data))
                        ]
                    else:
                        first_node_data = self.df.iloc[:, 0]
                        second_node_data = self.df.loc[:, root_col_name]
                    self.df[col] = create_column_values_space(
                        first_node_data=first_node_data,
                        second_node_data=second_node_data,
                    )
                else:
                    col_data_vals = col
                    root_col_name = self.translator.get_root_node()
                    first_node_data = self.df.iloc[:, 0]
                    second_node_data = [
                        col for count in range(len(first_node_data))
                    ]
                    self.df[col] = create_column_values_singleton(
                        first_node_data=first_node_data,
                        second_node_data=second_node_data,
                    )

    def to_property_di_graph(self):
        """
        Creates a PropertyDiGraph from the completely filled out dataframe.

        To achieve this, we loop over the Pattern Graph Edges defined in
        the JSON and take each pair of columns and the edge type as a
        source, target pair with the edge attribute corresponding to the
        edge type defined in the JSON.
        """
        self.prop_di_graph = PropertyDiGraph(
            root_attr_columns=self.root_node_attr_columns
        )
        for index, pair in enumerate(
            self.translator.get_pattern_graph_edges()
        ):
            # edge_type = self.translator.get_edge_type(index=index)
            self.df[pair[2]] = pair[2]
            df_temp = self.df[[pair[0], pair[1], pair[2]]]
            GraphTemp = nx.DiGraph()
            GraphTemp = nx.from_pandas_edgelist(
                df=df_temp,
                source=pair[0],
                target=pair[1],
                edge_attr=pair[2],
                create_using=GraphTemp,
            )
            self.prop_di_graph.add_nodes_from(GraphTemp.nodes)
            self.prop_di_graph.add_edges_from(
                GraphTemp.edges, edge_attribute=pair[2]
            )

        pdg = self.prop_di_graph
        tr = self.translator

        # Est list of lists with dict for each node contaiing its name
        # node is already a string because of networkx functionality
        # idea is to build up kwargs to instantiate a vertex object.
        node_atters = [[{"name": node} for node in list(pdg)]]

        # various functions required to get different vertex attrs
        # partially instantiate each function so that each fn only needs node
        associate_funs = [
            partial(associate_node_id, tr),
            partial(associate_successors, pdg),
            partial(associate_predecessors, pdg),
            partial(
                associate_node_types_settings,
                self.df,
                tr,
                self.root_node_attr_columns,
            ),
            partial(associate_renames, self.df_renames, tr),
        ]

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
            diedge = DiEdge(
                source=pdg.nodes[edge[0]][edge[0]],
                target=pdg.nodes[edge[1]][edge[1]],
                edge_attribute=data["edge_attribute"],
            )
            # The inner key must be a string thus 'diedge' instead of
            # pdg.edges[edge][edge] which would mimic behavior for nodes
            # pdg.nodes[node][node]
            edges.append((edge, {"diedge": diedge}))
        for edge in edges:
            # unpack each edge and the edge attribute dict for the add_edge fn
            pdg.add_edge(*edge[0], **edge[1])

        # pdg has associated vertex obj and associated edge obj in edj dict.
        return pdg


class MDTranslator:
    """
    Class that contains all of the JSON data.

    Class to serve as the Rosetta Stone for taking column headers from the
    Excel input to the MagicDraw compatible output. More specifically,
    this class provides access to data in the JSON file allowing the
    Evaluator to determine which columns are required to fill out the
    pattern that are missing in the input Excel and to associate edge
    types along the directed edges. Furthermore, while the Vertex is
    packaged in `to_uml_json()` the translator provides metadata
    information required by MagicDraw for block creation keyed by the
    `node_type`.

    Parameters
    ----------
    json_path : Path
        The path object to the JSON pattern file
    data : dict
        The JSON data saved off when the Manager accessed the JSON file.
    """

    def __init__(self, json_path=None, json_data=None):
        self.json_path = json_path
        self.data = json_data
        self.uml_id = {}

    def __repr__(self):
        return "MDTranslator Obj(Pattern Name: {0})".format(
            self.json_path.name
        )

    @property
    def pattern_path(self):
        """
        Returns the path to the pattern file
        """
        return self.json_path

    @property
    def pattern_name(self):
        """
        Returns the name of the pattern file
        """
        return self.json_path.name.split(".")[0].lower()

    def get_uml_id(self, name=None):
        """
        Returns the UML_ID for the corresponding vertex name provided.

        If the name provided does not exist as a key in the UML_ID
        dictionary than create a new uuid for that node.

        Parameters
        ----------
        name : string
            The `Vertex.name` attribute

        Returns
        -------
        id : str or UUID4 object
            Returns the string id given by MagicDraw loaded through the
            sheets to dataframe method or creates a new UUID4 object.
        """
        # TODO: write test function for this
        if name in self.uml_id.keys():
            return self.uml_id[name]
        else:
            self.uml_id.update({name: uuid.uuid4()})
            return self.uml_id[name]

    def get_root_node(self):
        """
        Returns the root node value from the JSON.
        """
        return self.data["Root Node"]

    def get_cols_to_nav_map(self):
        """
        Returns the columns to navigation map value.
        """
        return self.data["Columns to Navigation Map"]

    def get_pattern_graph(self):
        # change to return a set of 0, 1 index from pattern graph edges.
        data = self.data["Pattern Graph Edges"]
        vert_set = set()
        for edge in data:
            vert_set.update(set([edge[0], edge[1]]))
        return list(vert_set)

    def get_pattern_graph_edges(self):
        """
        Returns the pattern graph edges.
        """
        return self.data["Pattern Graph Edges"]

    def get_edge_type(self, index=None):
        # TODO: I think this function is deprecated.
        for count, edge in enumerate(self.data["Pattern Graph Edges"]):
            if index == count:
                return edge[-1]
        else:
            return None

    def get_col_uml_names(self, column=None):
        """
        Returns the MagicDraw name of the passed column (str).
        """
        return self.data["Columns to Navigation Map"][column][-1]

    def get_uml_metatype(self, node_key=None):
        """
        Returns the vertex metatype for the given node_key (str).
        """
        return self.data["Vertex MetaTypes"][node_key]

    def get_uml_stereotype(self, node_key=None):
        """
        Returns the vertex stereotype for the given node_key (str).
        """
        return self.data["Vertex Stereotypes"][node_key]

    def get_uml_settings(self, node_key=None):
        """
        Returns the settings key and settings value from the vertex
        settings for the node_key (str).
        """
        uml_phrase = self.data["Vertex Settings"][node_key]

        try:
            uml_phrase.keys()
        except AttributeError:
            return node_key, uml_phrase

        key = next(iter(uml_phrase))
        return key, uml_phrase[key]
