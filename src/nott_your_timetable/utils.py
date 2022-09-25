#!/usr/bin/env python3
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
import html
from enum import Enum
from calendar import Calendar
import datetime
import csv
from string import whitespace
import json
from importlib.resources import files
from collections import defaultdict
from typing import Any
from icalendar import Calendar as iCalendar
from icalendar import Event as iEvent


# Other Utils
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


def get_data() -> tuple[dict, dict]:
    """Gets Department and program data from json files.

    Returns
    -------
    tuple[dict, dict]
        The data where the first one is the department data
        and the second one is the program data.
    """
    data_path = files('nott_your_timetable.data')
    with open(data_path.joinpath("dept.json"), "r") as f:
        dept_data: dict = json.load(f)
    with open(data_path.joinpath("program.json"), "r") as f:
        program_data: dict = json.load(f)

    return (dept_data, program_data)


def get_program_value(school: str, program: str) -> str:
    """Gets the value of the program.

    Parameters
    ----------
    school: str
        The school of the program.
    program: str
        The program to find the value of.

    Returns
    -------
    str
        The value of the program
    """
    dept_data, program_data = get_data()

    school_value = dept_data.get(school)
    if school_value is None:
        raise ValueError("Invalid School Name")

    program_value = program_data[school_value].get(program)
    if program_value is None:
        raise ValueError("Invalid Program")

    return program_value


def find_first_day(day: int | str, year: int, month: int,
                   ISO: bool = False) -> int:
    """Finds the first day of week of a given month and year.

    Parameters
    ----------
    day: int | str
        The day of week to find
    year: int
        The year of interest
    month: int
        The month of interest
    ISO: bool
        Use the ISO the numbering system to use when specifying day of week
        Can be ignored when day is given as a string

    Returns
    -------
    int
        They date of the month in which the first day of week appeared
    """
    cal: Calendar = Calendar()
    weeks = cal.monthdayscalendar(year, month)

    if isinstance(day, int):
        day_index = day
        if ISO:
            day -= 1
    elif isinstance(day, str):
        try:
            day_index = DayOfWeek[day.title()].value
        except KeyError:
            raise ValueError("Invalid Day of Week")

    for week in weeks:
        if week[day_index] > 0:
            return week[day_index]


def find_week1() -> datetime.date:
    """Finds week 1 of the academic year.

    Returns
    -------
    datetime.date
        The date of the first week of september.
    """
    today: datetime.date = datetime.date.today()
    if today.month < 9:
        year: int = today.year - 1
        day: int = find_first_day(0, year, 9)
    else:
        year: int = today.year
        day: int = find_first_day(0, year, 9)

    week1: datetime.date = datetime.date(year, 9, day)
    return week1


def find_current_week_nott() -> int:
    """Finds the week number.

    Returns
    -------
    int
        The current week number.
    """
    diff = datetime.date.today() - find_week1()
    return int(diff.days / 7) + 1


# Utils for parsing data
class DayOfWeek(Enum):
    Monday = 0
    Mon = 0
    Tuesday = 1
    Tue = 1
    Wednesday = 2
    Wed = 2
    Thursday = 3
    Thu = 3
    Friday = 4
    Fri = 4
    Saturday = 5
    Sat = 5
    Sunday = 6
    Sun = 6


class DayOfWeekISO(Enum):
    Monday = 1
    Mon = 1
    Tuesday = 2
    Tue = 2
    Wednesday = 3
    Wed = 3
    Thursday = 4
    Thu = 4
    Friday = 5
    Fri = 5
    Saturday = 6
    Sat = 6
    Sunday = 7
    Sun = 7


class ScheduleParser(HTMLParser):
    """HTML Parser used to parse all the tables

    Parameters
    ----------
    days: list[int] = [1, 2, 3, 4, 5, 6, 7]
        A list of days of the week to look for
    """
    def __init__(self, days: list[int] = [i for i in range(1, 8)]):
        super().__init__()

        # Declaring needed variables
        self.day_found: bool = False
        self.table_found: bool = False
        self.table_ended: bool = False
        self.tables: dict[str, str] = {}
        self.current_day: str = ""

        # Populating tables
        days.sort()
        for day in days:
            self.tables[DayOfWeekISO(day).name] = ""

    def handle_data(self, data):
        """Handles data received (text inside tags)."""
        if not self.day_found:
            # Finding the days
            if data in self.tables:
                self.day_found = True
                self.current_day = data
        else:
            if data.strip() != "" and self.table_found:
                data = html.escape(data)
                self.tables[self.current_day] += data

    def handle_starttag(self, tag, attr):
        """Handles start tags received."""
        if not self.day_found:
            return
        if (tag == "table" or self.table_found):
            self.table_found = True
            self.tables[self.current_day] += f"<{tag}>"

    def handle_endtag(self, tag):
        """Handles end tags received."""
        if not self.day_found:
            return
        if self.table_found:
            self.tables[self.current_day] += f"</{tag}>"
            if tag == "table":
                self.table_found = False
                self.day_found = False


def table_to_dict(table: str | ET.Element, indexs: list[str] = None,
                  verbose: bool = True) -> dict[str, list[str]] | None:
    """Converts a HTML table into a python dict
    Parameters
    ----------
    table: str | xml.etree.ElementTree
        The HTML table to use.
        It can be in the form of a string, ElementTree from xml module.
    indexs: list[str]
        The Index to use for the dict.
        If None is provided, the first row of the table will be used.
    verbose: bool
        Determine to print information messages

    Returns
    -------
    dict[str, list[str]]
        The data of the table.
    None
        If there isn't any data

    TODO
    ----
    Handle Uneven Spaces
    """
    # Getting Element Tree
    if isinstance(table, ET.Element):
        data: ET.Element = table
    else:
        data: ET.Element = ET.fromstring(table)

    # Returning None if there isn't any data in table
    if data.find("tr") is None:
        if verbose:
            print("No Data in table")
        return None

    # Setting indexes/label used for the csv
    indexed = False
    if indexs is None:
        if verbose:
            print("No Indexs Provided, Using first row as index")

        indexs = []
        for col in data.findall("tr")[0].findall("td"):
            indexs.append(col.text)
        indexed = True

    # Setting up output dict
    output = {}
    for i in indexs:
        output[i] = []

    # Getting data from table
    skipped = False
    for row in data.findall("tr"):
        # Skipping first row if used for indexing
        if indexed and not skipped:
            skipped = True
            continue
        # Looping or indexs
        columns = row.findall("td")
        for i, label in enumerate(indexs):
            try:
                output[label].append(columns[i].text)
            except IndexError:
                if verbose:
                    print("Not Enough Data at Row")

    return output


def parse_data(data: dict, weeks: list) -> dict:
    """Combines all the parts of the tables into it's own list.

    Parameter
    ---------
    data: dict
        The data
    weeks: list
        The weeks to parse

    Return
    ------
    dict
        The parsed data
    """
    start_day = find_week1()

    output_data = {
        "Module": [],
        "Start": [],
        "End": [],
        "Date": [],
        "Room": []
    }

    # Looping Over all they day of the week
    for day, day_data in data.items():
        date_with_day = start_day +\
            datetime.timedelta(days=DayOfWeek[day].value)
        # Skipping if there is no classes
        if day_data is None:
            continue

        # Looping over all the modules in they day
        for i in range(len(day_data['Module'])):
            module_weeks = day_data['Weeks'][i]
            module = day_data['Module'][i]

            # Getting Start Time
            start = day_data['Start'][i].split(":")
            start = datetime.time(hour=int(start[0]), minute=int(start[1]))
            # Getting End Time
            end = day_data['End'][i].split(":")
            end = datetime.time(hour=int(end[0]), minute=int(end[1]))

            room = day_data["Room"][i]

            # Looping through all the weeks
            for week in handle_ranges(module_weeks):
                if week not in weeks:
                    continue
                date = date_with_day + datetime.timedelta(weeks=week-1)

                # Appending Data
                output_data["Module"].append(module)
                output_data["Date"].append(date)
                output_data["Start"].append(start)
                output_data["End"].append(end)
                output_data["Room"].append(room)

    # Returing Data
    return output_data


# Utils for exporting
class ScheduleData(defaultdict):
    def __init__(self, subject: list, start_date: list,
                 start_time: list = [],
                 end_date: list = [], end_time: list = [],
                 all_day_event: list = [], description: list = [],
                 location: list = [], private_event: list = []):
        super().__init__(list)

        # Ensuring equal length
        if len(subject) != len(start_date):
            raise ValueError("subject and start_date must be the same length")

        # Storing Variables
        # https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop
        self["Subject"] = subject
        self["Start Date"] = start_date
        self["Start Time"] = start_time
        self["End Date"] = end_date
        self["End Time"] = end_time
        self["All Day Event"] = all_day_event
        self["Description"] = description
        self["Location"]: list = location

        # Adding Dummy Values
        for key in self:
            if key == "Subject" or key == "Start Date":
                continue

            items = self[key]
            while len(items) < len(self["Subject"]):
                items.append(None)

        # Sorting Keys
        # Making a copy of need values
        self.__sorting_indexs = [
            self["Start Date"].copy(),
            self["Start Time"].copy(),
            self["Subject"].copy()
        ]
        # Looping over all values
        for items in self.values():
            self.__current_index = 0
            items.sort(key=self.__sort_indexs)

    def export_csv(self, output: str = "output.csv") -> list[list]:
        """Exports the timetable in a csv format.

        Parameters
        ----------
        output: str
            Output file name

        Returns
        -------
        list[list]
            A list of all the rows containg all the csv data
        """
        output_value = []

        with open(output, "w") as f:
            writer = csv.writer(f)
            # Adding Label Row
            output_value.append([
                "Subject", "Start Date", "Start Time", "End Date", "End Time",
                "All Day Event", "Description", "Location"
            ])

            # Looping over all values
            for i in range(len(self["Subject"])):
                output_value.append([
                    self["Subject"][i], self["Start Date"][i],
                    self["Start Time"][i], self["End Date"][i],
                    self["End Time"][i], self["All Day Event"][i],
                    self["Description"][i], self["Location"][i]
                ])

            # Writting Values
            writer.writerows(output_value)

        return output_value

    def export_ical(self, output: str = "output.ics"):
        """Exports the timetable in a iCalander format.
        The format is compatible with
        RCF 5545 see link below for more information:
        https://www.ietf.org/rfc/rfc5545.txt

        Parameters
        ----------
        output: str
            Output file name
        """
        cal = iCalendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//nott-your-timetable//Nottingham Schedule/EN")

        for i in range(len(self["Subject"])):
            event = iEvent()

            # Ignoing time if is is all day event
            if self["All Day Event"][i] is not None:
                dtstart = self["Start Date"][i]
                dtend = self["End Date"][i]
            else:
                dtstart = datetime.datetime.combine(self["Start Date"][i],
                                                    self["Start Time"][i])
                dtend = datetime.datetime.combine(self["Start Date"][i],
                                                  self["End Time"][i])

            event.add("dtstamp", datetime.datetime.now())
            event.add("uid", self.__get_uid(i))
            event.add("dtstart", dtstart)
            event.add("dtend", dtend)
            event.add("summary", self["Subject"][i])
            event.add("location", self["Location"][i])

            cal.add_component(event)

        with open(output, "wb") as f:
            f.write(cal.to_ical())

    def export_vcard(self, output: str = "output.vcard"):
        """Exports the timetable in a vCard format.

        Parameters
        ----------
        output: str
            Output file name
        """
        ...

    def __sort_indexs(self, index: Any) -> list:
        """Returns the key such that the lists would be sorted based on
        Start Date -> Start Time (if used) -> Subject.

        Parameters
        ----------
        index: Any
            Not used but added because it is required

        Returns
        -------
        list
            A list to be sorted by
        """
        index: int = self.__current_index
        data = [
            self.__sorting_indexs[0][index],
            self.__sorting_indexs[1][index],
            self.__sorting_indexs[2][index]
        ]
        self.__current_index += 1
        return data

    def __get_uid(self, index: int) -> str:
        """Gets a UID forr an event."""
        date = self["Start Date"][index]
        subject = self["Subject"][index]
        start = self["Start Time"][index]
        end = self["End Time"][index]

        return f"{date}-{subject}-{start}-{end}"
