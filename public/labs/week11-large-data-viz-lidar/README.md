# Week 11: Large-data visualization and LiDAR

- **Lecture 11A:** Dask tables → Datashader density maps → Census categories → taxi animation → parking exercise.
- **Lecture 11B:** two Philadelphia LAS tiles → raw maximum and IDW rasters → median-smoothed DSMs → before/after plots.

Both tutorials use **Python (largeviz)**. Run cells from top to bottom from this folder or the repository root.

## Create or update the environment

From the repository root:

```bash
cd public/labs/week11-large-data-viz-lidar
# First installation:
conda env create -f environment-viz.yml
# For an existing largeviz environment, use this instead:
# conda env update -n largeviz -f environment-viz.yml
conda activate largeviz
python -m ipykernel install --user --name largeviz --display-name "Python (largeviz)"
jupyter lab
```

If downloading the lab separately, keep `environment-viz.yml` beside the notebooks and run these commands from that folder, omitting `cd`. Create the environment once. Close running kernels before updating it. `environment-lidar.yml` defines the same shared environment for compatibility.

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

Lecture 11A uses the bundled extracts in `data/samples/`. See `data/samples/provenance.json` for sources and sampling. These are teaching extracts, not representative estimates. Outputs are `outputs/viz/osm_density.png` and `outputs/viz/taxi_dropoffs_24h.gif`.

Lecture 11B downloads `Philadelphia_394.las` (University City) and `Philadelphia_456.las` (Center City) from PASDA, about **2.09 GB** total. Complete downloads are reused. The default cache is `~/.cache/musa550-week11/raw/`; set `MUSA550_CACHE` before launching Jupyter to use another cache root.

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
