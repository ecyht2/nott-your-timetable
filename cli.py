#!/usr/bin/env python3
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Exports Timetable for\
    University of Nottingham Malaysia Student.')

    parser.add_argument('-w', '--weeks', type=str, default="1-52")
    parser.add_argument('-d', '--days', type=str, default="1-7")
    parser.add_argument('-o', '--output', type=str, default="output.csv")

    return parser.parse_args()
