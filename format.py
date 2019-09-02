class Course:
    def __init__(self, name: string, section: string, timing: tuple, room: tuple, days: tuple):
        '''
        @args:
        Name: Name of the course
        Section: Section of the course
        Timing: Timing of the course (start-time; end-time)
        Room: Venue of the course

        @Example:
        name: Linear Algebra
        section: CS-A
        timing: ((9:30, 10:50),(...))
        room: (CS-2)
        '''
        self.name = name
        self.section = section
        self.timing = timing
        self.room = room
        self.days = days
        self.course_type = 'BS' if 'MS' not in self.name else 'MS'

    def is_lab_course(self):
        return 'lab' in self.name.lower()
    
    def __repr__(self):
        return f'{self.name - self.section}'
    
    def __str__(self):
        return f'{self.name - self.section}'
