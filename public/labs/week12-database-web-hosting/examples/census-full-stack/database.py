"""Shared connection setup; CRS of all stored geometry is EPSG:26918."""
from pathlib import Path
import os
import duckdb

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('CENSUS_DB', ROOT / 'data/census.duckdb')).resolve()
LABELS = {'w': 'White', 'b': 'Black', 'a': 'Asian', 'h': 'Hispanic', 'o': 'Other'}
NOTICE = 'Synthetic 2010 Census teaching dots and 2015 districts; sample counts are not population estimates or current demographics.'


def connect(path=DB_PATH, *, read_only=True, install=False):
    config = {}
    if os.environ.get('DUCKDB_EXTENSION_DIRECTORY'):
        config['extension_directory'] = os.environ['DUCKDB_EXTENSION_DIRECTORY']
    con = duckdb.connect(str(path), read_only=read_only, config=config)
    try:
        if install:
            con.execute('INSTALL spatial')
        con.execute('LOAD spatial')
    except Exception:
        con.close()
        raise
    return con
