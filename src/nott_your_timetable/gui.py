#!/usr/bin/env python3
"""GUI related functions."""
from typing import Callable
import requests
import gi
gi.require_version("Gtk", "4.0")
# pylint: disable=wrong-import-position
from gi.repository import Gtk, Gio, GLib, GObject  # noqa: E402
from .utils.data import get_data, get_convinience_weeks,\
    get_convinience_days  # noqa: E402
from .utils.range_handlers import handle_ranges_days   # noqa: E402
from .utils.parsers import get_program_value, ScheduleData,\
    make_request   # noqa: E402
# pylint: enable=wrong-import-position


class MakeRequestWrapper(GObject.Object):
    """MakeRequest is a GObject wrapper for make_request function.

    MakeRequest provides a syncronous and asyncronous way of requesting
    data.

    Parameters
    ----------
    program_value: str
        The Program Value of the program to fetch
    days: list[int]
        The list days to fetch
    weeks: list[int]
        The list of weeks to fetch
    """
    def __init__(self, program_value: str, days: list[int], weeks: list[int]):
        super().__init__()
        self.program_value = program_value
        self.days = days
        self.weeks = weeks
        self.pool = {}

    def make_request_sync(self) -> ScheduleData:
        """Fetch data in a syncronous way."""
        data = make_request(self.program_value, self.days, self.weeks)
        return data

    def make_request_async(self, cancellable: Gio.Cancellable,
                           callback: Callable, *user_data):
        """Fetch data in an asyncronous way.

        Prameters
        ---------
        cancellable: Gio.Cancellable
            Sets if the operation is cancelable
        callback: Callable
            Callback function to use when the process finishes
        *user_data
            User data to pass into callback
        """
        task = Gio.Task.new(self, cancellable, callback, *user_data)

        # If task isn't cancellable
        if cancellable is None:
            task.set_return_on_cancel(False)

        # Setting Task Data
        data = (self.program_value, self.days, self.weeks)
        data_id = id(data)
        self.pool[data_id] = data
        task.set_task_data(data_id, lambda key: self.pool.pop(data_id))

        # Fetching data in different thread
        task.run_in_thread(self.__thread_callback)

    def __thread_callback(self, task: Gio.AsyncResult, worker,
                          task_data: None, cancellable: Gio.Cancellable):
        """Function used when fetching data in a different thread."""
        # pylint: disable=unused-argument
        data_id = task.get_task_data()
        data = self.pool.get(data_id)

        try:
            outcome = make_request(*data)
        except requests.RequestException as error:
            task.return_error(GLib.Error(" ".join(error.args),
                                         "requests-error"))
        else:
            task.return_value(outcome)

    def make_request_finish(self, result: Gio.AsyncResult) -> ScheduleData:
        """Returns the fetch ``ScheduleData`` Object when the asyncronous
        fetching completed.

        Parameters
        ----------
        task: Gio.AsyncResult
            The task used to fetch data asyncronously

        Returns
        -------
        ScheduleData
            The data that is fetched
        """
        value = None

        if Gio.Task.is_valid(result, self):
            value = result.propagate_value().value
        else:
            error = "Gio.Task.is_valid returned False."
            value = {"AsyncWorkerError": error}

        return value


class NottWindow(Gtk.ApplicationWindow):
    """Main Window for nott-your-timetable."""
    def __init__(self, *args, **kwargs):
        super().__init__(title="Nott Your Timetable", *args, **kwargs)

        # Setting up Needed variables
        self.dialog = None

        # Setting up options variables
        self.export_options = {}
        self.output_options = {}

        # Setting up main layout
        self.main_layout = Gtk.Stack()
        # Adding Margins
        self.main_layout.set_property("margin-bottom", 100)
        self.main_layout.set_property("margin-top", 100)
        self.main_layout.set_property("margin-end", 100)
        self.main_layout.set_property("margin-start", 100)

        # Setting up options page
        self.__setup_export_options()
        self.__setup_get_data()
        self.__setup_results()
        self.__setup_error()

        # Adding main stacked layout as the child
        self.set_child(self.main_layout)

    def school_changed(self, box: Gtk.ComboBoxText, listbox: dict) -> None:
        """Callback function when a school/division is selected.

        Parameters
        ----------
        box: Gtk.ComboBoxText
            The school/division combobox
        listbox: dict
            A dictionary containing all the widgets for program selection
        """
        school = box.get_active_id()
        _, programs = get_data()

        # Deleting all keys
        for _ in range(listbox["count"]):
            row = listbox["box"].get_row_at_index(0)
            listbox["box"].remove(row)
        # Reseting count
        listbox["count"] = 0

        # Getting the program
        program = programs.get(school)
        # Returning if there is no program found
        if program is None:
            return

        # Appending new keys
        for key in program:
            listbox["box"].append(Gtk.Label(label=key))
            listbox["count"] += 1

    def __setup_export_options(self):
        """Setup export options."""
        self.options_layout = Gtk.Grid()

        # Stack Label
        self.options_layout.attach(Gtk.Label.new("Select Export Settings"),
                                   0, 0, 2, 1)

        # Setting Up Program Options
        schools = self.__setup_schools()
        # Setting Up School Options
        programs = self.__setup_programs()
        schools.connect("changed", self.school_changed, programs)
        # Setting Up Week and Days Options
        weeks, days, *_ = self.__setup_weeks_days()
        # Setting Up File Format Options
        output = self.__setup_output_format()

        widgets = {
            "schools": schools,
            "programs": programs["box"],
            "weeks": weeks,
            "days": days,
            "output": output
        }

        # Continue Button
        button = Gtk.Button(label="Continue")
        button.connect("clicked", self.switch_export, widgets)
        self.options_layout.attach(button, 0, 6, 2, 1)

        # Adding to main stack layout
        self.main_layout.add_named(self.options_layout, "Options")

    def __setup_results(self):
        """Setup the success page."""
        layout = Gtk.Grid(valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER)

        # Success Label
        layout.attach(Gtk.Label(
            label="Timetable successfully exported.",
        ), 0, 0, 2, 1)

        # Setting up buttons
        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", lambda b: self.destroy())
        show_dialog = Gtk.Button(label="Export Another")
        show_dialog.connect("clicked", lambda b: (
            self.main_layout.set_visible_child_name("Options")
        ))

        # Attaching buttons
        layout.attach(exit_button, 0, 1, 1, 1)
        layout.attach(show_dialog, 1, 1, 1, 1)

        # Adding to main layout
        self.main_layout.add_named(layout, "Success")

    def __setup_error(self):
        """Setup the error page when the data can't be fetch."""
        layout = Gtk.Grid(valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER)

        # Error Label
        layout.attach(Gtk.Label(
            label="An error had occured during the process of fetching data.",
        ), 0, 0, 2, 1)

        # Setting up buttons
        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", lambda b: self.destroy())
        try_again = Gtk.Button(label="Try Again")
        try_again.connect("clicked", lambda b: self.make_request())

        # Attaching buttons
        layout.attach(exit_button, 0, 1, 1, 1)
        layout.attach(try_again, 1, 1, 1, 1)

        # Adding to main layout
        self.main_layout.add_named(layout, "Error")

    def __insert_row(self, row_number: int, label: str,
                     widget: Gtk.Widget) -> None:
        """Adds a new row of items to the options grid layout.

        Prameters
        ---------
        row_number: int
            The row number to insert at
        label: str
            The label of the widget
        widget: Gtk.Widget
            The gtk widget to insert
        """
        self.options_layout.attach(Gtk.Label(label=label), 0, row_number, 1, 1)
        self.options_layout.attach(widget, 1, row_number, 1, 1)

    def __setup_schools(self) -> Gtk.ComboBoxText:
        """Setting Up School/Division Options.

        Returns
        -------
        Gtk.ComboBoxText
            The resultant combobox widget
        """
        courses, _ = get_data()

        schools = Gtk.ComboBoxText()
        for key, value in courses.items():
            schools.append(value, key)
        self.__insert_row(1, "Select School/Division: ", schools)

        return schools

    def __setup_programs(self) -> dict:
        """Setting Up School Options.

        Returns
        -------
        dict
            A dict containing all the widgets and needed values
        """
        programs = {}
        programs["box"] = Gtk.ListBox()
        programs["count"] = 0
        programs["scroller"] = Gtk.ScrolledWindow(vexpand=True)
        programs["scroller"].set_child(programs["box"])
        self.__insert_row(2, "Select Program: ", programs["scroller"])

        return programs

    def __setup_weeks_days(self) -> tuple[Gtk.ComboBoxText]:
        """Setting Up Week and Days options."""
        # Setting Up values
        convinience_values = [get_convinience_weeks(), get_convinience_days()]
        labels = ["Select Week(s) or Semester: ",  "Select Day(s): "]
        index = list(range(3, 5))

        output = []
        # Looping over weeks and days
        for con, label, i in zip(convinience_values, labels, index):
            combo = Gtk.ComboBoxText.new_with_entry()
            # Adding convinience values
            for key, value in con.items():
                combo.append(value, key)
            # Inserting rows and adding to output tuple
            self.__insert_row(i, label, combo)
            output.append(combo)

        output = tuple(output)
        return output

    def __setup_output_format(self) -> Gtk.ComboBoxText:
        """Setting Up File Format Options.

        Returns
        -------
        Gtk.ComboBoxText
            The comboboxtext widget for the file format option
        """
        file_format = Gtk.ComboBoxText()
        for i in ["csv", "ics"]:
            file_format.append(i, i)
        # Setting Default Value
        file_format.set_active_id("ics")
        # Adding to layout
        self.__insert_row(5, "Select Output Format: ", file_format)

        return file_format

    def switch_export(self, button: Gtk.Button,
                      widgets: dict[Gtk.Widget]) -> None:
        """Callback when the continue button is pressed in the export options\
page.

        Prameters
        ---------
        button: Gtk.Button
            The continue button
        widgets: GtkWidget
            A dictionary widgets of all the widgets used for setting up export\
options
        """
        # pylint: disable=unused-argument
        # Getting convinience datas
        convinience: dict[dict[str, str]] = {
            "days": get_convinience_days(),
            "weeks": get_convinience_weeks()
        }

        if not self.__get_export_options(
                widgets
        ):
            return

        # Checking if all settings were is filled
        if any(value is None or value == "" for value in
                self.export_options.values()):
            self.show_error()
            return

        # Checking Validity of week and day ranges
        for i in ["weeks", "days"]:
            data: str = self.export_options.get(i)
            try:
                # Checking if it is a convinience day range
                if data not in convinience.get(i):
                    # If it is a range
                    self.export_options[i]: list[int] = handle_ranges_days(
                        data
                    )
                else:
                    # If it is a convinience range
                    self.export_options[i]: list[int] = handle_ranges_days(
                        convinience.get(i).get(data)
                    )
            except ValueError:
                # Invalid Ranges
                self.show_error()
                return

        self.main_layout.set_visible_child_name("Loading")
        self.spinner.start()
        self.make_request()

    def __get_export_options(self, widgets: dict[Gtk.Widget]) -> bool:
        """Gets the export options.

        Prameters
        ---------
        widgets: dict[Gtk.Widget]
            A dictionary widgets of all the widgets used for setting up export\
options
        """
        schools = widgets.get("schools")
        programs = widgets.get("programs")
        weeks = widgets.get("weeks")
        days = widgets.get("days")
        output = widgets.get("output")
        # Getting all the settings
        try:
            self.export_options["division"] = schools.get_active_text()
            self.export_options["program"] = programs.get_selected_row().\
                get_child().get_text()
            self.export_options["weeks"] = weeks.get_active_text()
            self.export_options["days"] = days.get_active_text()
            self.export_options["program"] = get_program_value(
                self.export_options.get("division"),
                self.export_options.get("program")
            )
            self.export_options["format"] = output.get_active_text()
        except AttributeError:
            # No division provided
            self.show_error()
            return False

        return True

    def make_request(self) -> None:
        """Make request for the raw HTML file."""
        self.main_layout.set_visible_child_name("Loading")
        response = MakeRequestWrapper(
            self.export_options.get('program'),
            self.export_options.get("days"),
            self.export_options.get("weeks")
        )
        response.make_request_async(None, self.handle_response, None)

    def show_error(self) -> None:
        """Function that shows an error dialog."""
        # Setting Up Dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text="Invalid Settings",
        )
        dialog.set_property(
            "secondary-text",
            "Please check inserted settings."
        )

        # Window Closing Handler
        dialog.connect("response", lambda dialog, res_id: dialog.destroy())
        # Showing Dialog
        dialog.show()

    def __setup_get_data(self):
        """Loading screen for for requesting data."""
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                         valign=Gtk.Align.CENTER)

        self.spinner = Gtk.Spinner()
        layout.append(self.spinner)
        layout.append(Gtk.Label(label="Fetching Data"))

        self.main_layout.add_named(layout, "Loading")

    def handle_response(self, source_object: MakeRequestWrapper,
                        result: Gio.AsyncResult, user_data: None) -> None:
        """Callback Function to handle the raw data HTML page.

        Paramters
        ---------
        source_object: __gi__.GDaemonFile
            The File Recived
        result: Gio.Task
            The Task object
        user_data: None
            User Data for the callback
        """
        # pylint: disable=unused-argument
        # Setting Up File Chooser Dialog
        self.dialog = Gtk.FileChooserNative.new(
            title="Save Output As",
            action=Gtk.FileChooserAction.SAVE,
            parent=self
        )
        self.dialog.set_current_name(
            f"output.{self.export_options.get('format')}"
        )

        try:
            # Getting Data
            schedule_data = source_object.make_request_finish(result)
        except GLib.GError:
            # Error
            self.main_layout.set_visible_child_name("Error")
        else:
            # Switching to success page
            self.main_layout.set_visible_child_name("Success")

            # Showing File Chooser Dialog
            self.dialog.connect("response", self.file_chosen, schedule_data)
            self.dialog.show()

    def file_chosen(
            self, dialog: Gtk.FileChooserNative,
            response: Gtk.ResponseType,
            schedule_data: ScheduleData
    ) -> None:
        """Logic when user chosen filename to save to.

        Parameters
        ----------
        dialog: Gtk.FileChooserNative
            The file selction dialog.
        response: Gtk.ResponseType
            The response code of the dialog e.g. (Accepted/Cancel/Quitted).
        schedule_data: ScheduleData
            The ScheduleData object of the fetched data.
        """
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            schedule_data.export(self.export_options.get("format"), filename)

        dialog.destroy()


class NottApp(Gtk.Application):
    # pylint: disable=too-few-public-methods
    """GTK application for nott-your-timetable."""
    def __init__(self):
        super().__init__(application_id="io.github.nott_your_timetable")
        self.connect('activate', self.on_activate)
        self.win = None

    def on_activate(self, app):
        """Activation Logic for application."""
        self.win = NottWindow(application=app)
        self.win.present()
