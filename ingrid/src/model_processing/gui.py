"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""

import argparse

from model_processing.commands import compare_md_model, create_md_model

from gooey import Gooey, GooeyParser


@Gooey(
    program_name="Rapid Modeling Tools: Ingrid",
    default_size=(710, 700),
    program_description="GUI for Ingrid interactions",
    optional_cols=2,
)
def main():
    """
    GUI interface built using the python project Gooey
    """

    print("Welcome to the GUI for Rapid Modeling Tools: Ingrid")
    settings_msg = (
        "Welcome to the GUI for Rapid Modeling Tools: Ingrid"
    )

    parser = GooeyParser(description=settings_msg)

    subs = parser.add_subparsers(help="commands", dest="commands")

    create_parser = subs.add_parser(
        "create",
        help="Transform patterned input Excel data into Cameo API JSON",
    )
    create_parser.add_argument(
        "Input",
        widget="MultiFileChooser",
        nargs="*",
        help="Choose File(s) for the CREATE command",
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

    compare_parser = subs.add_parser(
        "compare",
        help="Compare two Excel Model versions"
    )
    compare_parser.add_argument(
        "Original",
        widget="FileChooser",
        help="Upload the Original Excel Model File",
        metavar="Original File: Excel representation of current model state",
        gooey_options={
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    compare_parser.add_argument(
        "Changed",
        widget="MultiFileChooser",
        nargs="*",
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
        nargs="*",
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

    # diff_resolver_group = parser.add_argument_group("Difference Resolver")
    # Looks like a wx app can handle this.
    # TODO: Provide difference excel and associated JSON, output directory
    # I think we need Python state access so the other option is to run the
    # comparison again, assume same change issues

    return parser.parse_args()


if __name__ == "__main__":
    args = main()
    if args.commands == "create":
        create_md_model(args.Input, args.pattern, args.output)
    if args.commands == "compare":
        inputs = [args.Original]
        inputs.extend(args.Changed)
        compare_md_model(inputs, args.pattern, args.output)
