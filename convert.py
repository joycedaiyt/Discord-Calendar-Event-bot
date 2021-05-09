import datetime
import os


def convert_to_RFC_datetime(year, month, day, hour, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat()  # + "Z"
    return dt
