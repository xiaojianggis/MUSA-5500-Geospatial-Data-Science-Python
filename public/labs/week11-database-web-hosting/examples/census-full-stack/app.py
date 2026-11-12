"""Local Census tract explorer: python -m uvicorn app:app --host 127.0.0.1 --port 8000."""
from contextlib import asynccontextmanager
import json
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import ROOT, VARIABLES, YEAR, connect, initialize, prepared_counties
from prepare_data import DataError, build, counties
from datasets import dataset, csv_text

CountyID = r'^\d{5}$'


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title='Census tract data explorer', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


@app.get('/', include_in_schema=False)
def home():
    return FileResponse(ROOT / 'static/index.html', headers={'Cache-Control':'no-store'})


@app.get('/api/health')
def health():
    with connect() as con:
        tract_count = con.execute('SELECT count(DISTINCT geoid) FROM county_tracts').fetchone()[0]
    return {'status': 'ok', 'year': YEAR, 'geography_level': 'census_tract',
            'prepared_tracts': tract_count, 'prepared_counties': len(prepared_counties())}


@app.get('/api/config')
def config():
    return {'year': YEAR, 'period': '2020–2024 ACS 5-year', 'variables': VARIABLES,
            'sources': {'estimates': 'U.S. Census ACS via Census Reporter', 'boundaries': 'Census TIGERweb ACS 2024'}}


@app.get('/api/counties')
def list_counties(state: str = Query('42', pattern=r'^\d{2}$')):
    try:
        return counties(state)
    except DataError as error:
        raise HTTPException(502, str(error)) from error


@app.get('/api/prepared-counties')
def saved_counties():
    return prepared_counties()


class PrepareRequest(BaseModel):
    model_config = {'extra': 'forbid'}
    county_id: str = Field(pattern=CountyID)


@app.post('/api/prepare')
def prepare(request: PrepareRequest):
    try:
        return build(request.county_id)
    except DataError as error:
        raise HTTPException(502, str(error)) from error


@app.get('/api/tracts')
def tracts(county_id: str = Query(..., pattern=CountyID),
           variable: Literal['population', 'income', 'poverty', 'home_value'] = 'income'):
    with connect() as con:
        county = con.execute('SELECT * FROM counties WHERE county_id=?', [county_id]).fetchone()
        if county is None:
            raise HTTPException(404, 'Prepare this county first using the Prepare census tract data button.')
        rows = con.execute('SELECT * FROM county_tracts WHERE county_id=? ORDER BY geoid', [county_id]).fetchall()
    features = []
    for row in rows:
        metrics = json.loads(row['metrics'])
        features.append({'type': 'Feature', 'geometry': json.loads(row['geometry']),
                         'properties': {'geoid': row['geoid'], 'name': row['name'],
                                        **metrics[variable], 'metrics': metrics}})
    return {'type': 'FeatureCollection', 'features': features, 'county_id': county_id, 'county_name': county['name'],
            'year': county['year'], 'prepared_at': county['prepared_at'], 'variable': variable,
            'variable_info': VARIABLES[variable],
            'source': json.loads(county['source']), 'geography_level': 'census_tract'}


@app.get('/api/dataset')
def download_dataset(county_id: str | None = Query(None, pattern=CountyID),
                     format: Literal['geojson','csv'] = 'geojson'):
    data = dataset(county_id)
    if not data['features']:
        raise HTTPException(404, 'Prepare tract data for this area first.')
    name = f"acs2024_{county_id.replace(':','-') if county_id else 'all'}_tracts.{format}"
    return Response(content=csv_text(data) if format == 'csv' else json.dumps(data, ensure_ascii=False, allow_nan=False),
                    media_type='text/csv' if format == 'csv' else 'application/geo+json',
                    headers={'Content-Disposition': f'attachment; filename="{name}"'})
