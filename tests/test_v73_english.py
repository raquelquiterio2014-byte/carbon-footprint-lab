"""English-language release and backward-compatibility checks."""
import unittest
from datetime import date
from personal.factors import FACTORS, normalize_category, resolve_factor
from personal.database import connect, initialize, list_activities


class EnglishReleaseTests(unittest.TestCase):
    def test_english_categories(self):
        self.assertIn('Electricity', FACTORS)
        self.assertIn('Regular gasoline (liters)', FACTORS)
        self.assertEqual(normalize_category('Eletricidade'), 'Electricity')
        self.assertEqual(normalize_category('Gasolina comum (litros)'), 'Regular gasoline (liters)')

    def test_documented_fuel_unchanged(self):
        self.assertEqual(resolve_factor('Regular gasoline (liters)', date(2026, 2, 1))['factor'], '1.54840')

    def test_legacy_database_category_display(self):
        connection = connect(':memory:')
        initialize(connection)
        connection.execute('''INSERT INTO activities (activity_date,category,quantity,unit,factor,factor_unit,factor_source,emissions_kg,notes)
            VALUES ('2023-01-01','Eletricidade','100','kWh','0.1','kg CO2e/kWh','EXEMPLO DIDÁTICO','10','')''')
        self.assertEqual(normalize_category(list_activities(connection)[0]['category']), 'Electricity')
        connection.close()


if __name__ == '__main__':
    unittest.main()
