import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from personal.v72 import fuel_components, import_sin_csv, monthly_factor

class V72Tests(unittest.TestCase):
    def test_co2_biogenic_separate(self):
        x = fuel_components('Gasolina comum (litros)', date(2026, 2, 1), 10)
        self.assertEqual(x['co2_fossil_kg'], Decimal('15.4840'))
        self.assertEqual(x['co2_biogenic_kg'], Decimal('4.5300'))
        self.assertEqual(x['co2e_combustion_kg'], x['co2_fossil_kg'] + x['nonco2_co2e_kg'])
    def test_b15(self):
        self.assertEqual(fuel_components('Diesel B (litros)', date(2026, 2, 1), 1)['biogenic_share'], Decimal('0.15'))
    def test_negative(self):
        with self.assertRaises(ValueError): fuel_components('Diesel B (litros)', date(2026, 1, 1), -1)
    def test_import_monthly(self):
        with tempfile.TemporaryDirectory() as t:
            csv = Path(t)/'f.csv'; dest = Path(t)/'catalog.json'
            csv.write_text('year,month,factor_tco2_mwh\n2026,1,0.04\n', encoding='utf8')
            import_sin_csv(csv, 'a'*64, 'official.xlsx', dest)
            self.assertEqual(monthly_factor(date(2026,1,1),dest)['factor'], '0.04')
            with self.assertRaises(ValueError): monthly_factor(date(2026,2,1),dest)
if __name__ == '__main__': unittest.main()
