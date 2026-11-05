"""Prepare ACS tract estimates and matching town boundaries; usable from CLI or API."""
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

from database import DATA_DIR, VARIABLES, YEAR, initialize, save_town

TIGER = f'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS{YEAR}/MapServer'
ACS = f'https://api.censusreporter.org/1.0/data/show/acs{YEAR}_5yr'
KINDS = {28: 'Incorporated place', 30: 'Census-designated place', 22: 'County subdivision / township'}
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
        raise DataError('Public data download failed. Check internet access and try again; already prepared towns remain available.') from error
    if isinstance(result, dict) and result.get('error'):
        raise DataError('The public data service rejected the query. Try a smaller town or retry later.')
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


def places(state):
    if not re.fullmatch(r'\d{2}', state):
        raise DataError('State must be a two-digit FIPS code, such as 42 for Pennsylvania.')
    output = []
    for layer, kind in KINDS.items():
        for f in tiger_features(layer, f"STATE='{state}'", geometry=False):
            p = f['properties']
            output.append({'town_id': f"{layer}:{p['GEOID']}", 'name': p['NAME'], 'kind': kind, 'state': state})
    return sorted(output, key=lambda p: (p['name'], p['kind']))


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


def build(town_id):
    match = re.fullmatch(r'(22|28|30):(\d{7}|\d{10})', town_id)
    if not match or len(match[2]) != (10 if match[1] == '22' else 7):
        raise DataError('Choose a valid town ID from the town search results.')
    layer, geoid = int(match[1]), match[2]
    with PREPARE_LOCK:
        boundaries = tiger_features(layer, f"GEOID='{geoid}'")
        if len(boundaries) != 1:
            raise DataError('Town boundary not found in the 2024 Census geography.')
        boundary = boundaries[0]
        town_shape = make_valid(shape(boundary['geometry']))
        if town_shape.is_empty:
            raise DataError('Town has no usable boundary geometry.')
        # Tract/place boundaries do not nest; select positive-area overlap, not touching neighbors.
        candidates = tiger_features(8, f"STATE='{geoid[:2]}'", envelope=town_shape.bounds)
        tracts = [f for f in candidates if make_valid(shape(f['geometry'])).intersection(town_shape).area > 1e-10]
        if not tracts:
            raise DataError('No overlapping Census tracts found for this town.')
        tracts = list({f['properties']['GEOID']: f for f in tracts}.values())
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
                raise DataError(f'ACS response is missing tract {tract_id}; no incomplete town was saved.')
            output.append({'geoid': tract_id, 'name': f['properties']['NAME'],
                           'geometry': mapping(make_valid(shape(f['geometry'])).simplify(0.0001, preserve_topology=True)),
                           'metrics': metrics_for(tables)})
        stamp = datetime.now(timezone.utc).isoformat()
        town = {'town_id': town_id, 'name': boundary['properties']['NAME'], 'prepared_at': stamp,
                'boundary': {**boundary, 'geometry': mapping(town_shape.simplify(0.0001, preserve_topology=True))},
                'source': {'estimates': ACS, 'boundaries': TIGER, 'release': release,
                           'selection': 'Whole tracts with positive-area overlap with the town boundary; no areal apportionment.'}}
        initialize()
        save_town(town, output)
        # Human-readable prepared package beside the notebook's existing data.
        package = DATA_DIR / 'towns' / town_id.replace(':', '-')
        package.mkdir(parents=True, exist_ok=True)
        (package / 'prepared.json').write_text(json.dumps({'town': town, 'tracts': output}, indent=2))
        return {'town_id': town_id, 'name': town['name'], 'tract_count': len(output), 'year': YEAR, 'prepared_at': stamp}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', default='42', help='State FIPS for --search, e.g. 42')
    parser.add_argument('--search', help='Find a town name; returns IDs to prepare')
    parser.add_argument('--town', help='ID from search, e.g. 28:4232800 for Harrisburg')
    args = parser.parse_args()
    if args.search:
        print(json.dumps([p for p in places(args.state) if args.search.casefold() in p['name'].casefold()], indent=2))
    elif args.town:
        print(json.dumps(build(args.town), indent=2))
    else:
        parser.error('Use --search NAME or --town ID. The old synthetic-dot --data workflow has been replaced.')
