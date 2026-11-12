"""Prepare ACS tract estimates and county-based selections; usable from CLI or API."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from threading import Lock

import httpx
from shapely.geometry import mapping, shape
from shapely.validation import make_valid

from database import DATA_DIR, VARIABLES, YEAR, initialize, save_county
from datasets import export_datasets, write_atomic

TIGER = f'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS{YEAR}/MapServer'
ACS = f'https://api.censusreporter.org/1.0/data/show/acs{YEAR}_5yr'
PREPARE_LOCK = Lock()


class DataError(ValueError):
    pass


def get_json(url, params):
    """Cache only successful public responses. No credentials are used or saved."""
    key = hashlib.sha256((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    target = DATA_DIR / 'source-cache' / f'{key}.json'
    if target.is_file():
        return json.loads(target.read_text())
    try:
        response = httpx.get(url, params=params, timeout=120, follow_redirects=True)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise DataError('Public data download failed. Check internet access and try again; already prepared counties remain available.') from error
    if isinstance(result, dict) and result.get('error'):
        raise DataError('The public data service rejected the query. Try a smaller county or retry later.')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Atomic cache writes avoid partial files if interrupted or read concurrently.
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as handle:
        json.dump(result, handle)
        temporary = Path(handle.name)
    temporary.replace(target)
    return result


def tiger_features(layer, where, *, geometry=True, envelope=None):
    """Paginate explicitly rather than silently truncating larger selections."""
    features, offset = [], 0
    while True:
        params = {'where': where, 'outFields': 'GEOID,NAME,STATE', 'returnGeometry': str(geometry).lower(),
                  'outSR': '4326', 'f': 'geojson', 'orderByFields': 'GEOID',
                  'resultOffset': offset, 'resultRecordCount': 500}
        if envelope:
            params.update(geometry=','.join(map(str, envelope)), geometryType='esriGeometryEnvelope',
                          inSR='4326', spatialRel='esriSpatialRelIntersects')
        result = get_json(f'{TIGER}/{layer}/query', params)
        if result.get('type') != 'FeatureCollection':
            raise DataError('TIGERweb did not return the expected boundary features.')
        page = result['features']
        features.extend(page)
        if len(page) < 500:
            break
        offset += len(page)
    return features


def counties(state):
    if not re.fullmatch(r'\d{2}', state):
        raise DataError('State must be a two-digit FIPS code, such as 42 for Pennsylvania.')
    output = []
    for f in tiger_features(82, f"STATE='{state}'", geometry=False):
        p = f['properties']
        output.append({'county_id': p['GEOID'], 'name': p['NAME'],
                       'state_fips': p['GEOID'][:2], 'county_fips': p['GEOID'][2:]})
    output.sort(key=lambda c: c['name'])
    write_atomic(DATA_DIR.parent / 'county-lists' / f'{state}.json', json.dumps(output, ensure_ascii=False, indent=2))
    return output


def clean_number(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    # Census special negative codes and nulls mean unavailable, never zero.
    return value if math.isfinite(value) and value >= 0 else None


def metrics_for(tables):
    result = {}
    for key, spec in VARIABLES.items():
        table = tables.get(spec['table'], {})
        estimate, error = table.get('estimate', {}), table.get('error', {})
        value = clean_number(estimate.get(spec['column']))
        moe = clean_number(error.get(spec['column'])) if spec['moe'] else None
        item = {'value': value, 'moe': moe, 'topcoded': False}
        if key == 'poverty':
            denominator = clean_number(estimate.get('B17001001'))
            item.update(numerator=value, denominator=denominator,
                        numerator_moe=clean_number(error.get('B17001002')),
                        denominator_moe=clean_number(error.get('B17001001')))
            item['value'] = 100 * value / denominator if value is not None and denominator and value <= denominator else None
        elif key == 'income' and value == 250001:
            item.update(value=250000, topcoded=True)
        elif key == 'home_value' and value == 2000001:
            item.update(value=2000000, topcoded=True)
        result[key] = item
    return result


def build(county_id):
    if not re.fullmatch(r'\d{5}', county_id):
        raise DataError('Choose a valid five-digit county FIPS code from the county list.')
    with PREPARE_LOCK:
        matches = [c for c in counties(county_id[:2]) if c['county_id'] == county_id]
        if len(matches) != 1:
            raise DataError('County not found in the 2024 Census geography.')
        county_name = matches[0]['name']
        # Census tracts nest in counties. Match their geographic codes, not polygon overlap.
        candidates = tiger_features(8, f"STATE='{county_id[:2]}' AND COUNTY='{county_id[2:]}'")
        if not candidates:
            raise DataError('No Census tracts found for this county.')
        if any(not f['properties']['GEOID'].startswith(county_id) for f in candidates):
            raise DataError('Boundary response includes a tract from another county; no data were saved.')
        tracts = list({f['properties']['GEOID']: f for f in candidates}.values())
        estimates, release = {}, None
        for start in range(0, len(tracts), 50):
            ids = ['14000US' + f['properties']['GEOID'] for f in tracts[start:start+50]]
            data = get_json(ACS, {'table_ids': 'B01003,B19013,B17001,B25077', 'geo_ids': ','.join(ids)})
            release = data.get('release', {})
            if release.get('id') != f'acs{YEAR}_5yr':
                raise DataError('ACS release mismatch. No data were saved.')
            estimates.update(data.get('data', {}))
        output = []
        for f in tracts:
            tract_id = f['properties']['GEOID']
            tables = estimates.get('14000US' + tract_id)
            if tables is None:
                raise DataError(f'ACS response is missing tract {tract_id}; no incomplete county was saved.')
            output.append({'geoid': tract_id, 'name': f['properties']['NAME'],
                           'geometry': mapping(make_valid(shape(f['geometry'])).simplify(0.0001, preserve_topology=True)),
                           'metrics': metrics_for(tables)})
        stamp = datetime.now(timezone.utc).isoformat()
        county = {'county_id': county_id, 'name': county_name, 'prepared_at': stamp,
                  'source': {'estimates': ACS, 'boundaries': TIGER, 'release': release,
                             'selection': f'All Census tracts assigned to county FIPS {county_id}; no spatial overlap selection.'}}
        initialize()
        save_county(county, output)
        package = DATA_DIR / 'counties' / county_id
        package.mkdir(parents=True, exist_ok=True)
        write_atomic(package / 'prepared.json', json.dumps({'county': county, 'tracts': output}, indent=2))
        export_datasets(DATA_DIR.parent / 'census-tracts', county_id)
        return {'county_id': county_id, 'name': county_name, 'tract_count': len(output), 'year': YEAR, 'prepared_at': stamp,
                'geography_level': 'census_tract', 'dataset_folder': str(DATA_DIR.parent / 'census-tracts')}



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', default='42', help='State FIPS for --list-counties, e.g. 42')
    parser.add_argument('--list-counties', action='store_true', help='List all counties/county equivalents in --state')
    parser.add_argument('--export', action='store_true', help='Export prepared county tract datasets')
    parser.add_argument('--county', help='Five-digit county FIPS, e.g. 42043 for Dauphin County, PA')
    args = parser.parse_args()
    if args.list_counties:
        print(json.dumps(counties(args.state), indent=2))
    elif args.export:
        initialize()
        print(f'Exported {export_datasets(DATA_DIR.parent / "census-tracts")} unique Census tracts.')
    elif args.county:
        print(json.dumps(build(args.county), indent=2))
    else:
        parser.error('Use --list-counties, --export, or --county FIPS. County selection replaces the town workflow.')
