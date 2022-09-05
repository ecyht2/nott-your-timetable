#!/usr/bin/env python3
import argparse
from utils import get_data


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
                        help="Sets the output format. (Not Yet Available)")

    # Course Selection
    course_group = parser.add_mutually_exclusive_group(required=True)
    course_group.add_argument("-c", "--course", type=str, nargs=2,
                              help="Specify which School/Division and"
                              " Program to export",
                              metavar=("School/Division", "Program"))
    course_group.add_argument("-i", "--interactive", action="store_true",
                              help="Specify which School/Division and"
                              " Program to export using standard input")

    return parser.parse_args()


def get_school_interactive() -> tuple[str, list[str]]:
    school = None
    program = None

    dept_data, program_data = get_data()

    while school is None or school == "?" or school == "":
        school = input("Enter School/Division Name (? for list): ")

        if school == "?":
            for data in dept_data.keys():
                print(data)
        elif school == "":
            pass
        elif school not in dept_data:
            school = None
            print("Invalid School/Division Name.")

    school_value = dept_data[school]
    while program is None or program == "?" or program == "":
        program = input("Enter Program Name (? for list): ")

        if program == "?":
            for data in program_data[school_value].keys():
                print(data)
        elif program == "":
            pass
        elif program not in program_data[school_value]:
            print("Invalid Program.")

    return (school, program)
