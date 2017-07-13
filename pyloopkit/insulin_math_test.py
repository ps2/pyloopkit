import unittest
from insulin_math import *
from dose_entry import *
from datetime import datetime, timedelta

class AbsoluteScheduleValue():
    def __init__(self, start_date, value):
        self.start_date = start_date
        self.value = value

    def __repr__(self):
        return "%s = %s" % (self.start_date, self.value)

class MockSchedule():
    def __init__(self, items):
        self.items = items

    def between(self, start_date, end_date):
        start_index = 0
        end_index = len(self.items)

        for index, item in enumerate(self.items):
            if start_date >= item.start_date:
                start_index = index
            if end_date < item.start_date:
                end_index = index
                break
        return self.items[start_index:end_index]


class InsulinMathTestCase(unittest.TestCase):

    def test_reconcile_passes_bolus(self):
        bolus = DoseEntry(DoseEntryType.Bolus, datetime.now(), value = 5, unit = DoseUnit.Units)
        doses = [bolus]
        reconciled_doses = reconcile_doses(doses)
        self.assertEqual(len(reconciled_doses), 1)

    def test_reconcile_should_filter_0_duration_temp_basal(self):
        now = datetime.now()
        temp_basal = DoseEntry(DoseEntryType.TempBasal, now, now, value = 0.7, unit = DoseUnit.UnitsPerHour)
        doses = [temp_basal]
        reconciled_doses = reconcile_doses(doses)
        self.assertEqual(len(reconciled_doses), 0)

    def test_reconcile_should_handle_suspends(self):
        t = datetime.now() - timedelta(days=1)
        doses = [
            DoseEntry(DoseEntryType.TempBasal, t, t+timedelta(minutes=30), value = 3, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.Suspend, t+timedelta(minutes=10)),
            DoseEntry(DoseEntryType.Resume, t+timedelta(minutes=20))]
        reconciled_doses = reconcile_doses(doses)
        print([d.dose_entry_type for d in reconciled_doses])
        self.assertEqual(len(reconciled_doses), 3)
        self.assertEqual(reconciled_doses[0].dose_entry_type, DoseEntryType.TempBasal)
        self.assertEqual(reconciled_doses[0].end_date, t+timedelta(minutes=10))
        self.assertEqual(reconciled_doses[2].start_date, t+timedelta(minutes=20))
        self.assertEqual(reconciled_doses[2].end_date, t+timedelta(minutes=30))

    def test_mock_schedule(self):
        t = datetime(2017,7,7)
        schedule = MockSchedule([
            AbsoluteScheduleValue(t + timedelta(hours=0), 0),
            AbsoluteScheduleValue(t + timedelta(hours=1), 10),
            AbsoluteScheduleValue(t + timedelta(hours=2), 20),
            AbsoluteScheduleValue(t + timedelta(hours=3), 30),
            AbsoluteScheduleValue(t + timedelta(hours=4), 40),
        ])
        self.assertEqual(schedule.between(t + timedelta(minutes=90), t + timedelta(minutes=150)), schedule.items[1:3])

    def test_normalize(self):
        t = datetime(2017,7,7)
        schedule = MockSchedule([
            AbsoluteScheduleValue(t + timedelta(hours=0), 1.2),
            AbsoluteScheduleValue(t + timedelta(hours=1), 0.8),
            AbsoluteScheduleValue(t + timedelta(hours=2), 0.7),
            AbsoluteScheduleValue(t + timedelta(hours=3), 0.9)
        ])
        doses = [
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=00), t+timedelta(minutes=30), value = 1, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=45), t+timedelta(minutes=75), value = 1, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=100), t+timedelta(minutes=130), value = 1, unit = DoseUnit.UnitsPerHour),
        ]

        normalized_doses = normalize(doses,schedule)

        expected_doses = [
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=00), t+timedelta(minutes=30), value=-0.2, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=45), t+timedelta(minutes=60), value=-0.2, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=60), t+timedelta(minutes=75), value=0.2, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=100), t+timedelta(minutes=120), value=0.2, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=120), t+timedelta(minutes=130), value=0.3, unit = DoseUnit.UnitsPerHour),
        ]

        for dose, expected in zip(normalized_doses, expected_doses):
            self.assertAlmostEqual(dose.value, expected.value)
            self.assertEqual(dose.start_date, expected.start_date)
            self.assertEqual(dose.end_date, expected.end_date)

    def test_interpolate_doses_to_timeline(self):
        t = datetime(2017,7,7)
        doses = [
            DoseEntry(DoseEntryType.TempBasal, t+timedelta(minutes=00), t+timedelta(minutes=30), value = 1, unit = DoseUnit.UnitsPerHour),
            DoseEntry(DoseEntryType.Bolus, t+timedelta(minutes=15), value = 1, unit = DoseUnit.Units)
        ]

        values = interpolate_doses_to_timeline(doses)
        self.assertEqual(len(values), 6)

        expected = [
            InsulinValue(t+timedelta(minutes=05), 0.0833333),
            InsulinValue(t+timedelta(minutes=10), 0.0833333),
            InsulinValue(t+timedelta(minutes=15), 0.0833333),
            InsulinValue(t+timedelta(minutes=20), 1.0833333),
            InsulinValue(t+timedelta(minutes=25), 0.0833333),
            InsulinValue(t+timedelta(minutes=30), 0.0833333),
        ]

        for value, expected_value in zip(values, expected):
            self.assertEqual(value.start_date, expected_value.start_date)
            self.assertAlmostEqual(value.value, expected_value.value)

if __name__ == '__main__':
    unittest.main()
