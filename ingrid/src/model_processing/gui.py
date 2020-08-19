"""
Copyright (C) 2020 by the Georgia Tech Research Institute (GTRI)
This software may be modified and distributed under the terms of
the BSD 3-Clause license. See the LICENSE file for details.
"""

import argparse

from .commands import compare_md_model, create_md_model
from ._version import __version__

from gooey import Gooey, GooeyParser


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

    fh_group = parser.add_argument_group("File Handling")

    create_group = parser.add_argument_group("Create")
    create_group.add_argument(
        "--Input File(s)", action="store_true", help="Option One"
    )

    compare_group = parser.add_argument_group("Compare")
    compare_group.add_argument(
        "--opt2", action="store_true", help="Option Two"
    )

    layering_group = parser.add_argument_group("Pattern Layering")
    layering_group.add_argument(
        "--opt3", action="store_true", help="Option Three"
    )

    args = parser.parse_args()


if __name__ == '__main__':
    main()
