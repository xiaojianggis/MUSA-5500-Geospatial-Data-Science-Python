"""Validate generated lesson artifacts. Run in the LiDAR environment after both notebooks."""
from pathlib import Path
import json
import tempfile
import numpy as np
import nbformat
import rasterio
from rasterio.transform import from_origin
from PIL import Image
from lidar_workflow import fill_small_holes, NODATA

ROOT = Path(__file__).resolve().parent

def main():
    for name in ['lecture-11A.ipynb', 'lecture-11B.ipynb']:
        book = nbformat.read(ROOT / name, 4)
        nbformat.validate(book)
        cells = [cell for cell in book.cells if cell.cell_type == 'code']
        assert all(cell.execution_count is not None for cell in cells), name
        assert not any(output.output_type == 'error' for cell in cells for output in cell.outputs), name
    root = ROOT / 'outputs/lidar'
    raw_files = sorted((root / 'raw_dsm').glob('*.tif'))
    assert len(raw_files) == 3
    total = 0
    for path in raw_files:
        with rasterio.open(path) as raw, rasterio.open(root / 'filled_dsm' / path.name) as filled:
            a = raw.read(1, masked=True)
            b = filled.read(1, masked=True)
            count = raw.read(2, masked=True)
            assert raw.count == 2 and raw.dtypes[0] == 'float32'
            assert raw.units[0] == 'm'
            assert raw.crs == filled.crs and raw.transform == filled.transform
            assert np.array_equal(a.compressed(), b.data[~a.mask])
            assert np.isclose(raw.res[0] * (1200 / 3937), 1)
            assert a.count() > 0 and int(count.sum()) > 0
            total += int(count.sum())
        qa = root / 'qa' / path.name.replace('_dsm.tif', '_interpolation.tif')
        with rasterio.open(qa) as source:
            flags = source.read(1)
            assert set(np.unique(flags)).issubset({0, 1, 255})
            assert np.all(flags[~a.mask] == 0)
            assert np.array_equal(flags == 255, b.mask)
    assert total == 3_949_569, total
    with rasterio.open(root / 'philadelphia_dsm_mosaic.tif') as source:
        assert source.count == 1 and source.units[0] == 'm' and source.read(1, masked=True).count() > 0
    meta = json.loads((root / 'tiles/dsm/tilejson.json').read_text())
    assert meta['scheme'] == 'xyz' and meta['tiles']
    assert set(item['z'] for item in meta['tiles']) == {15, 16, 17}
    for item in meta['tiles']:
        with Image.open(root / 'tiles/dsm' / item['path']) as image:
            assert image.size == (256, 256) and image.mode == 'RGBA'
    assert (ROOT / 'outputs/viz/taxi_hour_slider.html').is_file()
    with Image.open(ROOT / 'outputs/viz/taxi_dropoffs_24h.gif') as image:
        assert image.n_frames == 24
    # Regression: one small hole is filled, a large enclosed hole and exterior gaps are not.
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        a = np.full((30, 30), 10.0, dtype='float32')
        a[4, 4] = NODATA
        a[10:16, 10:16] = NODATA
        a[0:3, 24:27] = NODATA
        profile = dict(driver='GTiff', width=30, height=30, count=1, dtype='float32',
                       crs='EPSG:6565', transform=from_origin(0, 30, 1, 1), nodata=NODATA)
        with rasterio.open(folder / 'raw.tif', 'w', **profile) as dest:
            dest.write(a, 1)
        assert fill_small_holes(folder / 'raw.tif', folder / 'filled.tif', folder / 'flags.tif') == 1
        with rasterio.open(folder / 'filled.tif') as source:
            result = source.read(1)
            assert result[4, 4] == 10
            assert np.all(result[10:16, 10:16] == NODATA)
            assert np.all(result[0:3, 24:27] == NODATA)
    print(f'PASS: both executed notebooks; 3 DSM/count tiles; {total:,} retained points; '
          f'mosaic; {len(meta["tiles"])} XYZ tiles; 24 GIF frames; conservative interpolation.')

if __name__ == '__main__':
    main()
