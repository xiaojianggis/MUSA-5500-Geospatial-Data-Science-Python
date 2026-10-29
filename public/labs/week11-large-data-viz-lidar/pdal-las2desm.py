"""Create a smooth DSM from a local LAS/LAZ file, retaining the IDW raster.

Example (activate largeviz first):
    python pdal-las2desm.py input.las outputs/dsm.tif

Source CRS is read from LAS metadata. If no vertical CRS is provided, pass
--z-scale explicitly. A DSM includes buildings/trees; this does not create a DTM.
"""
import argparse
from dsm_tools import create_dsm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('output')
    parser.add_argument('--crs', help='Optional projected output CRS, e.g. EPSG:2272')
    parser.add_argument('--z-scale', type=float, help='Source Z to meters, e.g. 1 or 0.3048')
    parser.add_argument('--resolution', type=float, default=1, help='Pixel size in meters')
    args = parser.parse_args()
    output = create_dsm({'type': 'readers.las', 'filename': args.source}, args.output,
                        output_crs=args.crs, z_scale=args.z_scale, resolution_m=args.resolution)
    print(output)


if __name__ == '__main__':
    main()
