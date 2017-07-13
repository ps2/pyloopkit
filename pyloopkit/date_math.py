from datetime import datetime
import math
import pytz

def date_floored_to_time_interval(date, delta):
    num_intervals = math.floor((date - datetime.fromtimestamp(0, pytz.utc)).total_seconds() / delta.total_seconds())
    return datetime.fromtimestamp(num_intervals * delta.total_seconds(), date.tzinfo)

def date_ceiled_to_time_interval(date, delta):
    num_intervals = math.ceil((date - datetime.fromtimestamp(0, pytz.utc)).total_seconds() / delta.total_seconds())
    return datetime.fromtimestamp(num_intervals * delta.total_seconds(), date.tzinfo)
