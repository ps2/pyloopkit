from dose_entry import *

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

                # Ignore 0-duration doses
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

def normalize_basal_dose(dose, profile):
    return [dose]

def normalize(doses, profiles):
    normalized = []
    for dose in doses:
        if dose.unit == DoseUnit.UnitsPerHour:
            profile = profiles.get_profile_definition_active_during(dose.start_date).get_default_profile()
            normalized.extend(normalize_basal_dose(dose, profile))
        else:
            normalized.append(dose)
    return doses
