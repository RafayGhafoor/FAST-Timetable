from openpyxl import load_workbook
import re


class Reader:
    DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')

    def __init__(self, filename):
        self.filename = filename
        self.wb_obj = load_workbook(filename=self.filename)
        self.sheet_obj = self.wb_obj.active
        self.info = list(self.sheet_obj.values)
        self.periods = self.info[2]
        self.timings = self.info[3]

    def extract_courses_with_sections(self):
        '''
        Extracts all courses from xlsx file which are being offered.

        @args:
            content: XLSX content.
        '''
        subjects = []

        for row in self.info[4:-3]:
            for subject in row[2:]:
                if subject:
                    subjects.append(subject)

        return subjects

    def filter_courses(self):
        '''
        Strips sections from the name of courses and returns only name of the courses being offered.
        '''
        return sorted({i.split('(')[0].strip() for i in self.extract_courses_with_sections()})

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
                    minute += self.periods[sheet_location-1]
                    time = f'{hour}:{str(minute).zfill(2)} {interval}'
                    break
        else:
            time = self.timings[sheet_location]

        return time

    def generate_end_time(self, start_time):
        # TODO: Timing for lab
        # 9:30
        time, interval = start_time.split()
        hour, minute = [int(i) for i in time.split(':')]
        hour += 1
        minute += 20
        if minute >= 60:
            hour += 1
            minute -= 60
        return f'{hour}:{str(minute).zfill(2)} {interval}'

    def get_venue(self, content):
        return content[1]

    def get_section(self, name):
        '''
        Obtain section from course name.
        '''
        sections = re.findall(r'CS-?\w?\d?', name)
        return tuple(sections)

    def display_courses(self):
        for i in self.extract_courses_with_sections():
            section = self.get_section(i)
            if section:
                print(section)
            else:
                print(i)

    def get_days_info(self):
        count = 0

        DAYS_INFO = {k: [] for k in self.DAYS}

        for row in self.info[4:-3]:
            if row[0]:
                if row[0].strip() == self.DAYS[count]:
                    count += 1
            DAYS_INFO[self.DAYS[count-1]].append(row)

        return DAYS_INFO

    def get_timing(self, course_name=''):
        course_name = 'Applied Physics  (CS-C)'
        DAYS_INFO = self.get_days_info()
        for n, i in enumerate(DAYS_INFO['Monday'][10]):
            if i:
                if i == course_name:
                    index = n

        a = self.get_course_time(course_name, index)
        b = self.generate_end_time(a)
        print(f'{a} - {b}')
        print(self.get_venue(DAYS_INFO['Monday'][10]))


if __name__ == "__main__":
    abc = Reader('cs.xlsx')
    # abc.display_courses()
    # print(abc.extract_courses_with_sections())
    print(abc.get_timing())
