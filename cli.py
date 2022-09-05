#!/usr/bin/env python3
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Exports Timetable for\
    University of Nottingham Malaysia Student.')

    # Range Options
    parser.add_argument('-w', '--weeks', type=str, default="1-52",
                        help="Sets the range of weeks to export. You can set"
                        "multiple weeks to export by seperating them by ','"
                        " or '-' to export all weeks in between.")
    parser.add_argument('-d', '--days', type=str, default="1-7",
                        help="Sets the range of days to export. You can set"
                        "multiple days to export by seperating them by ','"
                        " or '-' to export all days in between.")
    # Output Options
    parser.add_argument('-o', '--output', type=str, default="output.csv",
                        help="Sets the output file name.")
    parser.add_argument('-t', '--type', type=str, default="csv",
                        help="Sets the output format.")

    # Course Selection
    course_group = parser.add_mutually_exclusive_group(required=True)
    course_group.add_argument("-c", "--course", type=str, nargs=2,
                              help="Specify which School/Division and"
                              " Programme to export",
                              metavar=("School/Division", "Programme"))
    course_group.add_argument("-i", "--interactive", action="store_true",
                              help="Specify which School/Division and"
                              " Programme to export using standard input")

    return parser.parse_args()
