import time


def get_formatted_time_elapsed(x):
    starter = x
    seconds1 = time.time() - starter
    seconds2 = seconds1 % 60
    minutes = int((seconds1 / 60) % 60)
    hours = int((seconds1 / 60 / 60))
    timer = f"(Time elapsed: {hours}h:{minutes}m:{round(seconds2, 4)}s)"
    return timer
