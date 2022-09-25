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

    try:
        days = handle_ranges_days(args.days)
        weeks = handle_ranges(args.weeks)
    except ValueError:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    if args.output is None:
        args.output = "output." + args.format

    if args.today:
        days = [today.isoweekday()]
        weeks = [find_current_week_nott()]

    if days[0] < 1 or days[-1] > 7:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1
    if weeks[0] < 1 or weeks[-1] > 52:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1

    if args.interactive:
        school, program = get_school_interactive()
    else:
        school, program = args.course

    program_value = None
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
    schedule_data = ScheduleData(parsed_data["Module"], parsed_data["Date"],
                                 start_time=parsed_data["Start"],
                                 end_time=parsed_data["End"],
                                 location=parsed_data["Room"])

    if args.format == "csv":
        schedule_data.export_csv(args.output)
    elif args.format == "ics":
        schedule_data.export_ical(args.output)
    else:
        # Probably not gonna happen but added for redundancy
        print("Invalid Format", file=sys.stderr)
        return 1
    return 0
