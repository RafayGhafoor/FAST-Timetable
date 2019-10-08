# Probably add some time library in future for better time manipulation
def generate_end_time(start_time, lab_course=False):
    # TODO: Timing for lab [X]
    # TODO: Interval check am -> pm conversion
    time, interval = start_time.split()
    hour, minute = [int(i) for i in time.split(':')]
    if lab_course:
        # TODO: Simplify this!
        if hour + 3 >= 12:  # TODO: Add unit tests, need to check this condition
            interval = 'p.m.'
        if hour + 3 > 12:
            hour -= 12
        return f'{hour+3}:{str(minute).zfill(2)} {interval}'

    if hour >= 12:
        hour = 0
    hour += 1
    minute += 20

    if minute >= 60:
        hour += 1
        minute -= 60
    return f'{hour}:{str(minute).zfill(2)} {interval}'
