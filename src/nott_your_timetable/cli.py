#!/usr/bin/env python3
"""CLI related functions."""
import argparse
from .utils import get_data, find_current_week_nott


def parse_arguments():
    """Parses the cli arguments for nott-your-timetable-cli."""
    parser = argparse.ArgumentParser(description='Exports Timetable for\
    University of Nottingham Malaysia Student.')

    # Range Options
    # Range Options for weeks
    week_range_group = parser.add_argument_group(title="Week Range Options")
    range_week = week_range_group.add_mutually_exclusive_group()
    range_week.add_argument('-w', '--weeks', type=str, default="1-52",
                            help="""Sets the range of weeks to export.
                            You can set multiple weeks to export by
                            seperating them by ','  or '-' to export
                            all weeks in between.""")
    range_week.add_argument("-ay", "--all-year", action="store_const",
                            help="""Exports Timetable for the
                            entire year (Week 1-52).""",
                            const="1-52", dest="weeks")
    range_week.add_argument("-au", "--autumn", action="store_const",
                            help="""Exports Timetable for the
                            entire autumn semester (Week 4-15).""",
                            const="4-15", dest="weeks")
    range_week.add_argument("-sp", "--spring", action="store_const",
                            help="""Exports Timetable for the
                            entire spring semester (Week 22-33).""",
                            const="22-33", dest="weeks")
    range_week.add_argument("-su", "--summer", action="store_const",
                            help="""Exports Timetable for the
                            entire summer semester (Week 38-49).""",
                            const="38-49", dest="weeks")
    range_week.add_argument("-fy", "--full-year", action="store_const",
                            help="""Exports Timetable for the
                            full year semester (Week 4-15, 22-33).""",
                            const="4-15,22-33", dest="weeks")
    range_week.add_argument("-tw", "--this-week", action="store_const",
                            help="""Exports Timetable for this week.""",
                            const=str(find_current_week_nott()), dest="weeks")

    # Range Options for days
    day_range_group = parser.add_argument_group(title="Day Range Options")
    range_day = day_range_group.add_mutually_exclusive_group()
    range_day.add_argument('-d', '--days', type=str, default="1-7",
                           help="""Sets the range of days to export. You can
                           set multiple days to export by seperating them by
                           ','  or '-' to export all days in between.
                           1 is Monday and up to 7 is Sunday.""")
    range_day.add_argument("-wd", "--weekdays", action="store_const",
                           help="Exports Timetable for the weekdays.",
                           const="1-5", dest="days")
    range_day.add_argument("-aw", "--all-week", action="store_const",
                           help="""Exports Timetable for the whole week
                           (Mon-Sun).""", const="1-7", dest="days")
    range_day.add_argument("-we", "--weekends", action="store_const",
                           help="Exports Timetable for the weekends.",
                           const="6-7", dest="days")
    range_day.add_argument("-td", "--today", action="store_true",
                           help="""Exports Timetable for today.""")

    # Output Options
    output_group = parser.add_argument_group(title="Output Options")
    output_group.add_argument('-o', '--output', type=str, default=None,
                              help="Sets the output file name.")
    output_group.add_argument('-f', '--format', type=str, default="ics",
                              choices=["csv", "ics"],
                              help="Sets the output format.")

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
    """Code logic for interactive mode."""
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
            program = None
            print("Invalid Program.")

    return (school, program)
