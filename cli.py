#!/usr/bin/env python3
import argparse
from string import whitespace


def handle_ranges(value: str) -> list[int]:
    """Converts integers splitted by ',' into a list.
    A range of value can be added by using '-'.

    Parameters
    ----------
    value: str
        The integers to convert

    Returns
    -------
    list[int]
        The list of integers
    """
    # Removing white spaces
    for space in whitespace:
        value = value.replace(space, '')

    # Splitting all commas
    splitted = value.split(',')

    output = []
    for i in splitted:
        # Adding all values encoded in -
        if '-' in i:
            range_split = i.split('-')
            try:
                range_split[0] = int(range_split[0])
                range_split[1] = int(range_split[1])
                range_split.sort()
                for j in range(range_split[0], range_split[1] + 1):
                    output.append(j)
            except ValueError:
                raise ValueError("Invalid Range, Please Check Inserted Value")
        # Adding normal values
        else:
            try:
                output.append(int(i))
            except ValueError:
                raise ValueError("Invalid Range, Please Check Inserted Value")

    # Sorting Output
    output.sort()
    return output


def parse_arguments():
    parser = argparse.ArgumentParser(description='Exports Timetable for\
    University of Nottingham Malaysia Student.')

    parser.add_argument('-w', '--weeks', type=str, default="1-52")
    parser.add_argument('-d', '--days', type=str, default="1-7")
    parser.add_argument('-o', '--output', type=str, default="output.csv")

    return parser.parse_args()
