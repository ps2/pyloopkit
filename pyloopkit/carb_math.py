from carb_store import CarbEntry
from date_math import *
from datetime import timedelta

def carbs_in_date_range(entry, start_date, end_date):
    if entry.start_date >= start_date and entry.start_date < end_date:
        return entry.quantity
    else:
        return 0

def interpolate_entries_to_timeline(entries, start_date=None, end_date=None, delta=timedelta(minutes=5)):

    if start_date == None:
        start_date = date_floored_to_time_interval(doses[0].start_date, delta)

    if end_date == None:
        end_dates = [d.end_date for d in doses]
        end_dates.sort()
        end_date = end_dates[-1]

    date = start_date
    output = []


    while True:
        value = reduce(lambda sum,entry: sum+carbs_in_date_range(entry, date, date + delta), entries, 0)

        date = date + delta
        output.append(CarbEntry(date, value, None, None))
        if date >= end_date:
            break

    return output
