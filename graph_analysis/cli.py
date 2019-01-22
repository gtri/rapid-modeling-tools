import argparse

from .commands import compare_md_model, create_md_model


def main():
    """
    Command line entry function
    :return:
    """

    print('hello world')

    parser = argparse.ArgumentParser(
        description="A simple CLI for parsing an Excel Workbook and "
                    "generating SysML Graph JSON instructions to be used "
                    "with the Player Piano.",
    )

    parser.add_argument(
        "-cr",
        "--create",
        nargs='?',
        help="Create a JSON file for the Player Piano to make in a MD Diagram",
        default=True,
        const=True
    )

    parser.add_argument(
        "-cf",
        "--compare",
        nargs='?',
        help=("Compare a baseline Excel File with a collection of Change Files"
              + " Must supply the original file first and then the changes"),
        default=True,
        const=True
    )

    parser.add_argument(
        "-i",
        "--input",
        nargs='*',
        help="Path to Excel Workbook(s)",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output",
        help=("Path/Directory where the JSON file(s) should be placed"
              + " Default behavior will place the JSON in the input location"),
        type=str,
    )

    parser.add_argument(
        "-or",
        "--original",
        help="The original file to which the comparison will be run against.",
    )

    parser.add_argument(
        "-up",
        "--updated",
        nargs='*',
        help="Change files to be compared to the Original."
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
        return create_md_model(args.input, args.output)
    elif args.compare:
        # TODO: return comparison
        if not (args.original or args.updated):
            raise RuntimeError('Missing Original or Updated File(s)')
        else:
            # I could throw a warning and make the user type yes or no to
            # continue so they acknowledge the possibility of overwrite.
            inputs = [args.original, args.updated]
            return compare_md_model(inputs, args.output)
    else:
        return "Not a valid input argument. Choose from create or compare"


if __name__ == "__main__":
    main()
