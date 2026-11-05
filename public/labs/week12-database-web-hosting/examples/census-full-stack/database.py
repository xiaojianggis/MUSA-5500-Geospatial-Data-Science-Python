"""Local prepared-town store. Original lecture 12A/district databases stay untouched."""
from contextlib import contextmanager
from pathlib import Path
import json
import os
import sqlite3

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('CENSUS_DB', ROOT / 'data/tracts.sqlite')).resolve()
# Repository layout uses the existing source folder beside lecture-12C.ipynb.
DEFAULT_DATA = ROOT.parent.parent / 'data' if ROOT.parent.name == 'examples' else ROOT.parent / 'data'
DATA_DIR = Path(os.environ.get('CENSUS_DATA_DIR', DEFAULT_DATA / 'tract-explorer')).resolve()
YEAR = 2024
VARIABLES = {
    'population': {'label': 'Total population', 'unit': 'people', 'table': 'B01003', 'column': 'B01003001', 'moe': True},
    'income': {'label': 'Median household income', 'unit': '2024 dollars', 'table': 'B19013', 'column': 'B19013001', 'moe': True},
    'poverty': {'label': 'Poverty rate', 'unit': 'percent', 'table': 'B17001', 'column': 'B17001002', 'moe': False},
    'home_value': {'label': 'Median owner-occupied home value', 'unit': '2024 dollars', 'table': 'B25077', 'column': 'B25077001', 'moe': True},
}


@contextmanager
def connect(path=None):
    con = sqlite3.connect(path or DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS towns (
            town_id TEXT PRIMARY KEY, name TEXT NOT NULL, year INTEGER NOT NULL,
            prepared_at TEXT NOT NULL, boundary TEXT NOT NULL, source TEXT NOT NULL)''')
        con.execute('''CREATE TABLE IF NOT EXISTS tracts (
            town_id TEXT NOT NULL, geoid TEXT NOT NULL, name TEXT NOT NULL,
            geometry TEXT NOT NULL, metrics TEXT NOT NULL,
            PRIMARY KEY (town_id, geoid))''')


def prepared_towns():
    with connect() as con:
        return [dict(row) for row in con.execute('''SELECT t.town_id, t.name, t.year, t.prepared_at,
            count(r.geoid) AS tract_count FROM towns t LEFT JOIN tracts r USING(town_id)
            GROUP BY t.town_id ORDER BY t.name''')]


def save_town(town, features):
    # Replace one town atomically; other prepared towns remain available.
    with connect() as con:
        con.execute('DELETE FROM tracts WHERE town_id=?', [town['town_id']])
        con.execute('''INSERT OR REPLACE INTO towns VALUES (?, ?, ?, ?, ?, ?)''',
                    [town['town_id'], town['name'], YEAR, town['prepared_at'],
                     json.dumps(town['boundary']), json.dumps(town['source'])])
        con.executemany('INSERT INTO tracts VALUES (?, ?, ?, ?, ?)', [
            (town['town_id'], f['geoid'], f['name'], json.dumps(f['geometry']), json.dumps(f['metrics']))
            for f in features])
