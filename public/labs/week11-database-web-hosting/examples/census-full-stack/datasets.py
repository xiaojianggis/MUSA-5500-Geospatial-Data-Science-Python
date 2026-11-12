"""Portable Census tract datasets: one feature/row per 11-digit tract GEOID."""
import csv
import io
import json
from pathlib import Path
import tempfile

from database import VARIABLES, YEAR, connect


def dataset(county_id=None):
    # Counties select an area; Census estimates and map geometry are always tract-level.
    query = '''SELECT r.*, t.name AS county_name FROM county_tracts r JOIN counties t USING(county_id)'''
    with connect() as con:
        rows = con.execute(query + (' WHERE r.county_id=?' if county_id else '') + ' ORDER BY r.geoid,r.county_id',
                           [county_id] if county_id else []).fetchall()
    by_geoid = {}
    for row in rows:
        geoid = row['geoid']
        if geoid not in by_geoid:
            metrics = json.loads(row['metrics'])
            properties = {'geoid': geoid, 'tract_name': row['name'], 'state_fips': geoid[:2],
                          'county_fips': geoid[2:5], 'tract_code': geoid[5:], 'acs_year': YEAR,
                          'county_name': row['county_name'], 'county_geoid': row['county_id']}
            for key in VARIABLES:
                properties[key] = metrics[key]['value']
                properties[key + '_moe'] = metrics[key]['moe']
                properties[key + '_topcoded'] = metrics[key]['topcoded']
            for field in ['numerator','denominator','numerator_moe','denominator_moe']:
                properties['poverty_' + field] = metrics['poverty'].get(field)
            by_geoid[geoid] = {'type': 'Feature', 'geometry': json.loads(row['geometry']), 'properties': properties}
    return {'type': 'FeatureCollection', 'geography_level': 'census_tract', 'acs_period': '2020–2024',
            'sources': {'estimates': 'https://api.censusreporter.org/1.0/data/show/acs2024_5yr',
                        'boundaries': 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer'},
            'note': 'Whole census tracts belonging to selected counties by FIPS; no county-level aggregates.',
            'features': list(by_geoid.values())}


def csv_text(data):
    output = io.StringIO(newline='')
    rows = [f['properties'] for f in data['features']]
    # Export remains readable even when no areas have been prepared.
    fields = list(rows[0]) if rows else ['geoid','tract_name','state_fips','county_fips','tract_code','acs_year',*VARIABLES]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: '; '.join(value) if isinstance(value,list) else value for key,value in row.items()})
    return output.getvalue()


def write_atomic(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def export_datasets(folder, county_id=None):
    """Write the combined unique-tract dataset and optionally a selected county's tracts."""
    folder = Path(folder)
    data = dataset()
    write_atomic(folder / 'acs2024_tracts.geojson', json.dumps(data, ensure_ascii=False, allow_nan=False))
    write_atomic(folder / 'acs2024_tracts.csv', csv_text(data))
    if county_id:
        area = dataset(county_id)
        stem = county_id.replace(':','-')
        write_atomic(folder / 'counties' / f'{stem}_tracts.geojson', json.dumps(area, ensure_ascii=False, allow_nan=False))
        write_atomic(folder / 'counties' / f'{stem}_tracts.csv', csv_text(area))
    write_atomic(folder / 'README.txt', '''Census tract-level dataset — ACS 2020–2024

acs2024_tracts.geojson: one polygon feature per unique 11-digit tract GEOID, EPSG:4326.
acs2024_tracts.csv: same tract attributes, one row per GEOID, without geometry.
counties/: tract-only subsets for prepared counties. No county polygon features or county totals.
Coverage: only the counties prepared locally; this is not a nationwide tract dataset.

Variables: population (B01003), income (B19013, 2024 dollars), poverty (B17001,
percent below poverty among people with poverty status determined), home_value
(B25077, median owner-occupied value in 2024 dollars). Direct-estimate _moe fields
are 90% margins of error. Poverty rate MOE is not calculated; its numerator,
denominator, and their MOEs are included. Missing estimates are null/blank, not zero.
_topcoded=true means income $250,000+ or home value $2,000,000+.
county_name and county_geoid identify the parent county. Each row is a census
tract observation. No county-level aggregates are included.
Open CSV GEOID and FIPS columns as text to preserve leading zeros.

Tracts are selected by their parent county FIPS, never by town overlap. Population
is a count, not density. Medians cannot be summed. Geometries are slightly simplified.
Sources: U.S. Census ACS via https://api.censusreporter.org/ and matching Census
TIGERweb ACS 2024 boundaries. Source URLs also appear in the GeoJSON metadata.
''')
    return len(data['features'])
