from dose_entry import *
from datetime import timedelta
from date_math import *
from insulin_value import *

def reconcile_doses(doses):
    reconciled = []

    last_suspend = None
    last_temp_basal = None

    for dose in doses:
        if dose.dose_entry_type == DoseEntryType.Bolus:
            reconciled.append(dose)
        if dose.dose_entry_type == DoseEntryType.TempBasal:
            if last_temp_basal:
                end_date = min(last_temp_basal.end_date, dose.start_date)

                # Ignore 0-duration temp basals
                if end_date > last_temp_basal.start_date:
                    reconciled.append(DoseEntry(
                        last_temp_basal.dose_entry_type,
                        last_temp_basal.start_date,
                        end_date,
                        last_temp_basal.value,
                        last_temp_basal.unit,
                        last_temp_basal.description))
            last_temp_basal = dose
        if dose.dose_entry_type == DoseEntryType.Resume:
            if last_suspend:
                description = last_suspend.description or dose.description
                reconciled.append(DoseEntry(
                    last_suspend.dose_entry_type,
                    last_suspend.start_date,
                    dose.end_date,
                    last_suspend.value,
                    last_suspend.unit,
                    description))

                last_suspend = None

            if last_temp_basal:
                if last_temp_basal.end_date > dose.end_date:
                    last_temp_basal = DoseEntry(
                        last_temp_basal.dose_entry_type,
                        dose.end_date,
                        last_temp_basal.end_date,
                        last_temp_basal.value,
                        last_temp_basal.unit,
                        last_temp_basal.description)
                else:
                    last_temp_basal = None

        if dose.dose_entry_type == DoseEntryType.Suspend:
            if last_temp_basal:
                reconciled.append(DoseEntry(
                    last_temp_basal.dose_entry_type,
                    last_temp_basal.start_date,
                    min(last_temp_basal.end_date, dose.start_date),
                    last_temp_basal.value,
                    last_temp_basal.unit,
                    last_temp_basal.description))

                if last_temp_basal.end_date <= dose.start_date:
                    last_temp_basal = None

            last_suspend = dose

    if last_suspend:
        reconciled.append(last_suspend)
    elif last_temp_basal and last_temp_basal.end_date > last_temp_basal.start_date:
        reconciled.append(last_temp_basal)

    return reconciled

def normalize_basal_dose(dose, basal_schedule):
    normalized_doses = []
    basal_items = basal_schedule.between(dose.start_date, dose.end_date)

    for (index, basal_item) in enumerate(basal_items):
        units_per_hour = dose.value - basal_item.value
        start_date = None
        end_date = None

        if index == 0:
            start_date = dose.start_date
        else:
            start_date = basal_item.start_date

        if index == len(basal_items) - 1:
            end_date = dose.end_date
        else:
            end_date = basal_items[index + 1].start_date

        new_dose = DoseEntry(dose.dose_entry_type, start_date, end_date, units_per_hour, DoseUnit.UnitsPerHour, dose.description)
        normalized_doses.append(new_dose)

    return normalized_doses

def normalize(doses, basal_schedule):
    normalized = []
    for dose in doses:
        if dose.unit == DoseUnit.UnitsPerHour:
            normalized.extend(normalize_basal_dose(dose, basal_schedule))
        else:
            normalized.append(dose)
    return normalized

def interpolate_doses_to_timeline(doses, start_date=None, end_date=None, delta=timedelta(minutes=5)):

    if start_date == None:
        start_date = date_floored_to_time_interval(doses[0].start_date, delta)

    if end_date == None:
        end_dates = [d.end_date for d in doses]
        end_dates.sort()
        end_date = end_dates[-1]

    date = start_date
    values = []

    while True:
        value = reduce(lambda sum,dose: sum+dose.units_delivered_during_daterange(date, date+delta), doses, 0)

        date = date + delta
        values.append(InsulinValue(date, value))
        if date >= end_date:
            break

    return values
