"""Local Census tract explorer: python -m uvicorn app:app --host 127.0.0.1 --port 8000."""
from contextlib import asynccontextmanager
import json
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import ROOT, VARIABLES, YEAR, connect, initialize, prepared_towns
from prepare_data import DataError, build, places

TownID = r'^(22|28|30):(?:\d{7}|\d{10})$'


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title='Town Census tract explorer', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


@app.get('/', include_in_schema=False)
def home():
    return FileResponse(ROOT / 'static/index.html')


@app.get('/api/health')
def health():
    return {'status': 'ok', 'year': YEAR, 'prepared_towns': len(prepared_towns())}


@app.get('/api/config')
def config():
    return {'year': YEAR, 'period': '2020–2024 ACS 5-year', 'variables': VARIABLES,
            'sources': {'estimates': 'U.S. Census ACS via Census Reporter', 'boundaries': 'Census TIGERweb ACS 2024'}}


@app.get('/api/places')
def search_places(state: str = Query('42', pattern=r'^\d{2}$'), q: str = Query(..., min_length=2, max_length=80)):
    try:
        return [p for p in places(state) if q.casefold() in p['name'].casefold()][:100]
    except DataError as error:
        raise HTTPException(502, str(error)) from error


@app.get('/api/towns')
def towns():
    return prepared_towns()


class PrepareRequest(BaseModel):
    town_id: str = Field(pattern=TownID)


@app.post('/api/prepare')
def prepare(request: PrepareRequest):
    try:
        return build(request.town_id)
    except DataError as error:
        raise HTTPException(502, str(error)) from error


@app.get('/api/tracts')
def tracts(town_id: str = Query(..., pattern=TownID),
           variable: Literal['population', 'income', 'poverty', 'home_value'] = 'income'):
    with connect() as con:
        town = con.execute('SELECT * FROM towns WHERE town_id=?', [town_id]).fetchone()
        if town is None:
            raise HTTPException(404, 'Prepare this town first using the Prepare town data button.')
        rows = con.execute('SELECT * FROM tracts WHERE town_id=? ORDER BY geoid', [town_id]).fetchall()
    features = []
    for row in rows:
        metrics = json.loads(row['metrics'])
        features.append({'type': 'Feature', 'geometry': json.loads(row['geometry']),
                         'properties': {'geoid': row['geoid'], 'name': row['name'],
                                        **metrics[variable], 'metrics': metrics}})
    return {'type': 'FeatureCollection', 'features': features, 'town_id': town_id, 'town_name': town['name'],
            'year': town['year'], 'prepared_at': town['prepared_at'], 'variable': variable,
            'variable_info': VARIABLES[variable], 'boundary': json.loads(town['boundary']),
            'source': json.loads(town['source'])}
