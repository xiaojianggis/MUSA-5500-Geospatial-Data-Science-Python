# Large spatial data visualization and LiDAR

Two executable lessons, rendered with the same Quarto configuration and presentation CSS as Weeks 9–10:

- `lecture-11A.ipynb` → `lecture-11A.html`: merged and corrected large-data visualization lectures.
- `lecture-11B.ipynb` → `lecture-11B.html`: three real Philadelphia LAS files to analytical DSMs and XYZ web tiles.

The original lecture notebooks are retained locally and excluded from version control because of their large embedded outputs (one is about 285 MiB). The three supplied scripts are retained as small reference files. Run the new notebooks rather than the original scripts, which contain machine-specific paths and project assumptions.

## Environments and execution

Create the appropriate environment from `environment-viz.yml` or `environment-lidar.yml`, then select that environment's notebook kernel. Run each notebook from this folder or the repository root. Both lessons explain their dependencies and workflow.

Visualization runs from the bundled real-data extracts in `data/samples/`; see `provenance.json` for sampling limitations and original sources. The samples are for teaching, not representative estimates of population, demand, or travel behavior. Original billion-point archives are optional and are not downloaded by Run All.

The LiDAR notebook downloads `Philadelphia_104.las`, `Philadelphia_105.las`, and `Philadelphia_114.las` from PASDA, about 120 MB in total. `data/lidar_manifest.json` records URLs, sizes, point counts, and provider footprints. Raw LAS data is cached outside the public website at `~/.cache/musa550-week11/raw/`, or under the directory specified by `MUSA550_CACHE`.

Source horizontal and vertical units are US survey feet. Analytical outputs retain the native horizontal CRS but convert elevation values to meters; the one-meter pixel size is converted to native horizontal units. The vertical datum remains NAVD88. This is a unit conversion, not a vertical-datum transformation.

## Generated artifacts

`outputs/viz/` contains a density PNG, a 24-frame taxi GIF, and a standalone Bokeh hourly slider. The slider embeds JavaScript and precomputed frames; it works without a live Python server. Zooming does not reaggregate the source data.

`outputs/lidar/` contains:

- `raw_dsm/`: three aligned Float32 GeoTIFFs, band 1 maximum elevation (m), band 2 retained point count.
- `filled_dsm/`: three elevation-only rasters with only small enclosed holes interpolated.
- `qa/`: three flags rasters, 0 observed / 1 interpolated / 255 NoData.
- `pipelines/`: the executed PDAL stage specifications.
- `philadelphia_dsm_mosaic.tif`: the analytical elevation mosaic.
- `tiles/dsm/{z}/{x}/{y}.png`: RGBA display tiles at zooms 15–17 and shared-scale `tilejson.json` metadata.
- `dsm_viewer.html`: Leaflet viewer using the local XYZ tiles. Leaflet assets require internet access; no map API key is needed.

LAS files are sparse edge examples with substantial water/NoData coverage. Do not interpret the maximum surface as terrain or canopy height, or interpolate across broad gaps. The original LAS files and raw rasters are never deleted by the notebooks.

## Validate and render

After running both notebooks, run in the LiDAR environment:

```bash
python validate_outputs.py
```

From the repository root:

```bash
quarto render public/labs/week11-large-data-viz-lidar/lecture-11A.ipynb --to html
quarto render public/labs/week11-large-data-viz-lidar/lecture-11B.ipynb --to html
npm run build
```

Quarto uses saved outputs; no new downloads occur while rendering. The course schedule links to both HTML files. Use `npm run dev` or another HTTP server for the local tile viewer, rather than opening it through `file://`.
