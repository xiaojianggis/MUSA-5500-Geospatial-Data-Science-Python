# Week 11: Large-data visualization and LiDAR

1. [Visualization I: Dask and Datashader](Visualizing%20Large%20Data-Lec1.html) — OSM points, Census density, color scales, and city maps. [Notebook](Visualizing%20Large%20Data-Lec1.ipynb).
2. [Visualization II: Queries, movement, and animation](Visualizing%20Large%20Data-Lec2.html) — category queries, district boundaries, taxi maps, hourly slider/GIF, radial heatmap, and parking exercise. [Notebook](Visualizing%20Large%20Data-Lec2.ipynb).
3. [LiDAR data processing](lecture-11B.html) — LiDAR basics with four diagrams; manual or Python downloads; a USGS catalog API example; raw maximum/IDW rasters, smoothed DSMs, and before/after plots. [Notebook](lecture-11B.ipynb).

Each notebook runs independently. The two visualization notebooks have been repaired from the original lectures and use local teaching extracts. The older combined `lecture-11A` remains available as a reference; use the two visualization notebooks above for the three-section teaching sequence.

All three sections use **Python (largeviz)**. Save the notebooks and downloaded data in one local folder, then open the notebooks there and run cells from top to bottom.

## Create or update the environment

Download [environment-viz.yml](environment-viz.yml) and the notebooks to a local folder named `week11`. Open a terminal in that folder:

```bash
# First installation:
conda env create -f environment-viz.yml
# For an existing largeviz environment, use this instead:
# conda env update -n largeviz -f environment-viz.yml
conda activate largeviz
python -m ipykernel install --user --name largeviz --display-name "Python (largeviz)"
jupyter lab
```

Keep `environment-viz.yml` beside the notebooks and run these commands from that folder. Create the environment once. Close running kernels before updating it. `environment-lidar.yml` defines the same shared environment for compatibility.

In VS Code, choose **Select Kernel → Python (largeviz)**. If missing, use **Select Another Kernel → Python Environments**, or reload the VS Code window. In Jupyter, choose **Kernel → Change Kernel → Python (largeviz)**.

To launch with the environment explicitly:

```bash
conda run -n largeviz jupyter lab
# Or:
conda run -n largeviz jupyter notebook
```

Check both package stacks:

```bash
conda run -n largeviz python -c "import numpy, numba, scipy.special, dask.dataframe, datashader, pdal, rasterio, pyproj; print('Both lab stacks import OK')"
```

## Data and outputs

Download the three notebooks linked above. The HTML tutorials include the same direct data links and folder instructions below. If a link opens in the browser, right-click it and choose **Save Link As…**. Keep the original filenames.

For the two visualization sections, save these files in `data/samples/` beside the notebooks:

| Data | Download |
| --- | --- |
| OSM GPS points | [osm_sample.parquet](data/samples/osm_sample.parquet) |
| Census dots | [census_sample.parquet](data/samples/census_sample.parquet) |
| Taxi trips | [taxi_sample.parquet](data/samples/taxi_sample.parquet) |
| Parking records | [parking_sample.csv](data/samples/parking_sample.csv) |
| Historical congressional boundaries (Visualization II) | [districts_2015.geojson](data/samples/districts_2015.geojson) |

See [data provenance](data/samples/provenance.json) for sources and sampling. These are teaching extracts, not representative estimates. Visualization I exports images to `outputs/viz1/`. Visualization II exports its GIF and standalone JavaScript hour slider to `outputs/viz2/`. The slider works in static HTML; zooming enlarges precomputed frames rather than recalculating density.

For Lecture 11B, download both files and save them in `data/lidar/` beside the notebooks:

| Case study | Download | Size |
| --- | --- | --- |
| University City | [Philadelphia_394.las](https://www.pasda.psu.edu/download/phillyLiDAR/2022/LAS/Classified_LAS/Philadelphia_394.las) | about 1.09 GB |
| Center City | [Philadelphia_456.las](https://www.pasda.psu.edu/download/phillyLiDAR/2022/LAS/Classified_LAS/Philadelphia_456.las) | about 997 MB |

Wait for both downloads to finish; no extraction is needed. Allow at least 3 GB of free space. The processing cells read these local files. Alternatively, use the notebook’s optional Python HTTP downloader (`DOWNLOAD_PASDA = True`) to save the same two files in `data/lidar/`. It streams files to disk, checks expected size and the LAS header, and reuses complete local downloads. Network downloads are disabled by default.

```text
week11/
├── Visualizing Large Data-Lec1.ipynb
├── Visualizing Large Data-Lec2.ipynb
├── lecture-11B.ipynb
├── environment-viz.yml
└── data/
    ├── samples/
    │   ├── osm_sample.parquet
    │   ├── census_sample.parquet
    │   ├── taxi_sample.parquet
    │   ├── parking_sample.csv
    │   └── districts_2015.geojson
    └── lidar/
        ├── Philadelphia_394.las
        └── Philadelphia_456.las
```

Open the notebooks from `week11`. Paths such as `data/lidar/Philadelphia_394.las` are relative to that folder. If you keep your LAS files elsewhere, change the two paths in Lecture 11B, Step 2.

The selected footprints are about 914 × 914 m each. Horizontal coordinates remain in the native projected CRS; elevations and pixel size are converted to meters using the LAS CRS metadata. The vertical datum stays unchanged. DSM elevations include trees/buildings/ground and are not building heights above terrain.

Lecture 11B writes to `outputs/lidar/case_studies/`:

- `*_max.tif`: unsmoothed maximum return per pixel, retained for comparison.
- `*_idw.tif`: first-return IDW interpolation using a 1.5-pixel radius.
- `*_dsm.tif`: 3 × 3 median of the IDW surface, retaining its NoData mask.
- Pipeline JSON files, `dsm_before_after.png`, and `center_city_university_city_dsm.png`.

IDW and median filtering reduce isolated spikes but can lower small roof features, canopy peaks, and narrow structures. Use raw maximum rasters when examining measured peaks. Remaining NoData is retained; no broad water/gap filling is performed. Earlier outputs from other versions of the lesson may still exist; the current notebooks do not use them.

## Reference scripts

The scripts now use the same small-radius IDW + median approach via `dsm_tools.py`, read the source CRS rather than assigning EPSG:4326, and preserve raw rasters. They create DSMs only; they do not classify ground or produce a DTM.

For a local LAS/LAZ file:

```bash
python pdal-las2desm.py input.las outputs/dsm.tif --resolution 1
```

If the input has no vertical CRS, supply `--z-scale`: `1` for meters, `0.3048` for international feet, or `0.3048006096012192` for US survey feet. Do not infer Z units from a horizontal EPSG code. Optionally pass `--crs EPSG:2272` to reproject horizontal coordinates.

For a USGS EPT patch:

```bash
python usgs_pdal_dsm.py PATCH outputs/dsm.tif \
  --bounds LEFT BOTTOM RIGHT TOP --crs EPSG:2272 --z-scale 1
```

Replace placeholders with the patch name and a small EPSG:3857 bounding box. Confirm the source Z units before choosing the scale. The callable `usgs_pdal_dsm()` now requires explicit `bounds` and `z_scale` keyword arguments. It no longer depends on a machine-specific city shapefile. `fill_desm()` writes separate smoothed outputs and never deletes raw DSMs.

## Render the lessons

After running and saving the notebooks, from the repository root:

```bash
quarto render "public/labs/week11-large-data-viz-lidar/Visualizing Large Data-Lec1.ipynb" --to html
quarto render "public/labs/week11-large-data-viz-lidar/Visualizing Large Data-Lec2.ipynb" --to html
quarto render public/labs/week11-large-data-viz-lidar/lecture-11B.ipynb --to html
```

Quarto renders saved outputs; it does not rerun downloads or processing.

## LiDAR concepts and API examples

The LiDAR notebook now introduces laser travel time, multiple returns and point clouds, LAS/LAZ attributes, DSM versus DTM, and rasterization/smoothing. Four original schematic graphics are embedded in the notebook, so students do not need to download an image folder to see them. Standalone PNG/SVG copies are in `imgs/`; rebuild them with `python make_lidar_figures.py` in `largeviz`.

Two optional download examples are included:

1. **PASDA file requests:** use `requests.get(..., stream=True)` to download the exact class LAS tiles into `data/lidar/`. This is HTTP file access, not a catalog search API.
2. **USGS TNMAccess API:** request catalog metadata for a longitude/latitude bounding box, inspect product titles and `downloadURL`, and optionally download one selected LAS/LAZ product into `data/lidar/usgs/`. Set `SEARCH_USGS = True` to search and `DOWNLOAD_USGS = True` only after inspecting the results. The rest of the class workflow continues to use the two PASDA tiles.

References: [NOAA LiDAR introduction](https://oceanservice.noaa.gov/geodesy/lidar.html), [NOAA LiDAR 101](https://coast.noaa.gov/data/digitalcoast/pdf/lidar-101.pdf), and [USGS TNMAccess API documentation](https://tnmaccess.nationalmap.gov/api/v1/docs).
