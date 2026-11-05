# Census full-stack GIS demo — lecture 12C

Leaflet + browser JavaScript → FastAPI (Python) → DuckDB Spatial → JSON/GeoJSON.
The same Python server serves both the frontend and API. Download the source files into `week12/data` before preparing the database. No JavaScript build step or API key is needed.

## Setup

Use your existing course `geospatial` environment. Add the server and test tools in a terminal:

```bash
conda activate geospatial
conda install -c conda-forge fastapi uvicorn httpx
```

If you skipped Part A, also run `conda install -c conda-forge python-duckdb=1.5.6 pyarrow`. Keep this environment activated for the commands below. For notebook cells select **Python (geospatial)** and restart the kernel after installation. The included `environment.yml` is a dependency reference; no new environment is needed.


## Build the database

Download `census-full-stack.zip` and extract the `census-full-stack` project folder **inside `week12`**. Download the two source files into **`week12/data`** from the course Week 12 Part A tutorial before continuing. The ZIP contains application code and a dependency reference, not the source datasets.

```text
week12/
├── data/
│   ├── census_sample.parquet
│   └── districts_2015.geojson
├── lecture-12C.ipynb
└── census-full-stack/
    ├── environment.yml
    ├── prepare_data.py
    ├── database.py
    ├── app.py
    ├── test_app.py
    └── static/
```

Run shell commands below in a **terminal inside `week12/census-full-stack`**, rather than a notebook code cell. The notebook is a walkthrough; starting a long-running server in a cell would block Run All.

Open a terminal inside `census-full-stack`:

```bash
python prepare_data.py --data ../data
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

The first build downloads the DuckDB Spatial extension. It selects Pennsylvania dots using the historical district polygons and writes `data/census.duckdb`. It does not alter the original files or the 12A database.

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs. Try the Philadelphia button, change radius/category, and click another Pennsylvania location. The map uses Leaflet from a CDN and OpenStreetMap tiles, so it needs internet access. The browser receives district polygons and small query summaries, not the entire point table.

Stop the server with Ctrl+C. Keep one server worker for the classroom demo. Before rebuilding, stop the server and remove only this project's `data/census.duckdb`; the build refuses to overwrite an existing database. `CENSUS_DB` optionally sets a different database path in both preparation and API processes.

## API

- `GET /api/health`: database availability and total sample dots.
- `GET /api/districts?category=all`: 18 historical Pennsylvania districts with category counts.
- `GET /api/nearby?lon=-75.1636&lat=39.9526&radius_m=2000&category=all`: radius-query summary.

Category: `all`, `w`, `b`, `a`, `h`, or `o`. Radius: 100–20,000 meters. Search centers must lie in the historical Pennsylvania district coverage. Queries use bound parameters, and every request opens/closes a read-only database connection. Boundary points are assigned to the smallest matching district ID when building the district totals, as in 12A. A radius near the state border counts only points in the Pennsylvania selection.

## Verify

Run after preparation, from this project directory:

```bash
python -m unittest -v
```

Checks cover category totals against SQL, radius expansion, filtering, invalid requests, static files, and health. Browser checks: map loads; category changes the shading; the Philadelphia button returns a count; radius changes update the count; clicking outside Pennsylvania shows a useful message. Browser Network should show `/api/nearby` on each query.

## Hosting

GitHub Pages can host the lecture HTML, but cannot run this Python API. For this demo, keep the frontend and API on the same Python host. On a Python-capable host install the environment, prepare the database from supplied source files, then use a host-provided start command equivalent to `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`. Replace `$PORT` with your host's port setting. Preserve or rebuild the database on deployment, use HTTPS through the host, and check `/api/health`. `--reload` is for development only. Public multi-user write workloads are a later PostgreSQL/PostGIS topic; this example exposes read-only teaching queries. No deployment is created by running the lecture.

## Data limits

These are systematically thinned synthetic 2010 Census teaching dots with 2015 district boundaries. Counts are **sample dots**, not population estimates, density, or current demographics. Source labels reproduce historical race/ethnicity categories. See the Week 11 `data/samples/provenance.json`. Web-map radius circles are illustrative; SQL measures in EPSG:26918 meters, then returns GeoJSON coordinates in EPSG:4326.
