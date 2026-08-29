# MUSA 5500 — Geospatial Data Science in Python

Course website for MUSA 5500 at the University of Pennsylvania. It is a static
React application built with Vite. Course notebooks, assignments, and other
downloads are stored in `public/`.

## Requirements

- [Node.js](https://nodejs.org/) 20 or newer
- npm (included with Node.js)
- Git

## Start the website locally

```bash
git clone https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python.git
cd MUSA-5500-Geospatial-Data-Science-Python
npm ci
npm run dev
```

Vite prints the local URL, normally
`http://localhost:5173/MUSA-5500-Geospatial-Data-Science-Python/`. Changes in
`src/` appear automatically. Files in `public/` are copied without modification.

To test from another device on the same network, use `npm run dev -- --host`.
Do not expose the development server directly to the public internet.

## Render a notebook as HTML

The lecture notebooks and their rendered HTML files live together under
`public/labs/`. They are rendered with [Quarto](https://quarto.org/). Check that
Quarto is installed with:

```bash
quarto --version
```

From the repository root, render a notebook with:

```bash
quarto render public/labs/week-9-web-scraping/lecture-9A.ipynb --to html
```

### Preview while editing

Open the notebook in JupyterLab (or VS Code), then in a second terminal run:

```bash
quarto preview public/labs/week-9-web-scraping/lecture-9A.ipynb --to html
```

Quarto opens a local preview URL and refreshes it after you save the notebook.
Use the saved cell outputs for a fast preview. If you also need Quarto to run
every cell before rendering, add `--execute`:

```bash
quarto preview public/labs/week-9-web-scraping/lecture-9A.ipynb --to html --execute
```

Replace the example path with the notebook you want to update. Quarto writes
the HTML beside the notebook, so the example creates or replaces:

```text
public/labs/week-9-web-scraping/lecture-9A.html
```

The command uses the notebook's saved cell outputs. To execute every cell
before rendering, use:

```bash
quarto render public/labs/week-9-web-scraping/lecture-9A.ipynb --to html --execute
```

Use `--execute` only when the notebook's Python environment and required data
are available. After rendering, make sure the corresponding entry in
`src/pages/Schedule.jsx` has an `href` pointing to the HTML file. Then run
`npm run dev` to check the lecture link locally. Commit the notebook, generated
HTML, any generated `<notebook-name>_files/` directory, and the schedule change.

## Check and build

```bash
npm run lint
npm run build
```

The production files are created in `dist/`. To preview them locally, run:

```bash
npm run preview
```

## Publish with GitHub Pages

The site is published automatically through GitHub Pages whenever changes are
pushed to the `main` branch. The workflow is defined in
`.github/workflows/deploy.yml`.

For the first deployment, enable GitHub Pages in the repository settings:

1. Go to **Settings** > **Pages**.
2. Under **Build and deployment**, select **GitHub Actions** as the source.
3. Push your changes to `main` and wait for the **Deploy (Vite) to GitHub Pages**
   workflow to finish.

The Vite base path in `vite.config.js` is set for this repository's GitHub Pages
URL. If the repository name changes, update that base path to match the new name.

## Course outline

The course covers Python fundamentals, exploratory analysis and visualization,
Pandas and GeoPandas, spatial mapping, raster operations, spatial analysis,
network analysis, web scraping and APIs, web publishing, clustering, machine
learning, and final project presentations. Labs and assignments are available
through the website and under `public/`.
