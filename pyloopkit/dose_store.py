from datetime import datetime, timedelta
from . import insulin_math
from .dose_entry import *

class BasalSchedule:
    """ Exposes a simplified api to InsulinMath that abstracts away
        profile definition sets
    """
    def __init__(self, profile_definition_set):
        self.profile_definition_set = profile_definition_set

    def between(self, start_date, end_date):
        active_profile_def = self.profile_definition_set.get_profile_definition_active_at(start_date)
        profile = active_profile_def.get_default_profile()
        return profile.basal.between(start_date, end_date)

class DoseStore:
    """ DoseStore backed by Nightscout """
    def __init__(self, ns_client):
        self.ns_client = ns_client

    def treatment_to_dose(self, treatment):
        if treatment.eventType == 'Temp Basal':
            end_date = treatment.timestamp + timedelta(minutes=treatment.duration)
            return DoseEntry(DoseEntryType.TempBasal, treatment.timestamp, end_date, treatment.rate, DoseUnit.UnitsPerHour)
        if treatment.eventType == 'Correction Bolus':
            return DoseEntry(DoseEntryType.Bolus, treatment.timestamp, treatment.timestamp, treatment.insulin, DoseUnit.Units)
        if treatment.eventType == 'Meal Bolus' and treatment.insulin != None:
            return DoseEntry(DoseEntryType.Bolus, treatment.timestamp, treatment.timestamp, treatment.insulin, DoseUnit.Units)
        if treatment.eventType == 'Suspend Pump':
            return DoseEntry(DoseEntryType.Suspend, treatment.timestamp, treatment.timestamp, 0, DoseUnit.UnitsPerHour)
        if treatment.eventType == 'Resume Pump':
            return DoseEntry(DoseEntryType.Resume, treatment.timestamp, treatment.timestamp)

    def ns_treatments_to_doses(self, treatments):
        return filter(None, [self.treatment_to_dose(t) for t in treatments])

    def in_date_range(self, dose, start_date, end_date):
        if start_date and dose.end_date < start_date:
            return False
        if end_date and dose.start_date > end_date:
            return False
        return True

    def filter_date_range(self, doses, start_date, end_date):
        return filter(lambda x: self.in_date_range(x, start_date, end_date), doses)

    def fetch_treatments(self, start_date, end_date = None):
        query = {'count':0} # Don't limit by count
        if end_date:
            query['find[created_at][$lte]'] = end_date.isoformat()

        # Look 6 hours before start date, since an active temp basal could
        # have a long duration and have a timestamp much earlier than start_date
        # but still be delivering at start_date
        query['find[created_at][$gte]'] = (start_date - timedelta(hours=6)).isoformat()

        return self.ns_client.get_treatments(query)

    # Retrieves dose entries normalized to the current basal schedule.
    def get_normalized_dose_entries(self, start_date, end_date = None):

        treatments = self.fetch_treatments(start_date, end_date)

        doses = self.ns_treatments_to_doses(treatments)

        profiles = self.ns_client.get_profiles()

        doses = [d for d in doses if d.start_date]

        doses.sort(key=lambda x: x.start_date)

        # This adjusts start and stop times of overlapping records to reflect when
        # They were actually active.
        reconciled_doses = insulin_math.reconcile_doses(doses)

        # This normalizes rates against the basal schedule.  Rates can be negative
        # after this transformation
        basal_schedule = BasalSchedule(profiles)
        normalized_doses = insulin_math.normalize(reconciled_doses, basal_schedule)

        return self.filter_date_range(normalized_doses, start_date, end_date)
