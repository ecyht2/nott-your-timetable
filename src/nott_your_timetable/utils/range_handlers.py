#!/usr/bin/env python3
"""Functions that handles ranges encoded in strings e.g. 1, 2, 5-10"""
from string import whitespace
from .enums import DayOfWeekISO


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
            except ValueError as err:
                raise ValueError("Invalid Range, Please Check Inserted Value")\
                    from err
        # Adding normal values
        else:
            try:
                output.append(int(i))
            except ValueError as err:
                raise ValueError("Invalid Range, Please Check Inserted Value")\
                    from err

    # Sorting Output
    output.sort()
    return output


def handle_ranges_days(value: str) -> list[int]:
    """Converts integers splitted by ',' into a list.
    A range of value can be added by using '-'.
    This is simillar to handle_ranges but adds supports for
    text like Mon-Fri

    Parameters
    ----------
    value: str
        The data to convert

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
                try:
                    range_split[0] = DayOfWeekISO[range_split[0]].value
                    range_split[1] = DayOfWeekISO[range_split[1]].value
                except KeyError:
                    range_split[0] = int(range_split[0])
                    range_split[1] = int(range_split[1])
                range_split.sort()
                for j in range(range_split[0], range_split[1] + 1):
                    output.append(j)
            except ValueError as err:
                raise ValueError("Invalid Range, Please Check Inserted Value")\
                    from err
        # Adding normal values
        else:
            try:
                output.append(int(i))
            except ValueError as err:
                raise ValueError("Invalid Range, Please Check Inserted Value")\
                    from err

    # Sorting Output
    output.sort()
    return output
