import unittest
from .carb_math import *


class CarbMathTestCase(unittest.TestCase):

    def test_interpolate_doses_to_timeline(self):
        t = datetime(2017,7,7,tzinfo=pytz.utc).astimezone(pytz.timezone('US/Central'))
        entries = [
            CarbEntry(t+timedelta(minutes=1), 20),
            CarbEntry(t+timedelta(minutes=15), 30),
            CarbEntry(t+timedelta(minutes=16), 10)
        ]

        values = interpolate_entries_to_timeline(entries)
        self.assertEqual(len(values), 4)

        expected = [
            CarbEntry(t+timedelta(minutes=5), 20),
            CarbEntry(t+timedelta(minutes=10), 0),
            CarbEntry(t+timedelta(minutes=15), 30),
            CarbEntry(t+timedelta(minutes=20), 10),
        ]

        for value, expected_value in zip(values, expected):
            self.assertEqual(value.start_date, expected_value.start_date)
            self.assertAlmostEqual(value.quantity, expected_value.quantity)
