#!/usr/bin/env python3
"""Main Functions to run."""
import sys
import datetime
import requests
from .utils import (ScheduleParser, table_to_dict, handle_ranges, parse_data,
                    handle_ranges_days, get_program_value, ScheduleData,
                    find_current_week_nott)
from .cli import get_school_interactive, parse_arguments


def main_cli():
    """CLI main function."""
    args = parse_arguments()
    today = datetime.date.today()

    # Getting all the day and week ranges
    try:
        days = handle_ranges_days(args.days)
        weeks = handle_ranges(args.weeks)
    except ValueError:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    # Using default output filename
    if args.output is not None:
        args.output += f".{args.format}"

    # If today is specified
    if args.today:
        days = [today.isoweekday()]
        weeks = [find_current_week_nott()]

    # Checking if ranges are valid
    if (days[0] < 1 or days[-1] > 7) or (weeks[0] < 1 or weeks[-1] > 52):
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    # Interactive mode
    if args.interactive:
        school, program = get_school_interactive()
    else:
        school, program = args.course

    # Getting the pogram values
    try:
        program_value = get_program_value(school, program)
    except ValueError:
        print("Invalid School or Program", file=sys.stderr)
        return 1

    link = f"http://timetablingunmc.nottingham.ac.uk:8016/reporting/\
TextSpreadsheet;programme+of+study;id;{program_value}%0D%0A?\
days=1-7&weeks=1-52&periods=3-20&template=SWSCUST+programme+of+study+TextSpreadsheet&\
height=100&week=100"

    try:
        response: requests.Response = requests.get(link, timeout=10)
    except requests.ConnectTimeout:
        print("HTTP request taking too long, please check your internet"
              "connection", file=sys.stderr)
        return 1

    parser = ScheduleParser(days)
    parser.feed(response.text)
    parser.close()

    data = parser.tables.copy()
    for key, value in parser.tables.items():
        data[key] = table_to_dict(value, verbose=False)

    parsed_data = parse_data(data, weeks)
    schedule_data = ScheduleData()
    schedule_data.set("Subject", parsed_data["Module"])
    schedule_data.set("Start Date", parsed_data["Date"])
    schedule_data.set("Start Time", parsed_data["Start"])
    schedule_data.set("End Time", parsed_data["End"])
    schedule_data.set("Location", parsed_data["Room"])

    return schedule_data.export(args.format, args.output)
