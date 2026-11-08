import unittest
from datetime import date
from personal.factors import resolve_factor
from personal.database import connect, initialize, add_activity, list_activities

class V7Tests(unittest.TestCase):
    def test_sin_2023(self):
        self.assertEqual(resolve_factor('Electricity', date(2023, 6, 1))['factor'], '0.0385')
    def test_sin_2024(self):
        self.assertEqual(resolve_factor('Electricity', date(2024, 6, 1))['factor'], '0.058')
    def test_unsupported_year_rejected(self):
        with self.assertRaises(ValueError):
            resolve_factor('Electricity', date(2026, 1, 1))
    def test_snapshot_and_migration(self):
        db = connect(':memory:')
        initialize(db)
        add_activity(db, date(2023, 6, 1), 'Electricity', '100')
        record = list_activities(db)[0]
        self.assertEqual(record['emissions_kg'], '3.8500')
        self.assertEqual(record['factor_quality'], 'official')
        self.assertEqual(record['gas'], 'CO2')
        db.close()

if __name__ == '__main__':
    unittest.main()
