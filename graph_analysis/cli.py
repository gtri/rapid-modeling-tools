import argparse


def main():
    """
    Command line entry function
    :return:
    """

    parser = argparse.ArgumentParser(
        description="A simple CLI for parsing an Excel Workbook and "
                    "generating a SysML instruction graph",
    )

    parser.add_argument(
        "-i",
        "--input",
        help="path to Excel Workbook",
        type=str,
    )
