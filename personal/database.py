"""V3/V4: SQLite persistence with immutable emission snapshots."""
import sqlite3
from pathlib import Path
from .calculator import calculate_emissions, to_decimal
from .factors import resolve_factor

DEFAULT_DB = Path(__file__).resolve().parent.parent / 'carbon_personal.sqlite3'


def connect(path=DEFAULT_DB):
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    return connection


def initialize(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_date TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity TEXT NOT NULL,
        unit TEXT NOT NULL,
        factor TEXT NOT NULL,
        factor_unit TEXT NOT NULL,
        factor_source TEXT NOT NULL,
        factor_year INTEGER,
        emissions_kg TEXT NOT NULL,
        notes TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )''')
    existing = {row[1] for row in connection.execute('PRAGMA table_info(activities)')}
    for column in ('factor_quality', 'factor_url', 'gas', 'co2_fossil_kg', 'ch4_kg', 'n2o_kg', 'nonco2_co2e_kg', 'co2_biogenic_kg', 'methodology'):
        if column not in existing:
            connection.execute(f'ALTER TABLE activities ADD COLUMN {column} TEXT')
    connection.commit()


def add_activity(connection, date, category, quantity, notes='', use_official=True):
    factor = resolve_factor(category, date, use_official=use_official)
    amount = to_decimal(quantity)
    emission = calculate_emissions(amount, factor['factor'])
    connection.execute('''INSERT INTO activities
        (activity_date, category, quantity, unit, factor, factor_unit, factor_source, factor_year, emissions_kg, notes, factor_quality, factor_url, gas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (date.isoformat(), category, str(amount), factor['unit'], factor['factor'],
         factor['factor_unit'], factor['source'], factor['year'], str(emission), notes,
         factor['quality'], factor['url'], factor['gas']))
    from .v72 import fuel_components
    if category in ('Regular gasoline (liters)', 'Premium gasoline (liters)', 'Diesel B (liters)'):
        components = fuel_components(category, date, amount)
        connection.execute('''UPDATE activities SET emissions_kg=?, gas=?, co2_fossil_kg=?, ch4_kg=?, n2o_kg=?, nonco2_co2e_kg=?, co2_biogenic_kg=?, methodology=? WHERE id=last_insert_rowid()''',
            (str(components['co2e_combustion_kg']), 'combustion CO2e',
             str(components['co2_fossil_kg']), str(components['ch4_kg']),
             str(components['n2o_kg']), str(components['nonco2_co2e_kg']),
             str(components['co2_biogenic_kg']), components['method']))
    connection.commit()


def list_activities(connection):
    return [dict(row) for row in connection.execute('SELECT * FROM activities ORDER BY activity_date DESC, id DESC')]


def delete_activity(connection, activity_id):
    connection.execute('DELETE FROM activities WHERE id=?', (activity_id,))
    connection.commit()
