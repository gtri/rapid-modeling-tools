import argparse

from .commands import compare_md_model, create_md_model


def main():
    """
    Command line entry function
    :return:
    """

    print("I am shocked, shocked to find that gambling is going on in here!")

    parser = argparse.ArgumentParser(
        description="A simple CLI for parsing an Excel Workbook and "
        "generating SysML Graph JSON instructions to be used "
        "with the Player Piano."
    )

    parser.add_argument(
        "-c",
        "--create",
        nargs="?",
        help="Create a JSON file for the Player Piano to make in a MD Diagram",
        const=True,
    )

    parser.add_argument(
        "-C",
        "--compare",
        nargs="?",
        help=(
            "Compare a baseline Excel File with a collection of Change Files"
            + " Must supply the original file first and then the changes"
        ),
        const=True,
    )

    parser.add_argument(
        "-i", "--input", nargs="*", help="Path to Excel Workbook(s)", type=str
    )

    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path/Directory where the JSON file(s) should be placed"
            + " Default behavior will place the JSON in the input location"
        ),
        type=str,
    )

    parser.add_argument(
        "-O",
        "--original",
        help="The original file to which the comparison will be run against.",
        type=str,
    )

    parser.add_argument(
        "-U",
        "--updated",
        nargs="*",
        help="Change files to be compared to the Original.",
        type=str,
    )

    parser.add_argument(
        "-v", "--version", help="version information", action="store_true"
    )

    args = parser.parse_args()
    if args.version:
        # TODO: get __version__ form init.py and setup.py
        return "0.1.0"
    elif args.create:
        return create_md_model(args.input, args.output)
    elif args.compare:
        inputs = [args.original]
        inputs.extend(args.updated)
        return compare_md_model(inputs, args.output)
    else:
        return "Not a valid input argument. Choose from create or compare"


if __name__ == "__main__":
    main()
