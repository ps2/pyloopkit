from carb_store import CarbEntry
from date_math import *
from datetime import timedelta


def interpolate_entries_to_timeline(entries, start_date=None, end_date=None, delta=timedelta(minutes=5)):

    if start_date == None:
        start_date = date_floored_to_time_interval(entries[0].start_date, delta)

    if end_date == None:
        end_dates = [e.start_date for e in entries]
        end_dates.sort()
        end_date = date_ceiled_to_time_interval(end_dates[-1], delta)

    output = []
    num_entries = int((end_date - start_date).total_seconds() / delta.total_seconds())
    #print "%s - %s = %d entries" % (start_date, end_date, num_entries)
    for offset in range(num_entries):
        date = start_date + timedelta(seconds=((offset+1)*delta.total_seconds()))
        output.append(CarbEntry(date, 0, None, None))

    def date_to_offset(date):
        ceiled_date = date_ceiled_to_time_interval(date, delta)
        return int((ceiled_date - start_date).total_seconds() / delta.total_seconds()) - 1

    for entry in entries:
        offset = date_to_offset(entry.start_date)
        #print "offset = %d" % offset
        if offset >= 0 and offset < num_entries:
            output[offset].quantity += entry.quantity

    return output
