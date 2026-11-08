import unittest
from datetime import date
from decimal import Decimal
from personal.factors import resolve_factor

class BrasilTests(unittest.TestCase):
    def test_electricity_2025(self):
        self.assertEqual(resolve_factor('Eletricidade', date(2025, 5, 1))['factor'], '0.0461')
    def test_electricity_2026_blocked(self):
        with self.assertRaises(ValueError): resolve_factor('Eletricidade', date(2026, 5, 1))
    def test_gasoline_transition(self):
        a = resolve_factor('Gasolina comum (litros)', date(2025, 7, 31))
        b = resolve_factor('Gasolina comum (litros)', date(2025, 8, 1))
        self.assertEqual(Decimal(a['factor']), Decimal('1.61476'))
        self.assertEqual(Decimal(b['factor']), Decimal('1.54840'))
    def test_diesel_transition(self):
        a = resolve_factor('Diesel B (litros)', date(2025, 7, 31))
        b = resolve_factor('Diesel B (litros)', date(2026, 1, 1))
        self.assertEqual(Decimal(a['factor']), Decimal('2.23858'))
        self.assertEqual(Decimal(b['factor']), Decimal('2.21255'))
    def test_premium(self):
        self.assertEqual(Decimal(resolve_factor('Gasolina premium (litros)', date(2026, 1, 1))['factor']), Decimal('1.65900'))
