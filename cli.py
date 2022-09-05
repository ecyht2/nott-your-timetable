#!/usr/bin/env python3
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Exports Timetable for\
    University of Nottingham Malaysia Student.')

    parser.add_argument('-w', '--weeks', type=str, default="1-52",
                        help="Sets the range of weeks to export. You can set"
                        "multiple weeks to export by seperating them by ','"
                        " or '-' to export all weeks in between.")
    parser.add_argument('-d', '--days', type=str, default="1-7",
                        help="Sets the range of days to export. You can set"
                        "multiple days to export by seperating them by ','"
                        " or '-' to export all days in between.")
    parser.add_argument('-o', '--output', type=str, default="output.csv",
                        help="Sets the output file name.")

    return parser.parse_args()
