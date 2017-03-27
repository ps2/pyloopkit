from enum import Enum

class DoseEntryType(Enum):
    Bolus = 1
    Suspend = 2
    Resume = 3
    TempBasal = 4

class DoseUnit(Enum):
    UnitsPerHour = "U/hour"
    Units = "U"

class DoseEntry:
    def __init__(self, dose_entry_type, start_date, end_date = None, value = None, unit = None, description = None):
        self.dose_entry_type = dose_entry_type
        self.start_date = start_date
        self.end_date = end_date
        self.value = value
        self.unit = unit
        self.description = description

    def as_dict(self):
        return dict(
            dose_entry_type=self.dose_entry_type,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            value=self.value,
            unit=self.unit,
            description=self.description,
            )
