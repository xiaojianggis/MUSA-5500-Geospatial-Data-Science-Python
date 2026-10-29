# Week 11: Large-data visualization and LiDAR

- **Lecture 11A:** Dask tables → Datashader density maps → Census categories → taxi animation → parking exercise.
- **Lecture 11B:** two Philadelphia LAS tiles → raw maximum and IDW rasters → median-smoothed DSMs → before/after plots.

Both tutorials use **Python (largeviz)**. Save the notebooks and downloaded data in one local folder, then open the notebooks there and run cells from top to bottom.

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

Download [Lecture 11A](lecture-11A.ipynb) and [Lecture 11B](lecture-11B.ipynb). The HTML tutorials include the same direct data links and folder instructions below. If a link opens in the browser, right-click it and choose **Save Link As…**. Keep the original filenames.

For Lecture 11A, save these files in `data/samples/` beside the notebooks:

| Data | Download |
| --- | --- |
| OSM GPS points | [osm_sample.parquet](data/samples/osm_sample.parquet) |
| Census dots | [census_sample.parquet](data/samples/census_sample.parquet) |
| Taxi trips | [taxi_sample.parquet](data/samples/taxi_sample.parquet) |
| Parking records | [parking_sample.csv](data/samples/parking_sample.csv) |

See [data provenance](data/samples/provenance.json) for sources and sampling. These are teaching extracts, not representative estimates. Outputs are `outputs/viz/osm_density.png` and `outputs/viz/taxi_dropoffs_24h.gif`.

For Lecture 11B, download both files and save them in `data/lidar/` beside the notebooks:

| Case study | Download | Size |
| --- | --- | --- |
| University City | [Philadelphia_394.las](https://www.pasda.psu.edu/download/phillyLiDAR/2022/LAS/Classified_LAS/Philadelphia_394.las) | about 1.09 GB |
| Center City | [Philadelphia_456.las](https://www.pasda.psu.edu/download/phillyLiDAR/2022/LAS/Classified_LAS/Philadelphia_456.las) | about 997 MB |

Wait for both downloads to finish; no extraction is needed. Allow at least 3 GB of free space. The notebook reads these local files; it does not download or cache data automatically.

```text
week11/
├── lecture-11A.ipynb
├── lecture-11B.ipynb
├── environment-viz.yml
└── data/
    ├── samples/
    │   ├── osm_sample.parquet
    │   ├── census_sample.parquet
    │   ├── taxi_sample.parquet
    │   └── parking_sample.csv
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
quarto render public/labs/week11-large-data-viz-lidar/lecture-11A.ipynb --to html
quarto render public/labs/week11-large-data-viz-lidar/lecture-11B.ipynb --to html
```

Quarto renders saved outputs; it does not rerun downloads or processing.
