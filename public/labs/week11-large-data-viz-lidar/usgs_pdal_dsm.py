"""Create a smooth DSM from a bounded USGS EPT request.

Example:
    python usgs_pdal_dsm.py PATCH output.tif --bounds LEFT BOTTOM RIGHT TOP \
        --crs EPSG:2272 --z-scale 1

EPT bounds are EPSG:3857 coordinates. Specify the actual source Z-to-meter
factor; a horizontal EPSG code does not establish elevation units. This reads
full-resolution EPT points (no reader-level thinning) and retains raw IDW output.
"""
import argparse
from pathlib import Path
from dsm_tools import create_dsm, smooth_dsm


def usgs_pdal_dsm(lidar_patchs, root, cityname, epsg_code, *, bounds, z_scale, resolution_m=1):
    """Process explicit EPSG:3857 bounds for each patch; retain all source rasters."""
    outputs = []
    for patch in lidar_patchs:
        left, bottom, right, top = bounds
        reader = {'type': 'readers.ept',
                  'filename': f'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/{patch}/ept.json',
                  'bounds': f'([{left},{right}],[{bottom},{top}])'}
        output = Path(root) / cityname / 'patches' / patch / 'dsm' / 'dsm.tif'
        outputs.append(create_dsm(reader, output, output_crs=f'EPSG:{epsg_code}',
                                  z_scale=z_scale, resolution_m=resolution_m))
    return outputs


def fill_desm(lidar_patchs, root, cityname):
    """Smooth existing DSMs into a separate directory; do not fill large gaps."""
    for patch in lidar_patchs:
        folder = Path(root) / cityname / 'patches' / patch
        for source in (folder / 'dsm').glob('*.tif'):
            smooth_dsm(source, folder / 'smooth_dsm' / source.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('patch')
    parser.add_argument('output')
    parser.add_argument('--bounds', nargs=4, type=float, required=True,
                        metavar=('LEFT', 'BOTTOM', 'RIGHT', 'TOP'))
    parser.add_argument('--crs', required=True)
    parser.add_argument('--z-scale', type=float, required=True)
    parser.add_argument('--resolution', type=float, default=1)
    args = parser.parse_args()
    left, bottom, right, top = args.bounds
    reader = {'type': 'readers.ept',
              'filename': f'https://s3-us-west-2.amazonaws.com/usgs-lidar-public/{args.patch}/ept.json',
              'bounds': f'([{left},{right}],[{bottom},{top}])'}
    print(create_dsm(reader, args.output, output_crs=args.crs,
                     z_scale=args.z_scale, resolution_m=args.resolution))


if __name__ == '__main__':
    main()
