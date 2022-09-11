#!/usr/bin/env python3
import requests
import sys
from utils import (ScheduleParser, table_to_dict, csv_export, handle_ranges,
                   handle_ranges_days, get_program_value,
                   find_current_week_nott)
from cli import get_school_interactive
import argparse
import datetime


def main_cli(args: argparse.Namespace):
    today = datetime.date.today()

    try:
        days = handle_ranges_days(args.days)
        weeks = handle_ranges(args.weeks)
    except ValueError:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1
    output = args.output

    if args.today:
        days = [today.isoweekday()]
        weeks = [find_current_week_nott()]

    if days[0] < 1 or days[-1] > 7:
        print("Invalid Range, Please Check Inserted Value", file=sys.stderr)
        return 1
    elif weeks[0] < 1 or weeks[-1] > 52:
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

    response: requests.Response = requests.get(link)
    parser = ScheduleParser(days)
    parser.feed(response.text)
    parser.close()

    tables = parser.tables
    data = tables.copy()
    for table in tables:
        data[table] = table_to_dict(tables[table], verbose=False)

    csv_export(data, weeks, output)
    return 0
