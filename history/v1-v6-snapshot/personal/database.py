"""V3/V4: SQLite persistence with immutable emission snapshots."""
import sqlite3
from pathlib import Path
from .calculator import calculate_emissions, to_decimal
from .factors import FACTORS

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
    connection.commit()


def add_activity(connection, date, category, quantity, notes=''):
    if category not in FACTORS:
        raise ValueError('Categoria desconhecida')
    factor = FACTORS[category]
    amount = to_decimal(quantity)
    emission = calculate_emissions(amount, factor['factor'])
    connection.execute('''INSERT INTO activities
        (activity_date, category, quantity, unit, factor, factor_unit, factor_source, factor_year, emissions_kg, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (date.isoformat(), category, str(amount), factor['unit'], factor['factor'],
         factor['factor_unit'], factor['source'], factor['year'], str(emission), notes))
    connection.commit()


def list_activities(connection):
    return [dict(row) for row in connection.execute('SELECT * FROM activities ORDER BY activity_date DESC, id DESC')]


def delete_activity(connection, activity_id):
    connection.execute('DELETE FROM activities WHERE id=?', (activity_id,))
    connection.commit()
