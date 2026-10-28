"""Reusable I/O and display helpers for the Week 11 LiDAR teaching notebook.

Rasterization itself is defined visibly in lecture-11B.ipynb. No input files
are deleted. Raw downloads belong in a cache outside the public website.
"""
from pathlib import Path
import json
import math
import numpy as np
import requests
import rasterio
from rasterio.fill import fillnodata
from rasterio.merge import merge
from rasterio.warp import transform_bounds, reproject, Resampling
from rasterio.transform import from_bounds
from scipy.ndimage import binary_fill_holes, distance_transform_edt, label, maximum, sum as labeled_sum
from matplotlib import colormaps
from PIL import Image
import mercantile

NODATA = -9999.0


def download_file(url, target, expected_bytes=None):
    """Stream to a temporary file; reuse only a complete cached download."""
    target = Path(target)
    if target.exists() and (expected_bytes is None or target.stat().st_size == expected_bytes):
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + '.part')
    with requests.get(url, stream=True, timeout=(15, 120),
                      headers={'User-Agent': 'MUSA550-classroom/1.0'}) as response:
        response.raise_for_status()
        with temporary.open('wb') as stream:
            for chunk in response.iter_content(1024 * 1024):
                stream.write(chunk)
    if expected_bytes is not None and temporary.stat().st_size != expected_bytes:
        raise ValueError(f'Incomplete download: {target.name}. Rerun to retry.')
    temporary.replace(target)
    return target


def inspect_las(path):
    """Read header CRS/units and count classifications in bounded chunks."""
    import laspy
    with laspy.open(path) as reader:
        header = reader.header
        crs = header.parse_crs()
        if crs is None or not crs.is_compound:
            raise ValueError('This lesson expects the provider compound horizontal/vertical CRS.')
        horizontal, vertical = crs.sub_crs_list[:2]
        if horizontal.is_bound:
            horizontal = horizontal.source_crs
        if not horizontal.is_projected:
            raise ValueError('A projected horizontal CRS is required for raster cells.')
        classes = np.zeros(256, dtype=np.int64)
        for chunk in reader.chunk_iterator(250_000):
            classes += np.bincount(np.asarray(chunk.classification), minlength=256)
        return {
            'file': Path(path).name, 'points': int(header.point_count),
            'bounds': [float(header.mins[0]), float(header.mins[1]),
                       float(header.maxs[0]), float(header.maxs[1])],
            'horizontal_wkt': horizontal.to_wkt(), 'horizontal_epsg': horizontal.to_epsg(),
            'xy_unit': horizontal.axis_info[0].unit_name,
            'xy_to_m': horizontal.axis_info[0].unit_conversion_factor,
            'z_unit': vertical.axis_info[0].unit_name,
            'z_to_m': vertical.axis_info[0].unit_conversion_factor,
            'vertical_datum': vertical.name,
            'classes': {int(i): int(v) for i, v in enumerate(classes) if v},
        }


def grid_for(info, cell_size_m):
    """Snap every file to one global grid, including points on maximum bounds."""
    if not np.isfinite(cell_size_m) or cell_size_m <= 0:
        raise ValueError('Cell size must be positive and finite.')
    res = cell_size_m / info['xy_to_m']
    xmin, ymin, xmax, ymax = info['bounds']
    ox, oy = math.floor(xmin / res) * res, math.floor(ymin / res) * res
    return dict(resolution=res, origin_x=ox, origin_y=oy,
                width=math.floor((xmax - ox) / res) + 1,
                height=math.floor((ymax - oy) / res) + 1)


def fill_small_holes(raw_path, filled_path, flag_path, max_pixels=2, max_hole_pixels=16):
    """Interpolate only short enclosed holes. Preserve larger/exterior NoData."""
    with rasterio.open(raw_path) as source:
        original = source.read(1)
        valid = source.read_masks(1) > 0
        profile = source.profile.copy()
        holes = (~valid) & binary_fill_holes(valid)
        components, number = label(holes)
        ids = np.arange(1, number + 1)
        if number:
            area = labeled_sum(holes, components, ids)
            radius = maximum(distance_transform_edt(~valid), components, ids)
            small_ids = ids[(area <= max_hole_pixels) & (radius <= max_pixels)]
            eligible = np.isin(components, small_ids)
        else:
            eligible = np.zeros(valid.shape, dtype=bool)
        interpolated = fillnodata(np.where(valid, original, 0).astype('float32'),
                                  mask=valid.astype('uint8'), max_search_distance=max_pixels)
        output = original.copy()
        output[eligible] = interpolated[eligible]
    profile.update(count=1, dtype='float32', nodata=NODATA)
    with rasterio.open(filled_path, 'w', **profile) as dest:
        dest.write(output, 1)
        dest.set_band_unit(1, 'm')
        dest.set_band_description(1, 'DSM elevation; small enclosed gaps interpolated')
        dest.update_tags(vertical_units='m', interpolation=f'enclosed holes <= {max_hole_pixels} pixels; radius <= {max_pixels} pixels')
    profile.update(dtype='uint8', nodata=255)
    with rasterio.open(flag_path, 'w', **profile) as dest:
        # 0 = observed, 1 = interpolated, 255 = remaining NoData.
        flags = np.full(valid.shape, 255, dtype='uint8')
        flags[valid] = 0
        flags[eligible] = 1
        dest.write(flags, 1)
        dest.set_band_description(1, '0 observed; 1 interpolated; 255 NoData')
    assert np.array_equal(output[valid], original[valid])
    return int(eligible.sum())


def mosaic_dsm(paths, destination):
    """Mosaic only the elevation band; never confuse counts with elevations."""
    from contextlib import ExitStack
    with ExitStack() as stack:
        sources = [stack.enter_context(rasterio.open(p)) for p in paths]
        reference = sources[0]
        if any(s.crs != reference.crs or not np.allclose(s.res, reference.res) for s in sources):
            raise ValueError('All source tiles must share a CRS and cell size.')
        array, transform = merge(sources, indexes=[1], nodata=NODATA,
                                 method='max', target_aligned_pixels=True)
        profile = reference.profile.copy()
    profile.update(height=array.shape[1], width=array.shape[2], transform=transform,
                   count=1, nodata=NODATA, dtype='float32')
    with rasterio.open(destination, 'w', **profile) as dest:
        dest.write(array)
        dest.set_band_unit(1, 'm')
        dest.set_band_description(1, 'NAVD88 DSM elevation (m)')
    return Path(destination)


def make_xyz_tiles(mosaic, folder, zooms=(15, 16, 17), max_tiles=500):
    """Create display-only RGBA PNG XYZ tiles with one shared elevation scale."""
    folder = Path(folder)
    records = []
    with rasterio.open(mosaic) as source:
        sample = source.read(1, masked=True).compressed()
        vmin, vmax = np.percentile(sample, [2, 98])
        if vmax <= vmin:
            vmax = vmin + 1
        west, south, east, north = transform_bounds(source.crs, 'EPSG:4326', *source.bounds)
        tiles = list(mercantile.tiles(west, south, east, north, zooms))
        if len(tiles) > max_tiles:
            raise ValueError(f'{len(tiles)} tiles requested; reduce extent or zooms.')
        for tile in tiles:
            b = mercantile.xy_bounds(tile)
            transform = from_bounds(b.left, b.bottom, b.right, b.top, 256, 256)
            data = np.full((256, 256), NODATA, dtype='float32')
            reproject(rasterio.band(source, 1), data, src_transform=source.transform,
                      src_crs=source.crs, src_nodata=NODATA,
                      dst_transform=transform, dst_crs='EPSG:3857', dst_nodata=NODATA,
                      resampling=Resampling.bilinear)
            mask = data != NODATA
            if not mask.any():
                continue
            rgba = colormaps['terrain'](np.clip((data - vmin) / (vmax - vmin), 0, 1), bytes=True)
            rgba[~mask, 3] = 0
            path = folder / str(tile.z) / str(tile.x) / f'{tile.y}.png'
            path.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgba).save(path)
            records.append({'z': tile.z, 'x': tile.x, 'y': tile.y, 'path': str(path.relative_to(folder))})
    metadata = {'scheme': 'xyz', 'tile_size': 256, 'zooms': list(zooms), 'vmin_m': float(vmin),
                'vmax_m': float(vmax), 'bounds_wgs84': [west, south, east, north],
                'colormap': 'terrain', 'purpose': 'display only; analytical elevations remain in GeoTIFF',
                'tiles': records}
    (folder / 'tilejson.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata
