from openpyxl import load_workbook
import re
import os
from pony.orm import *

import utils
from format import Course

db = Database()


class DBCourse(db.Entity):
    name = Required(str)
    section = Required(str)
    start_time = Required(float)
    end_time = Required(float)
    room = Required(str)
    day = Required(str)


class Reader:
    DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")

    def __init__(self, filename):
        self.info = list(load_workbook(filename=filename).active.values)
        self.periods = self.info[2]
        self.timings = self.info[3]
        self.content = self.info[4:-3]

    def get_courses(self, sections=True):
        """
        Extracts all courses from xlsx file which are being offered.
        """
        subjects = []

        for row in self.content:
            # TODO: Why first two indexes are missed? [Add Documentation]
            for subject in row[2:]:
                if subject:
                    subjects.append(subject.strip())

        if sections:
            return subjects

        return sorted({i.split("(")[0].strip() for i in subjects})

    def get_course_time(self, name, sheet_location):
        """
        Obtain lecture timings for course.

        @args:
            name: Name of the course
            sheet_location: index of name in sheet (required to interpret lecture timing)
        """
        if not self.timings[sheet_location]:
            for i in range(sheet_location)[::-1]:
                if self.timings[i]:
                    time, interval = self.timings[i].split()
                    interval = interval.replace('.', '').upper()
                    hour, minute = [int(i) for i in time.split(":")]
                    minute += self.periods[sheet_location - 1]
                    time = f"{hour}:{str(minute).zfill(2)} {interval.replace('NOON', 'PM')}"
                    break
        else:
            time = self.timings[sheet_location].replace(
                '.', '').upper().replace('NOON', 'PM')

        return time

    def get_venue(self, content):
        return content[1]

    def get_section(self, name):
        """
        Obtain section from course name.
        """
        sections = re.findall(r"CS-?\w?\d?", name)
        return ", ".join(sections)

    def display_courses(self, sections=True):
        for i in self.get_courses(sections=sections):
            section = self.get_section(i)
            if section:
                print(i)
            else:  # When no sections are found for the course, Probably a MS-Course
                print(i)

    def get_days_info(self):
        count = 0

        DAYS_INFO = {k: [] for k in self.DAYS}
        # Day [0] -> Data Stored for Day 0 which is Monday
        # Day [1] -> Data Stored for Day 1 which is Tuesday

        for row in self.content:
            if row[0]:
                if row[0].strip() == self.DAYS[count]:
                    count += 1
            DAYS_INFO[self.DAYS[count - 1]].append(row)

        return DAYS_INFO

    @db_session
    def dump_to_db(self):
        """
        Returns list of course objects
        """
        DAYS_INFO = self.get_days_info()
        # TODO: Simplify this logic
        for day in self.DAYS:
            for column in range(len(DAYS_INFO[day])):
                for index, course_title in enumerate(DAYS_INFO[day][column]):
                    if course_title and ' (' in course_title:
                        # https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
                        course_title = " ".join(course_title.split())

                        course_start_timing = self.get_course_time(
                            course_title, index)

                        is_lab_course = True if "lab" in course_title.lower(
                        ) else False

                        course_end_timing = utils.generate_end_time(
                            course_start_timing, lab_course=is_lab_course)

                        section = self.get_section(course_title)

                        try:
                            DBCourse(
                                name=course_title,
                                section='CS' if not section else section,
                                start_time=utils.convert_to_24h(
                                    course_start_timing),
                                end_time=utils.convert_to_24h(
                                    course_end_timing),
                                room=self.get_venue(DAYS_INFO[day][column]),
                                day=day, )
                        except Exception as e:
                            print(e)


def export_timetable(export_directory, courses=None, dump_type="json"):
    if dump_type == "json":
        export_directory += "json/"
    else:
        export_directory += "text/"

    with db_session:
        my_dict = {}

        for course in select(c for c in DBCourse)[:]:
            for entity in courses:
                # print("%r - %r" % (entity, course.name))
                if entity in course.name:
                    section = re.search(r'CS-\w', course.section)
                    section = section.group() if section else course.section

                    export_entity = Course(
                        course.name, course.room, course.day, course.section,
                        utils.convert_to_12h(course.start_time),
                        utils.convert_to_12h(course.end_time))

                    if section not in my_dict.keys():
                        my_dict[section] = []

                    if dump_type == "json":
                        my_dict[section].append(export_entity.to_dict())
                    else:
                        my_dict[section].append(export_entity.get_text())

        for k, v in my_dict.items():
            if dump_type == "json":
                export_entity.write_to_file(
                    export_directory + k + ".json", data=v, dump_type=dump_type)
            else:
                export_entity.write_to_file(
                    export_directory + k + ".txt", data=v, dump_type=dump_type)


if __name__ == "__main__":

    files_path = "source_files/"
    output_path = "course_files/"
    test_files = {"old": "old.xlsx", "new": "new.xlsx"}
    timetable = Reader(files_path + test_files.get("old"))
    db.bind(provider="sqlite", filename="database_mod.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)

    # timetable.dump_to_db()
    # timetable.display_courses()

    courses = ('Discrete', 'Data Structures', 'Assembly',
               'Finance and Accounting', 'Linear Algebra')

    # Cleanup
    for i in os.listdir(output_path):
        if os.path.isfile(i):
            os.remove(output_path + i)

    print("Extracting timetable for given courses:")
    for i in courses:
        print(">>> ", i)

    export_timetable(output_path, courses=courses, dump_type='text')