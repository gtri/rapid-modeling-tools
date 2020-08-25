"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""

import argparse

from .commands import compare_md_model, create_md_model
from ._version import __version__

from gooey import Gooey, GooeyParser


# TODO: Menu items
@Gooey(
    program_name="Rapid Modeling Tools: Ingrid",
    default_size=(710, 700),
    program_description="GUI for Ingrid interactions",
    # use_cmd_args=True,
    optional_cols=2,
)
def main():
    """
    GUI interface
    """
    # Either need to add an entry point for this file in setup
    # console_scripts or add a new key, gui_scripts, to entry_points in
    # setup file.

    print("Welcome to the GUI for Rapid Modeling Tools: Ingrid")
    settings_msg = (
        "Welcome to the GUI for Rapid Modeling Tools: Ingrid"
    )

    parser = GooeyParser(description=settings_msg)

    # fh_group = parser.add_argument_group("File Handling")
    subs = parser.add_subparsers(help="commands", dest="commands")

    create_parser = subs.add_parser(
        "create",
        help="Transform patterned input Excel data into Cameo API JSON",
    )
    create_parser.add_argument(
        "Input",
        widget="MultiFileChooser",
        help="Choose File(s) to Create Model JSON From",
        metavar="Create File(s)",
        gooey_options={
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    create_parser.add_argument(
        "--pattern",
        widget="MultiFileChooser",
        help="Choose Custom Pattern File(s)",
        metavar="Custom Pattern File(s)",
        gooey_options={
            "wildcard": "JSON (*.json)|*.json",
            "message": "Select your JSON pattern file(s)",
            "default_file": "",
        },
    )
    create_parser.add_argument(
        "--output",
        widget="DirChooser",
        help="Choose the Output Directory",
        metavar="Desired Output Directory",
        gooey_options={
            "message": "Identify the desired output directory",
            "default_dir": "",
        },
    )
    create_parser.add_argument(
        "--patterns",
        type=list,
        metavar="Comma Separated Pattern List",
        help=(
            "In a comma separated list (without spaces) identify the "
            "desired patterns in order of application. Required for input "
            "Excel files with multiple patterns in a single data sheet. "
            "Example Input: Composition,PropertyRedef,SystemParts"
        )
    )

    compare_parser = subs.add_parser(
        "compare",
        help="Compare two Excel Model versions"
    )
    compare_parser.add_argument(
        "Original",
        widget="FileChooser",
        help="Upload the Original Excel Model File",
        metavar="Create File",
        gooey_options={
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    compare_parser.add_argument(
        "Changed",
        widget="MultiFileChooser",
        help="Choose File(s) to Compare to the Original Model",
        metavar="Changed File(s)",
        gooey_options={
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    compare_parser.add_argument(
        "--pattern",
        widget="MultiFileChooser",
        help="Choose Custom Pattern File(s)",
        metavar="Custom Pattern File(s)",
        gooey_options={
            "wildcard": "JSON (*.json)|*.json",
            "message": "Select your JSON pattern file(s)",
            "default_file": "",
        },
    )
    compare_parser.add_argument(
        "--output",
        widget="DirChooser",
        help="Choose the Output Directory",
        metavar="Desired Output Directory",
        gooey_options={
            "message": "Identify the desired output directory",
            "default_dir": "",
        },
    )

    layer_parser = subs.add_parser(
        "pattern_layering",
        help="Create the first pattern and comapre subsequent patterns"
    )
    layer_parser.add_argument(
        "Data",
        widget="FileChooser",
        help=(
            "Upload the Data file which should have one sheet containing "
            "all of the columns required for each pattern desired."
        ),
        metavar="Create File",
        gooey_options={
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    layer_parser.add_argument(
        "patterns",
        type=list,
        metavar="Comma Separated Pattern List",
        help=(
            "In a comma separated list (without spaces) identify the "
            "desired patterns in order of application. Required for input "
            "Excel files with multiple patterns in a single data sheet. "
            "Example Input: Composition,PropertyRedef,SystemParts"
        )
    )
    layer_parser.add_argument(
        "--pattern",
        widget="MultiFileChooser",
        help="Choose Custom Pattern File(s)",
        metavar="Custom Pattern File(s)",
        gooey_options={
            "wildcard": "JSON (*.json)|*.json",
            "message": "Select your JSON pattern file(s)",
            "default_file": "",
        },
    )
    layer_parser.add_argument(
        "--output",
        widget="DirChooser",
        help="Choose the Output Directory",
        metavar="Desired Output Directory",
        gooey_options={
            "message": "Identify the desired output directory",
            "default_dir": "",
        },
    )

    # diff_resolver_group = parser.add_argument_group("Difference Resolver")
    # Looks like a wx app can handle this.
    # TODO: Provide difference excel and associated JSON, output directory
    # I think we need Python state access so the other option is to run the
    # comparison again, assume same change issues

    args = parser.parse_args()
    print(args)
    return args
    # return parser.parse_args()


if __name__ == "__main__":
    args = main()
    print(args)
    assert False
    if args.cr_file or args.cr_dir:
        inputs = [args.cr_file]
        inputs.extend(args.cr_dir)
        create_md_model(inputs, None, args.cr_out_dir)
