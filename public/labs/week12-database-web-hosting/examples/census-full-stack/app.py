"""Read-only Census GIS API and same-origin frontend. Run: uvicorn app:app."""
from contextlib import asynccontextmanager
from typing import Literal
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import ROOT, DB_PATH, LABELS, NOTICE, connect

Category = Literal['all', 'w', 'b', 'a', 'h', 'o']


@asynccontextmanager
async def lifespan(app):
    if not DB_PATH.is_file():
        raise RuntimeError('Database missing. Run python prepare_data.py --data PATH first.')
    with connect() as con:
        con.execute('SELECT count(*) FROM census_points').fetchone()
    yield


app = FastAPI(title='Census teaching GIS', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


@app.get('/', include_in_schema=False)
def home():
    return FileResponse(ROOT / 'static/index.html')


@app.get('/api/health')
def health():
    with connect() as con:
        count = con.execute('SELECT count(*) FROM census_points').fetchone()[0]
    return {'status': 'ok', 'sample_dots': count, 'notice': NOTICE}


@app.get('/api/districts')
def districts(category: Category = 'all'):
    # Only a bounded set of historical Pennsylvania polygons goes to the browser.
    with connect() as con:
        rows = con.execute('''WITH totals AS (
            SELECT a.district_id, count(*) AS n
            FROM point_district a JOIN census_points p USING(point_id)
            WHERE (? = 'all' OR p.category = ?) GROUP BY a.district_id
        ) SELECT d.district_id, coalesce(t.n,0),
            ST_AsGeoJSON(ST_Transform(d.geom,'EPSG:26918','EPSG:4326',always_xy := true))
            FROM districts d LEFT JOIN totals t USING(district_id) ORDER BY d.district_id''',
            [category, category]).fetchall()
    return {'type': 'FeatureCollection', 'notice': NOTICE, 'category': category,
            'features': [{'type': 'Feature', 'geometry': json.loads(geometry),
                          'properties': {'district_id': district, 'sample_dots': count}}
                         for district, count, geometry in rows]}


@app.get('/api/nearby')
def nearby(lon: float = Query(..., ge=-180, le=180),
           lat: float = Query(..., ge=-85, le=85),
           radius_m: int = Query(2000, ge=100, le=20000),
           category: Category = 'all'):
    # Values are bound parameters, never SQL text supplied by the browser.
    with connect() as con:
        inside = con.execute('''SELECT EXISTS(SELECT 1 FROM districts
            WHERE ST_Covers(geom,ST_Transform(ST_Point(?,?),
            'EPSG:4326','EPSG:26918',always_xy := true)))''', [lon, lat]).fetchone()[0]
        if not inside:
            raise HTTPException(400, 'Choose a location inside historical Pennsylvania district coverage.')
        rows = con.execute('''WITH location AS (
            SELECT ST_Transform(ST_Point(?,?),'EPSG:4326','EPSG:26918',always_xy := true) AS geom
        ) SELECT p.category,count(*) FROM census_points p,location q
        WHERE ST_DWithin(p.geom,q.geom,?) AND (? = 'all' OR p.category = ?)
        GROUP BY p.category ORDER BY p.category''', [lon, lat, radius_m, category, category]).fetchall()
    counts = dict(rows)
    return {'location': {'lon': lon, 'lat': lat}, 'radius_m': radius_m,
            'category': category, 'sample_dots': sum(counts.values()), 'notice': NOTICE,
            'categories': [{'category': code, 'label': label, 'sample_dots': counts.get(code, 0)}
                           for code, label in LABELS.items() if category in ('all', code)]}
