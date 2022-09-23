# Nott Your Timetable
Exports Timetable for University of Nottingham Malaysia Student.

# Installation
## Cloning Repo
``` sh
git clone https://github.com/IEEE-UNM/nott-your-timetable.git
cd nott-your-timetable
```
## Installing requirements
### Using Pipenv
``` sh
pipenv install
```
### Using venv/pip
Activate your virtual environment then:
``` sh
pip install -r requirements.txt
```

# Usage
A simple usage to export the entire year to a ics file by default.

**Note:** The quotes are needed if you are putting spaces inbetween

Gets the timetable for Electrical and Electronic Engineering BEng Year 2:

```sh
./nott-your-timetable -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering"
```

Only for week 1 to week 10.

```sh
./nott-your-timetable -w '1-10' -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering"
```

Only for Monday to Friday.

```sh
./nott-your-timetable -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -d 1-5
```

Only for week 4 to week 6 Monday to Friday.

```sh
./nott-your-timetable -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -d '4, 5, 6' -w 1-5
```

If you don't know what school/division and program, the `-i` flag can be used to ender interactive mode.

```sh
./nott-your-timetable -i
```

To export the output to csv
```sh
./nott-your-timetable -c "E & EE" "BEng Hons Electl & Electnc Eng/F/02 - H603 Electrical and Electronic Engineering" -o csv
```

There are more options available, to see all the options use the help argument.

```sh
./nott-your-timetable -h
```


# TODO
  * [ ] Support for exporting to other formats
    * [x] CSV
    * [x] iCalander
    * [ ] vCard
  * [x] Support for other course programs
  * [x] Add more convinience option e.g. Schedule for Spring Semester
  * [ ] A graphical frontend
  * [ ] Add GUI and TUI for displaying timetable
  * [ ] Make use of [Calender Object](https://docs.python.org/3/library/calendar.html)
  * [ ] Add Export Options
  * [x] Add better help descriptions
  * [ ] Support for mutiple program selection
