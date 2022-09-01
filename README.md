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
A simple usage to export the entire year to a csv.
*Note:* The quotes are needed if you are putting spaces inbetween
``` sh
./nott-your-timetable
```
Only for week 1 to week 10.
``` sh
./nott-your-timetable -w '1-10'
```
Only for Monday to Friday.
``` sh
./nott-your-timetable -d 1-5
```
Only for week 4 to week 6 Monday to Friday.
``` sh
./nott-your-timetable -d '4, 5, 6' -w 1-5
```
For more information use the help flag:
``` sh
./nott-your-timetable -h
```


# TODO
  * [ ] Support for exporting to other formats
  * [ ] Support for other course programs
  * [ ] Add more convinience option e.g. Schedule for Spring Semester
  * [ ] A graphical frontend
  * [ ] Add GUI and TUI for displaying timetable
  * [ ] Make use of [Calender Object](https://docs.python.org/3/library/calendar.html)
  * [ ] Add Export Options
  * [ ] Add better help descriptions
