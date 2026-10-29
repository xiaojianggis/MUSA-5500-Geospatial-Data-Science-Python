# Week 12: Databases and web hosting

Two student-facing tutorials connect spatial analysis to publication:

1. [Census analysis with DuckDB Spatial](lecture-12A.html) — [notebook](lecture-12A.ipynb).
2. [Quarto, ChatGPT, localhost, and GitHub Pages](lecture-12B.html) — [notebook notes](lecture-12B.ipynb).

Start at [the module homepage](index.html). [Download the tutorial folder](downloads/week12-tutorials.zip).

## Reuse Week 11 data

**Do not download another Census dataset.** The database notebook uses the exact `census_sample.parquet` and `districts_2015.geojson` files from Week 11. It selects Pennsylvania inside DuckDB.

```text
course-work/
├── week11/
│   └── data/samples/
│       ├── census_sample.parquet
│       └── districts_2015.geojson
└── week12/
    ├── lecture-12A.ipynb
    ├── lecture-12B.ipynb
    └── environment.yml
```

Open the notebook from `week12`. The one data-folder setting is:

```python
DATA = Path("../week11/data/samples")
```

If your Week 11 folder has another name, edit that path. For an instructor running from this course repository's lab folder, use `Path("../week11-large-data-viz-lidar/data/samples")`. There is no automatic path detection or data downloading in the notebook.

The source is a systematically thinned synthetic 2010 Census point extract, with historical source categories and 2015 congressional polygons. All counts are **sample dots**, not population estimates, density, or current district demographics. See [Week 11 provenance](../week11-large-data-viz-lidar/data/samples/provenance.json).

## Environment

From the local `week12` folder:

```bash
conda env create -f environment.yml
conda activate census-web
python -m ipykernel install --user --name census-web --display-name "Python (census-web)"
jupyter lab
```

Use **Python (census-web)**. The first `INSTALL spatial` needs internet access to download DuckDB's extension. `LOAD spatial` is required in each new connection. Existing environments can be updated with `conda env update -n census-web -f environment.yml`.

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
