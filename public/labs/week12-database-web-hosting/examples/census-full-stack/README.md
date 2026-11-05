# Town Census tract explorer — lecture 12C

Prepare real ACS data for towns in different states, then compare census tracts using a Leaflet choropleth. Python/FastAPI serves both frontend and API; SQLite stores prepared towns. This replaces the historical district and synthetic-dot radius demo.

## Run locally

From the folder containing `lecture-12C.ipynb`:

```bash
conda activate geospatial
conda install -c conda-forge fastapi uvicorn httpx shapely
cd examples/census-full-stack
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

For the standalone ZIP, extract `census-full-stack` beside the notebook and use `cd census-full-stack` instead. Keep the terminal running. Open **http://127.0.0.1:8000/**, not the HTML file directly. API docs: **http://127.0.0.1:8000/docs**. Stop with Ctrl+C. After code changes, restart Uvicorn and hard-refresh the browser.

No map or Census API key is needed. Initial preparation downloads public data. Leaflet and OpenStreetMap tiles need internet access; already prepared estimates are stored locally.

## Prepare and explore towns

1. Choose Pennsylvania and search **Harrisburg**.
2. Select **Harrisburg city — Incorporated place (`28:4232800`)** and click **Prepare town data**.
3. Wait for downloads and the tract choropleth. The purple dashed line outlines the town.
4. Choose population, median household income, poverty rate, or median owner-occupied home value.
5. Search **Pittsburgh**, select **Pittsburgh city — Incorporated place (`28:4261000`)**, and prepare it.
6. Switch between prepared towns. Click a tract or its table row for details and an orange selected boundary.
7. Choose another state and town. Search covers incorporated places, CDPs, and county subdivisions/townships. Check the geography type; names may repeat.

The app starts with an empty prepared-town list in a fresh installation. No manual build is required before starting Uvicorn. Previously prepared towns reappear after restart. Repreparing replaces one town and reuses cached source responses.

## Data and interpretation

- **Estimates:** U.S. Census **2020–2024 ACS five-year**, delivered through the public [Census Reporter API](https://github.com/censusreporter/census-api/blob/master/API.md). The direct Census API may require a key; the mirror keeps this lesson key-free.
- **Boundaries:** matching [Census TIGERweb ACS 2024](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer), not current boundaries or the old district data.
- **Measures:** B01003 total population; B19013 median household income; B17001 below-poverty count / poverty-status universe × 100; B25077 median owner-occupied home value. Dollars are 2024 dollars.
- **Selection:** whole tracts with positive-area overlap with the town. Tracts are not clipped or apportioned to the town. Touching-only neighbors are excluded. Display geometry is slightly simplified after selection.
- **Uncertainty:** available 90% margins of error accompany direct estimates. Poverty displays its numerator/denominator; the rate MOE is not calculated. Null/suppressed estimates are gray, distinct from true zero. Upper-coded medians show `+`.
- **Comparisons:** class breaks stay fixed per variable across towns. Population is a count, not density. Whole-tract estimates include areas outside the town; do not call their sum a town total. Medians cannot be summed.

## Files and storage

In the repository layout:

```text
lecture folder/
├── data/tract-explorer/
│   ├── source-cache/                  # original public JSON responses
│   └── towns/28-4232800/prepared.json  # joined estimates, boundary, provenance
└── examples/census-full-stack/
    ├── app.py
    ├── database.py
    ├── prepare_data.py
    ├── test_app.py
    ├── static/
    └── data/tracts.sqlite              # database created on first server start
```

The standalone ZIP puts `census-full-stack` beside the shared data folder. Layout detection sets the same sibling source-data destination automatically. The old `census_sample.parquet`, `districts_2015.geojson`, and DuckDB files are unused and remain unchanged.

`CENSUS_DB` overrides the SQLite path; `CENSUS_DATA_DIR` overrides the source-cache/package folder. Use the same settings for the API and CLI. Do not point the SQLite app at an old DuckDB file.

## Optional command-line preparation

Run in the app directory:

```bash
python prepare_data.py --state 42 --search Harrisburg
python prepare_data.py --town 28:4232800
python prepare_data.py --town 28:4261000
```

Search returns IDs; use those IDs rather than guessing. The former `--data` CLI has been replaced. Refresh the app after CLI preparation. To refresh remote responses for this fixed vintage, stop the server, remove only the sibling `data/tract-explorer/source-cache` folder, restart, and reprepare the town.

## API

| Route | Purpose |
| --- | --- |
| `GET /api/health` | Status, vintage, prepared-town count |
| `GET /api/config` | Variable descriptions and sources |
| `GET /api/places?state=42&q=Harrisburg` | Search town IDs and geography types |
| `POST /api/prepare` | Body `{"town_id":"28:4232800"}`; download and save one town |
| `GET /api/towns` | List prepared towns |
| `GET /api/tracts?town_id=28:4232800&variable=income` | Choropleth GeoJSON with all metrics, boundary, provenance |

Variable keys: `population`, `income`, `poverty`, `home_value`. Invalid inputs return 422, unprepared towns 404, and failed upstream preparation 502. Failed downloads do not replace existing database data. SQL uses bound parameters. A single server worker is sufficient for this teaching app.

## Verify

```bash
python -m unittest -v
```

Six offline integration tests use isolated synthetic fixtures and a temporary database; no prepared town, network, or server is required. Checks cover overlap versus touching, whole geometries, joins, missing values, zeros, poverty denominators, top-coding, release consistency, failed-download preservation, repreparation, route validation, and static assets.

Browser checks: search → prepare → choropleth; switch all variables; prepare a second town; switch towns; inspect popups and table rows; restart and check persistence. In browser Network inspect `/api/tracts`; compare one feature to `prepared.json`.

## Troubleshooting

- **Old district/radius page:** stop the old server, start from the updated app directory, and hard-refresh.
- **Map library unavailable:** allow `unpkg.com`; a missing Leaflet library is reported in the page.
- **Streets blank but tracts visible:** check `tile.openstreetmap.org` requests and internet access.
- **Preparation fails:** check public Census TIGERweb/Census Reporter connectivity and the Uvicorn terminal. Existing prepared towns remain usable.
- **No matches:** verify state, spelling, and geography type.
- **File is not a database:** unset a `CENSUS_DB` pointing at an old DuckDB file; default is `data/tracts.sqlite`.
- **Port occupied:** stop the previous server or use `--port 8001` and that URL everywhere.

Quarto/GitHub Pages publish lecture HTML, not this Python service. A deployed app needs a Python-capable host, persistent storage, HTTPS, and separate decisions about public preparation jobs and access. Running locally does not publish the app.
