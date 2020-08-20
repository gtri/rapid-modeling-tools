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
    tabbed_groups=True,
    navigation="TABBED",
    program_description="GUI for Ingrid interactions",
)
def main():
    """
    GUI interface
    """
    # Either need to add an entry point for this file in setup
    # console_scripts or add a new key, gui_scripts, to entry_points in
    # setup file.

    print("Welcome to the GUI for Rapid Modeling Tools: Ingrid")

    parser = GooeyParser()

    # fh_group = parser.add_argument_group("File Handling")

    pattern_up_group = parser.add_argument_group("Pattern Upload")
    pattern_up_group.add_argument(
        "custom_pattern",
        help="Choose custom pattern file(s)",
        metavar="Custom Pattern(s)",
        widget="MultiFileChooser",
        default="",
        required=False,
        gooey_options = {
            "wildcard": "JSON (*.json)|*.json",
            "message": "Select your JSON pattern file(s)",
            "default_file": "",
        }
    )
    pattern_up_group.add_argument(
        "custom_pattern_dir",
        help="Upload an entire directory of custom JSON pattern file(s)",
        metavar="Custom Pattern(s) Directory",
        widget="DirChooser",
        gooey_options = {
            "wildcard": "JSON (*.json)|*.json",
            "message": "Select a directory containing JSON pattern file(s)",
            "default_dir": "",
        }
    )
    # parser.set_defaults(custom_pattern="", custom_pattern_dir="")

    # multi-select widget for patterns with write in box for custom uploads
    # check-box to store true if user applying multiple patterns to single
    # data sheet.
    create_group = parser.add_argument_group("Create")
    create_group.add_argument(
        "cr_file",
        # action="Select the Create Excel file(s)",
        help="Choose File(s) to Create Model JSON From",
        widget="MultiFileChooser",
        metavar="Create File(s)",
        gooey_options = {
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File(s)",
            "default_file": "",
        },
    )
    create_group.add_argument(
        "cr_dir",
        help="Pick a directory of create files. Dir only contains RMT Excels",
        metavar="Directory of Create Excel File(s)",
        widget="DirChooser",
        gooey_options = {
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick a directory contining input Excel file(s)",
            "default_dir": "",
        },
    )
    create_group.add_argument(
        "cr_out_dir",
        # action="",
        help="Pick the output directory",
        metavar="Output Directory",
        widget="DirChooser",
        gooey_options = {
            "message": "Identify the desired output directory",
            "default_dir": "",
        },
    )

    compare_group = parser.add_argument_group("Compare")
    # TODO: Pattern picker
    compare_group.add_argument(
        "og_file",
        help="Upload the original Excel file",
        widget="FileChooser",
        gooey_options = {
            "wildcard": "Xlsx (*.xlsx)|*.xlsx",
            "message": "Pick Excel File",
            "default_file": "",
        },
    )
    compare_group.add_argument(
        "ch_file",
        help="Choose file(s) to compare against the original",
        widget="MultiFileChooser",
    )
    compare_group.add_argument(
        "cmp_out_dir",
        help="Pick the output directory",
        widget="DirChooser",
    )


    layering_group = parser.add_argument_group("Pattern Layering")
    layering_group.add_argument(
        "--opt3", action="store_true", help="Option Three"
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


if __name__ == '__main__':
    args = main()
    print(args)
    assert False
    if args.cr_file or args.cr_dir:
        inputs = [args.cr_file]
        inputs.extend(args.cr_dir)
        create_md_model(inputs, None, args.cr_out_dir)
