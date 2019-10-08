from openpyxl import load_workbook
import re
import utils
from format import Course


class Reader:
    DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')

    def __init__(self, filename):
        self.info = list(load_workbook(filename=filename).active.values)
        self.periods = self.info[2]
        self.timings = self.info[3]
        self.content = self.info[4:-3]

    def get_courses(self, sections=True):
        '''
        Extracts all courses from xlsx file which are being offered.
        '''
        subjects = []

        for row in self.content:
            #TODO: Why first two indexes are missed? [Add Documentation]
            for subject in row[2:]:
                if subject:
                    subjects.append(subject.strip())

        if sections:
            return subjects

        return sorted({i.split('(')[0].strip() for i in subjects})

    def get_course_time(self, name, sheet_location):
        '''
        Obtain lecture timings for course.

        @args:
            name: Name of the course
            sheet_location: index of name in sheet (required to interpret lecture timing)
        '''
        if not self.timings[sheet_location]:
            for i in range(sheet_location)[::-1]:
                if self.timings[i]:
                    time, interval = self.timings[i].split()
                    hour, minute = [int(i) for i in time.split(':')]
                    minute += self.periods[sheet_location - 1]
                    time = f'{hour}:{str(minute).zfill(2)} {interval}'
                    break
        else:
            time = self.timings[sheet_location]

        return time

    def get_venue(self, content):
        return content[1]

    def get_section(self, name):
        '''
        Obtain section from course name.
        '''
        sections = re.findall(r'CS-?\w?\d?', name)
        return tuple(sections)

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

    def get_timing(self, course_name):
        DAYS_INFO = self.get_days_info()
        meta_info = {
            "name": course_name,
            "section": [],
            "timing": [],
            "room": [],
            "days": []
        }

        # TODO: Simplify this logic
        for day in self.DAYS:
            for column in range(len(DAYS_INFO[day])):
                for index, course_title in enumerate(DAYS_INFO[day][column]):
                    if course_title:
                        if course_name in course_title:
                            # if i == course_name:
                            meta_info["section"] = self.get_section(
                                course_title)

                            course_start_timing = self.get_course_time(
                                course_name, index)

                            is_lab_course = True if 'lab' in course_title.lower(
                            ) else False

                            course_end_timing = utils.generate_end_time(
                                course_start_timing, lab_course=is_lab_course)

                            meta_info[
                                'timing'] = f'{course_start_timing} - {course_end_timing}'

                            meta_info['room'] = self.get_venue(
                                DAYS_INFO[day][column])

                            meta_info['days'] = day

                            print(
                                f'Name: {course_title}\nSection: {meta_info["section"]}\nDay: {day}\nTimings: <{course_start_timing} - {course_end_timing}>\nVenue: <{self.get_venue(DAYS_INFO[day][column])}>\n\n'
                            )
                            # return (day, col, index)
        # return meta_info

    def get_info(self, courses=None):
        if courses:
            COURSES = courses
        else:
            COURSES = self.get_courses()

        for i in COURSES:
            self.get_timing(i)
            input()
            # print(Course.from_dict(self.get_timing(i)))
            # input()
            # print(f"Course: {i}")
            # Course(name=i, section=self.get_section(i), timing=self.get_timing(i), room=, days=)
            # self.get_timing(course_name=i)
            # print()


if __name__ == "__main__":
    courses = ("Discrete Structures", "Linear Algebra",
               "Comp. Organization and Assembly Lang", "Data Structures",
               "Finance and Accounting")

    abc = Reader('cs.xlsx')
    abc.get_info(courses=courses)

    # abc.display_courses()

    # while (1):
    # name = input("Please enter course name: ")
    # abc.get_timing(name)

    # for i in abc.filter_courses():
    #     print(i)
