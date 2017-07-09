import unittest
from insulin_math import *
from dose_entry import *
from datetime import datetime, timedelta

class InsulinMathTestCase(unittest.TestCase):
#    def setUp(self):

#    def tearDown(self):

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
        start = datetime.now() - timedelta(days=1)
        temp_basal = DoseEntry(DoseEntryType.TempBasal, start, start+timedelta(minutes=30), value = 3, unit = DoseUnit.UnitsPerHour)
        suspend = DoseEntry(DoseEntryType.Suspend, start+timedelta(minutes=10))
        resume = DoseEntry(DoseEntryType.Resume, start+timedelta(minutes=20))
        doses = [temp_basal, suspend, resume]
        reconciled_doses = reconcile_doses(doses)
        print([d.dose_entry_type for d in reconciled_doses])
        self.assertEqual(len(reconciled_doses), 3)
        self.assertEqual(reconciled_doses[0].dose_entry_type, DoseEntryType.TempBasal)
        self.assertEqual(reconciled_doses[0].end_date, start+timedelta(minutes=10))
        self.assertEqual(reconciled_doses[2].start_date, start+timedelta(minutes=20))
        self.assertEqual(reconciled_doses[2].end_date, start+timedelta(minutes=30))

if __name__ == '__main__':
    unittest.main()
