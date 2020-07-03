"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""


import json
import os
import warnings
from pathlib import Path

import pandas as pd

from model_processing.graph_creation import Evaluator, Manager, MDTranslator

from . import PATTERNS


def create_md_model(input_paths, output_path=""):
    """
    For each Excel file in input_paths create a JSON file that creates
    the desired model in MagicDraw, as long as it corresponds to a valid
    pattern sheet.

    Parameters
    ----------
    input_paths : list of str
        List of strings parsed from the command line.

    output_path : str
        String of the desired location for the output. This is optional
        and if omitted then the output files will be placed in the same
        directory as the input files.

    Returns
    -------
    output : JSON file
        Generates a JSON file as output that the Player Piano digests to
        generate a new MagicDraw model.
    """
    json_patterns = {
        pattern_path.parts[-1].split(".")[0].lower(): pattern_path
        for pattern_path in PATTERNS.glob("*.json")
    }

    wkbk_paths = []
    here = Path(os.getcwd())

    for path in input_paths:
        p = Path(path)
        if not p.is_absolute():
            p = here / p
        if p.is_dir():
            p = list(p.glob("*.xlsx"))
        else:
            p = [p]

        wkbk_paths.extend(p)

    for wkbk in wkbk_paths:
        # TODO: Can this support Heterogeneous excel input files?
        if wkbk.parts[-1].split(".")[-1] != "xlsx":
            msg = (
                "\n"
                + "This program only supports Excel Files."
                + ' "{0}" was skipped, not an Excel File'
            ).format(wkbk.parts[-1])
            warnings.warn(msg)
            continue
        xl = pd.ExcelFile(wkbk)
        not_found = 0
        pattern_sheet = ""
        for sheet in xl.sheet_names:
            if sheet.lower() not in json_patterns.keys():
                not_found += 1
                if not_found == len(xl.sheet_names):
                    warn_msg = (
                        'The Excel File "{0}" cannot be processed as none of the worksheets match a '
                        + "supported pattern type."
                    ).format(wkbk.parts[-1])
                    patterns_msg = (
                        "The currently supported "
                        + "patterns are: {0}".format([*json_patterns])
                    )
                    patts = (
                        "New patterns may be added in the"
                        + " ingrid/src/model_processing/patterns directory"
                    )
                    warnings.warn(
                        "\n" + warn_msg + "\n" + patterns_msg + "\n" + patts
                    )
                    break
                else:
                    continue
            else:
                pattern_sheet = sheet.lower()
                break

        if pattern_sheet:
            data = (json_patterns[pattern_sheet]).read_text()
            data = json.loads(data)
            translator = MDTranslator(json_data=data)
            evaluator = Evaluator(excel_file=wkbk, translator=translator)
            evaluator.rename_df_columns()
            evaluator.add_missing_columns()
            evaluator.to_property_di_graph()
            property_di_graph = evaluator.prop_di_graph
            vert_set = property_di_graph.vertex_set
            json_out = {"modification targets": []}
            decs_json = []
            edge_json = []
            for vertex in vert_set:
                vert_uml, decs_uml, edge_uml = vertex.create_node_to_uml(
                    translator=translator
                )
                json_out["modification targets"].extend(vert_uml)
                decs_json.extend(decs_uml)
                edge_json.extend(edge_uml)

            json_out["modification targets"].extend(decs_json)
            json_out["modification targets"].extend(edge_json)

            if not output_path:
                outfile = wkbk.parent.joinpath(wkbk.parts[-1]).with_suffix(
                    ".json"
                )
            else:
                outpath = Path(output_path)
                if not outpath.is_absolute():
                    if outpath.parts[-1] == here.parts[-1]:
                        outpath = here
                    else:
                        outpath = here / outpath
                outfile = (
                    Path(outpath)
                    .joinpath(wkbk.parts[-1])
                    .with_suffix(".json")
                )

            (outfile).write_text(
                json.dumps(json_out, indent=4, sort_keys=True)
            )

            print("Creation Complete")


def compare_md_model(inputs, output_path=""):
    """
    Produces difference files (JSON and Excel) for the original file to
    each change file provided.

    Parameters
    ----------
    inputs : list of strs
        List of one or more file paths parsed from the command line.
        This can be a path to one or more Excel files or a path to a
        directory of Excel files.

    output_path : str
        String of the desired location for the output. This is optional
        and if omitted then the output files will be placed in the same
        directory as the input files.

    Returns
    -------
    output_json : JSON file
        Generates a JSON file as output that the Player Piano digests to
        Generates a JSON file as output that the Player Piano digests to
        update the original Model.
    output_excel : Excel file
        Generates an Excel file that lists the confident changes (ones
        made by the JSON) and the unstable pairs so the user can make the
        determination on those changes on their own.
    """
    provided_paths = inputs
    wkbk_paths = []
    here = Path(os.getcwd())

    for counter, path in enumerate(provided_paths):
        p = Path(path)
        if not p.is_absolute():
            p = here / p
        if p.is_dir():
            p = list(p.glob("*.xlsx"))
            for path in p:
                if counter != 0 and path.name == p[0].name:
                    p.remove(path)
        else:
            p = [p]

        wkbk_paths.extend(p)

    if output_path:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            if output_path.parts[-1] == here.parts[-1]:
                output_path = here
            else:
                output_path = here / output_path
        if not output_path.is_dir():
            raise RuntimeError("Please provide an output directory")
        outpath = output_path
    else:
        outpath = wkbk_paths[0].parent

    for wkbk in wkbk_paths:
        if wkbk.parts[-1].split(".")[-1] != "xlsx":
            msg = (
                "\n"
                + "This program only supports Excel Files."
                + ' "{0}" was skipped, not an Excel File'
            ).format(wkbk.parts[-1])
            warnings.warn(msg)
            continue

    json_patterns = {
        pattern_path.parts[-1].split(".")[0].lower(): pattern_path
        for pattern_path in PATTERNS.glob("*.json")
    }

    xl = pd.ExcelFile(wkbk_paths[0])
    not_found = 0
    pattern_sheet = ""
    for sheet in xl.sheet_names:
        if sheet.lower() not in json_patterns.keys():
            not_found += 1
            if not_found == len(xl.sheet_names):
                warn_msg = (
                    'The Excel File "{0}" cannot be processed as none of the worksheets match a '
                    + "supported pattern type."
                ).format(wkbk.parts[-1])
                patterns_msg = (
                    "The currently supported "
                    + "patterns are: {0}".format([*json_patterns])
                )
                patts = (
                    "New patterns may be added in the"
                    + " ingrid/src/model_processing/patterns directory"
                )
                warnings.warn(
                    "\n" + warn_msg + "\n" + patterns_msg + "\n" + patts
                )
                break
            else:
                continue
        else:
            pattern_sheet = sheet.lower()
            break

    if pattern_sheet:
        manager = Manager(
            excel_path=wkbk_paths, json_path=[json_patterns[pattern_sheet]]
        )
        for evaluator in manager.evaluators:
            evaluator.rename_df_columns()
            evaluator.add_missing_columns()
            evaluator.to_property_di_graph()

        manager.get_pattern_graph_diff(out_directory=outpath)
        manager.changes_to_excel(out_directory=outpath)

        print("Comparison Complete")
    else:
        raise RuntimeError(
            "No matching pattern sheet was found."
            + " Check the sheet names and try again."
        )
