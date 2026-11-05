# Week 12: Databases and web hosting

Three student-facing tutorials connect spatial analysis to publication:

1. [Census analysis with DuckDB Spatial](lecture-12A.html) — [notebook](lecture-12A.ipynb).
2. [Quarto, ChatGPT, localhost, and GitHub Pages](lecture-12B.html) — [notebook notes](lecture-12B.ipynb).

3. [Full-stack Census GIS with a Python backend](lecture-12C.html) — [notebook](lecture-12C.ipynb) · [runnable project ZIP](downloads/census-full-stack.zip).

Start at [the module homepage](index.html). [Download the tutorial folder](downloads/week12-tutorials.zip).

## Download data into week12/data

Create a local **`week12`** folder and a **`data`** subfolder. Download both required files using these links and save them directly in **`week12/data/`**, keeping the filenames unchanged:

- <a href="../week11-large-data-viz-lidar/data/samples/census_sample.parquet" download>Download census_sample.parquet</a>
- <a href="../week11-large-data-viz-lidar/data/samples/districts_2015.geojson" download>Download districts_2015.geojson</a>

If your browser saves files to Downloads, move them into `week12/data` before running the notebook. These are the same teaching datasets used in Week 11; Week 12 reads its own local copies.

```text
week12/
├── data/
│   ├── census_sample.parquet
│   └── districts_2015.geojson
├── lecture-12A.ipynb
├── lecture-12B.ipynb
└── lecture-12C.ipynb
```

Open Jupyter from `week12` and save the notebooks there. The notebook uses `DATA = Path("data")` to read these files. Generated analysis exports go into `week12/outputs`.

The source is a systematically thinned synthetic 2010 Census point extract, with historical source categories and 2015 congressional polygons. All counts are **sample dots**, not population estimates, density, or current district demographics. See [Week 11 provenance](../week11-large-data-viz-lidar/data/samples/provenance.json).

## Environment

Keep using the **`geospatial` environment** created earlier in the course. Install the additional packages into that environment; you do not need to create a Week 12 environment. Run these commands in a **terminal** (Anaconda Prompt on Windows):

```bash
conda activate geospatial
conda install -c conda-forge python-duckdb=1.5.6 pyarrow
```

DuckDB provides the database and spatial SQL; PyArrow supports Parquet/table exchange. The notebook also uses pandas, GeoPandas, and Matplotlib from your existing environment. If an import reports a missing package, install it in the same activated environment, for example `conda install -c conda-forge pandas geopandas matplotlib`.

To make the existing environment available in Jupyter:

```bash
conda install -c conda-forge ipykernel jupyterlab
python -m ipykernel install --user --name geospatial --display-name "Python (geospatial)"
jupyter lab
```

Select **Python (geospatial)** in the notebook's kernel menu. After installing a package, restart the kernel and rerun the notebook. To check the selected interpreter, run `import sys; print(sys.executable)` in a code cell; its path should point to `geospatial`. Quarto is installed separately in Part B.

The first `INSTALL spatial` needs internet access to download DuckDB's extension. `LOAD spatial` is required in each new connection.

Install the [Quarto CLI](https://quarto.org/docs/get-started/) separately for Section 2. Git is needed for the publishing exercise. No OpenAI API key is required: students use ChatGPT through its interface and save the returned code locally.

## Section 1: DuckDB Spatial

The notebook introduces tables, schemas, keys, SQL, connections, and persistence. It imports the existing point and polygon files, transforms both to EPSG:26918 for local spatial operations, filters and summarizes, queries a location and radius, performs a spatial join, maps the results, and exports small files for a website.

Rerunning the import cells rebuilds two teaching tables in `outputs/census_tutorial.duckdb`. This local database is not included in the download or website starters. CSV/JSON tables, GeoJSON, and PNG charts are written to `outputs/`. The notebook verifies unique assignment of all selected dots and checks persistence after closing/reopening the database.

## Section 2: Publish the results

The tutorial covers:

- Rendering a saved notebook to HTML with Quarto.
- A small Quarto website with navigation and a rendered notebook report.
- A complete ChatGPT prompt for an HTML/CSS/JavaScript website using exported results.
- A reusable example skill, with setup and a prompt-only fallback.
- Local HTTP preview and the difference between `file://`, localhost, and a public URL.
- Git commits, a GitHub repository, and branch-based GitHub Pages publication from `main` + `/docs`.
- Updating the source, rerendering, and pushing the refreshed public files.

The instructions do not create a repository or publish on the student's behalf. Static hosting serves exports and browser JavaScript; it does not run DuckDB or Python kernels.

## Downloadable examples

- [Working standalone website](downloads/starter-website.zip): `index.html`, CSS, JavaScript, and precomputed small exports.
- [Complete Quarto publishing starter](downloads/quarto-site.zip): homepage, executed report notebook, website, assets, and publication configuration.
- [Example ChatGPT prompt](examples/website-prompt.txt).
- [Example skill ZIP](downloads/census-story-site-skill.zip) and [SKILL.md](examples/skills/census-story-site/SKILL.md). This is not installed automatically.

These starters include only small analysis exports, not another Census point-data download. To use fresh analysis, replace their assets with your own notebook's exports before rendering.

For a standalone website, extract its ZIP, open a terminal inside `starter-website`, and run:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

For the Quarto starter, extract its ZIP, enter `quarto-site`, and run:

```bash
quarto preview
# After stopping preview with Ctrl+C:
quarto render
python -c "from pathlib import Path; Path('docs/.nojekyll').touch()"
```

The project `.gitignore` intentionally **does not ignore `docs/`**, because that starter teaches branch-based Pages hosting. The course module's own `.gitignore` excludes the locally rendered copy of the starter site to avoid duplicate generated files in this course repository.

## Instructor rendering

Execute and save the database notebook first. From the repository root:

```bash
quarto render public/labs/week12-database-web-hosting/index.qmd --to html
quarto render public/labs/week12-database-web-hosting/lecture-12A.ipynb --to html
quarto render public/labs/week12-database-web-hosting/lecture-12B.ipynb --to html
```

The module configuration renders saved notebook outputs. It does not rerun the database import or publish externally.

## Section 3: Full-stack Census GIS

Lecture 12C adds a local Leaflet frontend, FastAPI/Uvicorn backend, and read-only DuckDB Spatial database. Activate `geospatial` and run `conda install -c conda-forge fastapi uvicorn httpx` to add the server and test tools. Extract [census-full-stack.zip](downloads/census-full-stack.zip), then follow its README to prepare the database from the downloaded files in `week12/data` and start the API. Save the extracted project inside `week12`; no hosting account is needed. The project includes integration tests and a category/radius query map.

Render the notes with `quarto render public/labs/week12-database-web-hosting/lecture-12C.ipynb --to html --no-execute` from the course repository root. The optional HTTP client cell requires the app to be running. Quarto/GitHub Pages serve the lecture; the live Python app requires its own Python-capable server.
