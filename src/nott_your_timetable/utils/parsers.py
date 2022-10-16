#!/usr/bin/env python3
"""Functions and Classes used by nott-your-timetable."""
import html
import datetime
import csv
import sys
import io
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, NoReturn
import requests
from icalendar import Calendar as iCalendar
from icalendar import Event as iEvent
from .data import get_data
from .enums import DayOfWeekISO, DayOfWeek
from .weeks import find_week1
from .range_handlers import handle_ranges


# Other Utils
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


# Utils for parsing data
class ScheduleParser(HTMLParser):
    """HTML Parser used to parse all the tables

    Parameters
    ----------
    days: list[int] = [1, 2, 3, 4, 5, 6, 7]
        A list of days of the week to look for
    """
    def __init__(self, days: list[int] = None):
        super().__init__()

        if days is None:
            days = list(range(1, 8))

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

    def handle_starttag(self, tag, attrs):
        """Handles start tags received."""
        # pylint: disable=unused-argument
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
    # Setting Up function to print verbose statments
    def print_verbose(verbosity: bool, print_index: int):
        if not verbosity:
            return

        match print_index:
            case 0:
                print("No Data in table")
            case 1:
                print("No Indexs Provided, Using first row as index")
            case 2:
                print("Not Enough Data at Row")

    # Getting Element Tree
    if isinstance(table, ET.Element):
        data: ET.Element = table
    else:
        data: ET.Element = ET.fromstring(table)

    # Returning None if there isn't any data in table
    if data.find("tr") is None:
        print_verbose(verbose, 0)
        return None

    # Setting indexes/label used for the csv
    indexed = False
    if indexs is None:
        print_verbose(verbose, 1)

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
                print_verbose(verbose, 2)

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
    """Object that holds all the data of a Schedule."""
    def __init__(self):
        super().__init__(list)
        key_list = ["Subject", "Start Date", "Start Time", "End Date",
                    "End Time", "All Day Event", "Description", "Location"]

        # Storing Variables
        for key in key_list:
            super().__setitem__(key, [])

        # Setting up some needed variables
        self.__current_index = 0
        self._sorting_keys = [
            self["Start Date"].copy(),
            self["Start Time"].copy(),
            self["Subject"].copy()
        ]

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
        # Sorting Values
        self._sort_values()

        output_value = []

        csv_output = io.StringIO()
        writer = csv.writer(csv_output)
        # Adding Label Row
        output_value.append([
            "Subject", "Start Date", "Start Time", "End Date", "End Time",
            "All Day Event", "Description", "Location"
        ])

        # Looping over all values
        for i in range(len(self["Subject"])):
            output_value.append([
                self._get_value("Subject", i),
                self._get_value("Start Date", i),
                self._get_value("Start Time", i),
                self._get_value("End Date", i),
                self._get_value("End Time", i),
                self._get_value("All Day Event", i),
                self._get_value("Description", i),
                self._get_value("Location", i)
            ])

        # Writting Values
        writer.writerows(output_value)

        self._write_file(csv_output.getvalue(), output)

        return output_value

    def export_ical(self, output: str = "output.ics") -> iCalendar:
        """Exports the timetable in a iCalander format.
        The format is compatible with
        RCF 5545 see link below for more information:
        https://www.ietf.org/rfc/rfc5545.txt

        Parameters
        ----------
        output: str
            Output file name
        """
        # Sorting Values
        self._sort_values()

        # Creating Calendar Component
        cal = iCalendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//nott-your-timetable//Nottingham Schedule/EN")

        # Creating all the Event Components
        for i in range(len(self["Subject"])):
            event = iEvent()

            # Ignoing time if is is all day event
            if self._get_value("All Day Event", i) is not None:
                dtstart = self._get_value("Start Date", i)
                dtend = self._get_value("End Date", i)
            else:
                dtstart = datetime.datetime.combine(
                    self._get_value("Start Date", i),
                    self._get_value("Start Time", i)
                )
                dtend = datetime.datetime.combine(
                    self._get_value("Start Date", i),
                    self._get_value("End Time", i)
                )

            event.add("dtstamp", datetime.datetime.now())
            event.add("uid", self.__get_uid(i))
            event.add("dtstart", dtstart)
            event.add("dtend", dtend)
            event.add("summary", self._get_value("Subject", i))
            event.add("location", self._get_value("Location", i))

            cal.add_component(event)

        self._write_file(cal.to_ical().decode("utf-8"), output)

        return cal

    def export_vcard(self, output: str = "output.vcard"):
        """Exports the timetable in a vCard format.

        Parameters
        ----------
        output: str
            Output file name
        """
        # Sorting Values
        self._sort_values()
        self._write_file("WIP", output)

    def export(self, export_format: str, output: str) -> int:
        """Exports the data to a given format.

        Parameters
        ----------
        export_format: str
            The format to export in.
            It can be [ics, vcard (WIP), csv]
        output: str
            Output filename

        Returns
        -------
        int
            0 if successful
            1 if unsuccessful (e.g. invalid format)
        """
        # Sorting Values
        self._sort_values()

        match export_format:
            case "csv":
                self.export_csv(output)
            case "ics":
                self.export_ical(output)
            case _:
                # Probably not gonna happen but added for redundancy
                print("Invalid Format", file=sys.stderr)
                return 1

        return 0

    def _write_file(self, data: str, output: str = None) -> None:
        """Writes the data into a file.

        Parameters
        ----------
        data: str
            The data to write
        output: str | None
            The output filename
            If None is provided, it will be written to stdout
        """
        if output is None:
            print(data)
        else:
            with open(output, "w", encoding="utf-8") as file:
                file.write(data)
                print(f"Data Exported to {output}")

    def __get_sort_values(self, index: Any) -> list:
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
        data = []
        for i in self._sorting_keys:
            try:
                data.append(i[index])
            except IndexError:
                data.append("")
        self.__current_index += 1
        return data

    def __get_uid(self, index: int) -> str:
        """Gets a UID forr an event.

        Parameters
        ----------
        index: int
            The index of the event
        """
        date = self._get_value("Start Date", index)
        subject = self._get_value("Subject", index)
        start = self._get_value("Start Time", index)
        end = self._get_value("End Time", index)

        return f"{date}-{subject}-{start}-{end}"

    def add(self, key: str, value: Any) -> None:
        """Adds the value to the specific key.

        Paramters
        ---------
        key: str
            The key of the value to set
        value: Any
            Value to add to the list
        """
        if key not in self.keys():
            raise ValueError(f"{key} is not a valid key.")

        self[key].append(value)

    def set(self, key: str, value: Iterable) -> None:
        """Replace the value of the specific key to the given value.

        Paramters
        ---------
        key: str
            The key of the value to set
        value: Iterable
            Iterable to set to
        """
        if key not in self.keys():
            raise ValueError(f"{key} is not a valid key.")

        if not isinstance(value, Iterable):
            raise ValueError("Value is not an iterable")

        super().__setitem__(key, list(value))

    def __setitem__(self, key: Any, value: Any) -> NoReturn:
        """Raises TypeError when doing self[key] = value.
        Use self.set or self.add instead.
        """
        raise TypeError("Use set/add instead to set values")

    def _sort_values(self, sorting_keys: list[Any] = None) -> None:
        """Sort all the value

        Parameters
        ----------
        sorting_keys: list[Any]
            The keys to sort by
            Defaults is "Start Date" -> "Start Time" -> "Subject"
        """
        # Sorting Keys
        # Making a copy of need values
        self._sorting_keys = []
        if sorting_keys is None:
            self._sorting_keys.append(self["Start Date"].copy())
            self._sorting_keys.append(self["Start Time"].copy())
            self._sorting_keys.append(self["Subject"].copy())
        else:
            for item in sorting_keys:
                self._sorting_keys.append(self[item].copy())
        # Looping over all values
        for items in self.values():
            self.__current_index = 0
            items.sort(key=self.__get_sort_values)

    def _get_value(self, key: str, index: int) -> Any:
        """Gets the event data of the key at the index.
        None will be returned if the index is out of range.

        Parameters
        ----------
        key: str
            The key of the value to get
        index: int
            The index the event
        """
        try:
            return self[key][index]
        except IndexError:
            return None
        except TypeError as err:
            raise ValueError("Invalid Key") from err


# Requester
def make_request(program_value: str, days: list[int],
                 weeks: list[int]) -> ScheduleData:
    """Make the http request to retrieve data.

    Prameters
    ---------
    program_value: str
        The program value of the program to request
    days: list[int]
        A list of day of week to request
    weeks: list[int]
        A list of weeks to request

    Returns
    -------
    ScheduleData
        The data fetch
    """
    link = f"http://timetablingunmc.nottingham.ac.uk:8016/reporting/\
TextSpreadsheet;programme+of+study;id;{program_value}%0D%0A?\
days=1-7&weeks=1-52&periods=3-20&template=SWSCUST+programme+of+study+TextSpreadsheet&\
height=100&week=100"

    response: requests.Response = requests.get(link, timeout=10)
    text = response.text

    return parse_response(text, days, weeks)


def parse_response(response: str, days: list[int],
                   weeks: list[int]) -> ScheduleData:
    """Parses the HTML response into a ScheduleData Object.

    Parameters
    ----------
    response: str
        The Response of the HTTP request
    days: list[int]
        A list of day of week to request
    weeks: list[int]
        A list of weeks to request

    Returns
    -------
    ScheduleData
        The data object
    """
    parser = ScheduleParser(days)
    parser.feed(response)
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

    return schedule_data
