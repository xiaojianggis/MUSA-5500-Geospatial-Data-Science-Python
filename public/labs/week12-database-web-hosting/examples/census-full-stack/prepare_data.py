"""Build a separate demo database from the existing Week 11 files."""
import argparse
from pathlib import Path
from database import DB_PATH, connect


def build(data, destination=DB_PATH):
    data = Path(data).resolve()
    for name in ['census_sample.parquet', 'districts_2015.geojson']:
        if not (data / name).is_file():
            raise FileNotFoundError(f'Missing {data / name}; download both source files into week12/data and point --data there.')
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f'{destination} exists. Stop the API and remove only this demo database before rebuilding.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with connect(destination, read_only=False, install=True) as con:
            con.execute('BEGIN')
            con.execute('''CREATE TABLE districts AS
                SELECT STATEFP || CD114FP AS district_id,
                ST_Transform(geom, 'EPSG:4326', 'EPSG:26918', always_xy := true) AS geom
                FROM ST_Read(?) WHERE STATEFP = '42' ''', [str(data / 'districts_2015.geojson')])
            con.execute('''CREATE TABLE census_points AS
                WITH candidates AS (
                    SELECT easting AS x, northing AS y, race::VARCHAR AS category,
                    ST_Transform(ST_Point(easting, northing), 'EPSG:3857', 'EPSG:26918', always_xy := true) AS geom
                    FROM read_parquet(?)
                    WHERE easting BETWEEN -9000000 AND -8200000
                    AND northing BETWEEN 4750000 AND 5300000
                )
                SELECT row_number() OVER (ORDER BY p.x,p.y,p.category) AS point_id, category, geom
                FROM candidates p
                WHERE EXISTS (SELECT 1 FROM districts d WHERE ST_Covers(d.geom,p.geom))''',
                [str(data / 'census_sample.parquet')])
            con.execute('''CREATE TABLE point_district AS
                SELECT p.point_id, min(d.district_id) AS district_id
                FROM census_points p JOIN districts d ON ST_Covers(d.geom,p.geom)
                GROUP BY p.point_id''')
            count = con.execute('SELECT count(*) FROM census_points').fetchone()[0]
            assigned = con.execute('SELECT count(*) FROM point_district').fetchone()[0]
            assert count == assigned and count > 0
            con.execute('COMMIT')
            print(f'Built {destination}: {count:,} sample dots, each assigned once.')
    except Exception:
        # A failed first build must not leave a database that appears ready.
        destination.unlink(missing_ok=True)
        Path(str(destination) + '.wal').unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Local week12/data folder containing the downloaded Parquet and GeoJSON files')
    build(parser.parse_args().data)
