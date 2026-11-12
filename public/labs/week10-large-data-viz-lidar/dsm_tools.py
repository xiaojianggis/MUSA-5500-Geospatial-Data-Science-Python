"""Small, non-destructive DSM helpers used by the two command-line scripts."""
from pathlib import Path
import json

import numpy as np
import pdal
import rasterio
from pyproj import CRS
from scipy.ndimage import distance_transform_edt, median_filter


def smooth_dsm(source, destination, size=3):
    """Median-filter valid pixels; keep the input NoData mask and raw raster."""
    if size < 1 or size % 2 != 1:
        raise ValueError('size must be a positive odd number')
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Write the smoothed surface to a separate file')
    with rasterio.open(source) as src:
        data = src.read(1, masked=True)
        valid = ~np.ma.getmaskarray(data)
        if not valid.any():
            raise ValueError(f'No valid elevations in {source}')
        # Temporary nearest values prevent NoData from entering the median.
        indices = distance_transform_edt(~valid, return_distances=False, return_indices=True)
        filtered = median_filter(data.data[tuple(indices)], size=size, mode='nearest')
        result = np.where(valid, filtered, src.nodata).astype('float32')
        profile = src.profile.copy()
        tags = src.tags()
        unit = src.units[0]
    profile.update(count=1, dtype='float32', compress='deflate')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(destination, 'w', **profile) as dst:
        dst.write(result, 1)
        dst.set_band_description(1, 'Smoothed first-return DSM elevation')
        if unit:
            dst.set_band_unit(1, unit)
        dst.update_tags(**tags)
        dst.update_tags(smoothing=f'{size}x{size} median; original NoData mask retained',
                        source_raster=source.name)
    return destination


def create_dsm(reader, output, *, output_crs=None, z_scale=None, resolution_m=1.0, bounds=None):
    """Rasterize LAS/EPT first returns with IDW, then write a separate smooth DSM.

    bounds, when provided, uses output horizontal CRS units. z_scale explicitly
    converts source elevations to meters if the source lacks a vertical CRS.
    The original vertical datum is retained; this does not transform heights.
    """
    if resolution_m <= 0:
        raise ValueError('resolution_m must be positive')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    reader_type = reader['type']
    header = pdal.Pipeline(json.dumps([reader])).quickinfo[reader_type]
    srs = header.get('srs', {})
    metadata_srs = header.get('metadata', {}).get('srs', {})
    wkt = metadata_srs.get('compoundwkt') or srs.get('compoundwkt') or srs.get('wkt')
    if not wkt:
        raise ValueError('Source CRS is missing; inspect the source metadata')
    source_crs = CRS.from_wkt(wkt)
    horizontal = source_crs.sub_crs_list[0] if source_crs.is_compound else source_crs
    if horizontal.is_bound:
        horizontal = horizontal.source_crs
    target = CRS.from_user_input(output_crs) if output_crs else horizontal
    if not target.is_projected:
        raise ValueError('Choose a projected output CRS with --crs')
    if z_scale is None:
        if not source_crs.is_compound:
            raise ValueError('No vertical CRS: specify --z-scale (1 for meters, 0.3048 for feet)')
        z_scale = source_crs.sub_crs_list[1].axis_info[0].unit_conversion_factor
    if z_scale <= 0:
        raise ValueError('z_scale must be positive')
    resolution = resolution_m / target.axis_info[0].unit_conversion_factor
    stages = [reader]
    if target != horizontal:
        stages.append({'type': 'filters.reprojection', 'in_srs': horizontal.to_wkt(),
                       'out_srs': target.to_wkt()})
    if bounds:
        left, bottom, right, top = bounds
        stages.append({'type': 'filters.crop', 'bounds': f'([{left},{right}],[{bottom},{top}])'})
    stages += [
        {'type': 'filters.expression', 'expression':
         'ReturnNumber == 1 && Classification != 7 && Classification != 18 && Withheld == 0'},
        {'type': 'filters.assign', 'value': f'Z = Z * {z_scale:.15g}'},
    ]
    raw = output.with_name(output.stem + '_idw.tif')
    stages.append({'type': 'writers.gdal', 'filename': str(raw), 'output_type': 'idw',
                   'resolution': resolution, 'radius': 1.5 * resolution,
                   'window_size': 0, 'data_type': 'float32', 'nodata': -9999,
                   'override_srs': target.to_wkt(), 'gdalopts': 'COMPRESS=DEFLATE,TILED=YES'})
    specification = {'pipeline': stages}
    output.with_suffix('.json').write_text(json.dumps(specification, indent=2))
    pdal.Pipeline(json.dumps(specification)).execute_streaming(chunk_size=250_000)
    with rasterio.open(raw, 'r+') as dst:
        dst.set_band_unit(1, 'm')
        dst.update_tags(vertical_reference=source_crs.name, interpolation='IDW radius = 1.5 pixels')
    return smooth_dsm(raw, output)
