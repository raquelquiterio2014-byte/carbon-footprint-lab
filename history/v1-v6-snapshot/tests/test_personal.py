import unittest
from datetime import date
from decimal import Decimal
from personal.calculator import calculate_emissions
from personal.database import connect, initialize, add_activity, list_activities, delete_activity


class TestPersonal(unittest.TestCase):
    def test_calculation(self):
        self.assertEqual(calculate_emissions('150', '0.10'), Decimal('15.00'))
        self.assertEqual(calculate_emissions(0, '0.10'), 0)

    def test_invalid_values(self):
        for value in [-1, 'NaN', 'Infinity', 'abc']:
            with self.assertRaises(ValueError):
                calculate_emissions(value, '0.1')

    def test_database(self):
        conn = connect(':memory:')
        initialize(conn)
        add_activity(conn, date(2026, 11, 8), 'Eletricidade', '150')
        rows = list_activities(conn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(Decimal(rows[0]['emissions_kg']), Decimal('15.00'))
        self.assertEqual(rows[0]['factor_source'], 'EXEMPLO DIDÁTICO')
        delete_activity(conn, rows[0]['id'])
        self.assertEqual(len(list_activities(conn)), 0)
        conn.close()


if __name__ == '__main__':
    unittest.main()
