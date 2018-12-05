import argparse

from .graph_creation import compare, create


def main():
    """
    Command line entry function
    :return:
    """

    print('hello world')

    parser = argparse.ArgumentParser(
        description="A simple CLI for parsing an Excel Workbook and "
                    "generating a SysML instruction graph",
    )

    parser.add_argument(
        "-cr",
        "--create",
        help="Create a JSON file for the Player Piano to make in a MD Diagram"
    )

    parser.add_argument(
        "-cf",
        "--compare",
        help="Compare a baseline Excel File with a collection of Change Files"
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Path to Excel Workbook(s)",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to JSON file to save instruction to",
        type=str,
    )

    parser.add_argument(
        "-v",
        "--version",
        help="version information",
        action="store_true",
    )

    args = parser.parse_args()
    if args.version:
        # TODO: get __version__ form init.py and setup.py
        return "0.1.0"
    elif args.create:
        # TODO: define a create function that creates a json for a fresh model
        return None
    elif args.compare:
        # TODO: return comparison
        return None
    else:
        return "Not a valid input argument. Choose from create or compare"


if __name__ == "__main__":
    main()
