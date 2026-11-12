"""Local prepared-county store. Original lecture 12A/district databases stay untouched."""
from contextlib import contextmanager
from pathlib import Path
import json
import os
import sqlite3

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('CENSUS_DB', ROOT / 'data/tracts.sqlite')).resolve()
# Repository layout uses the existing source folder beside lecture-11C.ipynb.
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
        # New county tables keep earlier town datasets intact but out of county results.
        con.execute('''CREATE TABLE IF NOT EXISTS counties (
            county_id TEXT PRIMARY KEY, name TEXT NOT NULL, year INTEGER NOT NULL,
            prepared_at TEXT NOT NULL, source TEXT NOT NULL)''')
        con.execute('''CREATE TABLE IF NOT EXISTS county_tracts (
            county_id TEXT NOT NULL, geoid TEXT NOT NULL, name TEXT NOT NULL,
            geometry TEXT NOT NULL, metrics TEXT NOT NULL,
            PRIMARY KEY (county_id, geoid))''')


def prepared_counties():
    with connect() as con:
        return [dict(row) for row in con.execute('''SELECT c.county_id, c.name, c.year, c.prepared_at,
            substr(c.county_id,1,2) AS state_fips, count(r.geoid) AS tract_count
            FROM counties c LEFT JOIN county_tracts r USING(county_id)
            GROUP BY c.county_id ORDER BY c.name,c.county_id''')]


def save_county(county, features):
    with connect() as con:
        con.execute('DELETE FROM county_tracts WHERE county_id=?', [county['county_id']])
        con.execute('INSERT OR REPLACE INTO counties VALUES (?, ?, ?, ?, ?)',
                    [county['county_id'], county['name'], YEAR, county['prepared_at'], json.dumps(county['source'])])
        con.executemany('INSERT INTO county_tracts VALUES (?, ?, ?, ?, ?)', [
            (county['county_id'], f['geoid'], f['name'], json.dumps(f['geometry']), json.dumps(f['metrics']))
            for f in features])
