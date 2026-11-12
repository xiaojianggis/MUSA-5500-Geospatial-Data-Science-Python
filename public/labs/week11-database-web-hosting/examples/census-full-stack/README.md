# County Census tract explorer — lecture 12C

Select **State → County → Prepare census tract data**, then visualize individual census tracts. All map features and exported rows are tract-level ACS estimates. The selectors list counties and Census county equivalents only; no towns, townships, or places.

## Run locally

From the folder containing `lecture-11C.ipynb`:

```bash
conda activate geospatial
conda install -c conda-forge fastapi uvicorn httpx shapely
cd examples/census-full-stack
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

For the standalone ZIP use `cd census-full-stack`. Open **http://127.0.0.1:8000/**. Keep the terminal running; Ctrl+C stops it. After upgrading from the town version, stop the old server, start the updated app, and hard-refresh.

No API key is needed. Initial downloads, Leaflet, and free OpenStreetMap tiles require internet. Prepared county estimates persist locally in SQLite.

## Choose counties in different states

1. Select Pennsylvania; its county names load automatically.
2. Select **Dauphin County (42043)** and prepare it: **67 census tracts**.
3. Switch among population, median household income, poverty rate, and median home value.
4. Select New Jersey, then **Mercer County (34021)** and prepare it: **84 census tracts**.
5. Switch saved datasets using **Prepared county**. State names distinguish counties with the same name.
6. Click a tract or its table row to inspect estimates, MOEs, and an orange selected-tract boundary.

County equivalents (such as parishes, boroughs, census areas, and independent cities) appear where they are part of Census county geography. County names choose the study area; colors and records remain census tract data, not county aggregates.

## Preparation and data

The 2024 TIGERweb county layer supplies names and five-digit FIPS codes. The tract query filters directly by two-digit state and three-digit county codes. Every returned 11-digit tract GEOID must begin with the selected county FIPS. This includes the county's complete tract set, rather than tracts intersecting a town. Results are paginated and checked before replacing saved data.

Estimates: real **2020–2024 ACS five-year** via the public Census Reporter mirror. Boundaries: matching Census TIGERweb ACS 2024. Fields: B01003 population (count, not density), B19013 median household income (2024 dollars), B17001 poverty numerator / poverty-status universe × 100, B25077 median owner-occupied home value (2024 dollars).

Class breaks stay fixed per variable across counties. Direct estimates include available 90% MOEs; poverty rate MOE is not calculated, but its numerator/denominator and their MOEs are included. Null/gray means unavailable, not zero. Upper-coded medians show `+`. Medians cannot be summed. Geometries are slightly simplified for display after selection by FIPS.

Files beside the notebook:

- `data/census-tracts/acs2024_tracts.geojson`: one polygon feature per unique tract in prepared counties.
- `data/census-tracts/acs2024_tracts.csv`: same flat attributes without geometry.
- `data/census-tracts/counties/<fips>_tracts.geojson` and `.csv`: county-specific tract datasets.
- `data/census-tracts/README.txt`: data dictionary.
- `data/county-lists/<state-fips>.json`: county names for each visited state.
- `data/tract-explorer/source-cache`: cached public responses.
- `data/tract-explorer/counties/<fips>/prepared.json`: joined data/provenance.

The generated classroom snapshot covers Dauphin County, PA, and Mercer County, NJ. It is not nationwide. Prepare additional counties to expand it. Every record includes an 11-digit `geoid` and five-digit `county_geoid`; preserve FIPS columns as text in CSV.

The database is `data/tracts.sqlite` inside the app folder. New `counties` and `county_tracts` tables exclude old municipality records while leaving legacy town tables intact. Earlier municipality exports are archived in `data/tract-explorer/legacy-town-exports`, outside the active dataset/download. Original Part A dot/district files remain unchanged.

## CLI

From the app directory:

```bash
python prepare_data.py --state 42 --list-counties
python prepare_data.py --county 42043
python prepare_data.py --county 34021
python prepare_data.py --export
```

`--export` uses saved data without downloads. `CENSUS_DB` overrides the SQLite file, and `CENSUS_DATA_DIR` overrides the internal cache/package folder; deliverable tract data and county catalogs are sibling folders of that cache. Keep API/CLI settings consistent. Do not use an old DuckDB file as the SQLite database.

## API

| Route | Purpose |
| --- | --- |
| `/api/counties?state=42` | State's county names and IDs |
| `POST /api/prepare` | JSON `{"county_id":"42043"}` prepares complete tract data for the county |
| `/api/prepared-counties` | Prepared counties, state codes, tract counts |
| `/api/tracts?county_id=42043&variable=income` | Tract choropleth GeoJSON |
| `/api/dataset?county_id=42043&format=geojson` | Flat tract-only download; `format=csv` returns CSV |
| `/api/config`, `/api/health`, `/docs` | Variables, readiness, interactive docs |

Omit `county_id` on `/api/dataset` to export all unique prepared county tracts. Variable keys: `population`, `income`, `poverty`, `home_value`. The old town endpoints and IDs are replaced by county endpoints and five-digit FIPS codes.

## Verify and troubleshoot

```bash
python -m unittest -v
```

Eight offline tests cover complete county selection by FIPS, wrong-county rejection, state county lists, uncertainty/missing values, release mismatch, incomplete-download protection, preserving other counties/legacy towns, and tract-only exports.

Browser checks: select PA/Dauphin; prepare; switch variables; select NJ/Mercer; prepare; switch saved counties; select a tract; download CSV/GeoJSON and verify GEOID prefixes. Restart and check persistence.

If the town selector remains, restart the old server and hard-refresh. Use **Reload county list** on list-download failure. Check `unpkg.com` for a missing Leaflet library and `tile.openstreetmap.org` for missing streets. Failed preparation retains previously saved data. Use Uvicorn, not a static server or direct HTML file. Quarto/GitHub Pages publish the lecture, not this Python API; hosted execution needs a Python-capable host and persistent storage.
