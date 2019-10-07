def generate_end_time(start_time):
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
