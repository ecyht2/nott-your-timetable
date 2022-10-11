#!/usr/bin/env python3
"""GUI related functions."""
import gi
from .utils.data import get_data, get_convinience_weeks, get_convinience_days
from .utils.range_handlers import handle_ranges_days
from .utils.parsers import parse_response, get_program_value, ScheduleData
gi.require_version("Gtk", "4.0")  # pylint: disable=wrong-import-position
from gi.repository import Gtk, Gio, GLib  # noqa: E402


class NottWindow(Gtk.ApplicationWindow):
    """Main Window for nott-your-timetable."""
    def __init__(self, *args, **kwargs):
        super().__init__(title="Nott Your Timetable", *args, **kwargs)

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
        weeks, days = self.__setup_weeks_days()
        # Setting Up File Format Options
        output = self.__setup_output_format()

        # Continue Button
        button = Gtk.Button(label="Continue")
        button.connect("clicked", self.switch_export, schools, programs["box"],
                       weeks, days, output)
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

        return tuple(output)

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

    def switch_export(
            self, button: Gtk.Button, schools: Gtk.ComboBoxText,
            programs: Gtk.ListBox, weeks: Gtk.ComboBoxText,
            days: Gtk.ComboBoxText, output: Gtk.ComboBoxText
    ) -> None:
        """Callback when the continue button is pressed in the export options\
page.

        Prameters
        ---------
        button: Gtk.Button
            The continue button
        schools: GObject.ComboBoxText
            The combobox used to store the schools
        programs: Gtk.ListBox
            The listbox storing the programs
        weeks: Gtk.ComboBoxText
            The combobox used to store the weeks
        days: Gtk.ComboBoxText
            The combobox used to store the days
        output: Gtk.ComboBoxText
            The combobox used to store the output format
        """
        # Getting convinience datas
        convinience: dict[dict[str, str]] = {
            "days": get_convinience_days(),
            "weeks": get_convinience_weeks()
        }

        if not self.__get_export_options(schools, programs, weeks,
                                         days, output):
            return

        # Checking if all settings were is filled
        if any([value is None or value == "" for value in
                self.export_options.values()]):
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

    def __get_export_options(self, schools: Gtk.ComboBoxText,
                             programs: Gtk.ListBox, weeks: Gtk.ComboBoxText,
                             days: Gtk.ComboBoxText, output: Gtk.ComboBoxText
                             ) -> bool:
        """Gets the export options.

        Prameters
        ---------
        schools: GObject.ComboBoxText
            The combobox used to store the schools
        programs: Gtk.ListBox
            The listbox storing the programs
        weeks: Gtk.ComboBoxText
            The combobox used to store the weeks
        days: Gtk.ComboBoxText
            The combobox used to store the days
        output: Gtk.ComboBoxText
            The combobox used to store the output format
        """
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
        response = Gio.File.new_for_uri(
            "http://timetablingunmc.nottingham.ac.uk:8016/reporting/\
TextSpreadsheet;programme+of+study;id;{0}%0D%0A?\
days=1-7&weeks=1-52&periods=3-20&template=SWSCUST+programme+of+study+TextSpreadsheet&\
height=100&week=100".format(self.export_options.get("program"))
        )
        response.load_contents_async(None, self.handle_response, None)

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

    def handle_response(self, source_object: object, result: Gio.Task,
                        user_data: None) -> None:
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
        # Setting Up File Chooser Dialog
        self.dialog = Gtk.FileChooserNative.new(
            title="Save Output As",
            action=Gtk.FileChooserAction.SAVE,
            parent=self
        )
        self.dialog.set_current_name(
            "output.{}".format(self.export_options.get("format"))
        )

        try:
            # Getting Data
            _, content, _ = source_object.load_contents_finish(result)
        except GLib.GError:
            # Error
            self.main_layout.set_visible_child_name("Error")
        else:
            # Switching to success page
            self.main_layout.set_visible_child_name("Success")
            # Getting and parsing Data
            content = content.decode("utf-8")
            schedule_data = parse_response(
                content,
                self.export_options.get("days"),
                self.export_options.get("weeks")
            )
            # Showing File Chooser Dialog
            self.dialog.connect("response", self.file_chosen, schedule_data)
            self.dialog.show()

    def file_chosen(
            self, dialog: Gtk.FileChooserNative,
            response: Gtk.ResponseType,
            schedule_data: ScheduleData
    ) -> None:
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            schedule_data.export(self.export_options.get("format"), filename)

        dialog.destroy()


class NottApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.nott_your_timetable")
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = NottWindow(application=self)
        win.present()


class BoxWithLabel(Gtk.Grid):
    """A Gtk Box with a label.

    Parameters
    ----------
    label: str
        The label for the widget
    widget: Gtk.Widget
        The widget
    """
    def __init__(self, label: str, widget: Gtk.Widget):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.attach(Gtk.Label(label=label), 0, 0, 1, 1)
        self.attach(widget, 1, 0, 5, 1)
