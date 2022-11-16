#!/usr/bin/env python3
"""Main Functions to run."""
import sys
import datetime
import requests
from .utils.range_handlers import handle_ranges_days, handle_ranges
from .utils.weeks import find_current_week_nott
from .utils.parsers import get_program_value, make_request
from .cli import get_school_interactive, parse_arguments

GUI_FLAG = False
try:
    from .gui import NottApp
    GUI_FLAG = True
except ModuleNotFoundError:
    pass


def main():
    """Main Function to interface with nott-your-timetable.

    If GUI dependencies are installed, it will launch the GUI. Otherwise, it
    will default to CLI.
    """
    if GUI_FLAG:
        return main_gui()

    print("PyGObject not installed, deafulting to CLI.", file=sys.stderr)
    print("Please install the gi module or install the gui extras.",
          file=sys.stderr)
    return main_cli()


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

    try:
        schedule_data = make_request(program_value, days, weeks)
    except requests.ConnectTimeout:
        print("HTTP request taking too long, please check your internet"
              "connection", file=sys.stderr)
        return 1

    return schedule_data.export(args.format, args.output)


def main_gui():
    """GUI main function."""
    app = NottApp()
    return app.run()
