#!/usr/bin/env python3
import requests
from utils import (ScheduleParser, table_to_dict, csv_export, handle_ranges)
import argparse


def main_cli(args: argparse.Namespace):
    try:
        days = handle_ranges(args.days)
        weeks = handle_ranges(args.weeks)
    except ValueError:
        print("Invalid Range, Please Check Inserted Value")
        return 1
    output = args.output

    if days[0] < 1 or days[-1] > 7:
        print("Invalid Range, Please Check Inserted Value")
        return 1
    elif weeks[0] < 1 or weeks[-1] > 52:
        print("Invalid Range, Please Check Inserted Value")
        return 1

    program = "UG/M1024/M6UEEENG/F/02"

    link = f"http://timetablingunmc.nottingham.ac.uk:8016/reporting/\
TextSpreadsheet;programme+of+study;id;{program}%0D%0A?\
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
