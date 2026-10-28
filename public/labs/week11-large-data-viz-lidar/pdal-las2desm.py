## This script is used to generate the DEM/DSM tif 
## from the LiDAR cloud points based on PDAL
## Last modified Aug 7, 2021 by Xiaojiang Li, Temple University

### last modified by Xiaojiang Li, Dec 31, 2023, last day of 2023 Temple University of Pennsylvania
### this version add the laz file downloading part, like Miami

import pdal
import os, os.path
import rasterio
from rasterio.fill import fillnodata
import fiona
import os, os.path
import urllib.request
import time


### download the laz file
# for miami, noaa
root = r'/home/tul69181/research/thermal-env/data/florida/miami/'
outfolder = os.path.join(root, 'miami_noaa')
tileshp = os.path.join(root, 'spatial-data/fl2018_miamidade_index.shp')
epsg_code = '2236' #florida, project, projection


## For research triangle, NC
root = r'/home/tul69181/research/thermal-env/data/durham'
outfolder = os.path.join(root, 'patches')
tileshp = os.path.join(root, 'spatial-data/tileindex_orange_durham.shp')
epsg_code = '6543' #durham, project, projection


lasfolder = os.path.join(outfolder, 'laz')
if not os.path.exists(lasfolder):
    os.mkdir(lasfolder)


tiles_lyr = fiona.open(tileshp)
for feat in tiles_lyr:
    props = feat['properties']
    url = props['URL']
    basename = os.path.basename(props['Name'])
    
    # if basename != '20131208_usgspostsandy_19TCG210890.laz':
    #     continue
    print(basename)
    outlas = os.path.join(lasfolder, basename)
    if os.path.exists(outlas): continue
    time.sleep(1)
    try:
        urllib.request.urlretrieve(url, outlas)
    except:
        try:
            urllib.request.urlretrieve(url, outlas)
        except:
            urllib.request.urlretrieve(url, outlas)


### ==============Convert laz file into las, dem, dsm===================
# root = r'/home/tul69181/research/uv-expo/lidar-proj/lazfile/boston'
root = outfolder

lasfolder = os.path.join(root, 'laz')
demfolder = os.path.join(root, 'dem')
dsmfolder = os.path.join(root, 'dsm')

## For miami, NC

if not os.path.exists(demfolder): os.mkdir(demfolder)
if not os.path.exists(dsmfolder): os.mkdir(dsmfolder)

for idx, las in enumerate(os.listdir(lasfolder)):
    lasfile = os.path.join(lasfolder, las)
    print('The lasfile name is:', lasfile)
    
    demfile = os.path.join(demfolder, 'dem_' + las[:-4] + '.tif')
    
    if os.path.exists(demfile): continue

    dsmfile = os.path.join(dsmfolder, 'dsm_' + las[:-4] + '.tif')
    
    dsmjson = """
    {
      "pipeline": [
        "%s",
        {
          "type":"filters.reprojection",
          "in_srs": "EPSG:4326",
          "out_srs": "EPSG:%s"
        },
        {
          "type": "filters.range",
          "limits": "returnnumber[1:1]"
        },
        {
          "filename": "%s",
          "gdaldriver": "GTiff",
          "output_type": "idw",
          "resolution": "2.0",
          "type": "writers.gdal",
          "radius": 5
        }
      ]
    }
    
    """%(lasfile, epsg_code, dsmfile)
    
    
    demjson = '''
    {
        "pipeline": [
            "%s",
            {
                "type":"filters.reprojection",
                "in_srs":"EPSG:4326",
                "out_srs":"EPSG:%s"
            },
          
            {
                "type": "filters.range",
                "limits": "Classification[2:2]"
            },

            {
              "type":"filters.smrf",
              "ignore":"Classification[7:7]",
              "slope":0.2,
              "window":16,
              "threshold":0.45,
              "scalar":1.2
            },

            {
                "filename": "%s",
                "gdaldriver": "GTiff",
                "resolution": 2,
                "radius": 4,
                "output_type":"idw",
                "output_type": "mean",
                "type": "writers.gdal"
            }
        ]
    }

    '''%(lasfile, epsg_code, demfile)
    
    
    # # create the dsm based on the dsm pipeline
    try:
        pipeline = pdal.Pipeline(dsmjson)
        count = pipeline.execute()
    except:
        print("Something wrong with the dsm")
        continue
    # create the dem based on the dem pipeline
    try:
        pipeline = pdal.Pipeline(demjson)
        count = pipeline.execute()
    except:
        print("Something wrong with dem")
        continue



## Fill the nodata in the DEM
fill_demfolder = os.path.join(root, 'fill_dem')
if not os.path.exists(fill_demfolder): os.mkdir(fill_demfolder)

for dem in os.listdir(demfolder):
    demfile = os.path.join(demfolder, dem)
    print('The demfile is:', demfile)

    with rasterio.open(demfile) as src:
        profile = src.profile
        arr = src.read(1)
        arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=200, smoothing_iterations=0)
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                 "compress": 'lzw'})

    newtif_file = os.path.join(fill_demfolder, dem)
    with rasterio.open(newtif_file, 'w', **profile) as dest:
        dest.write_band(1, arr_filled)



## Fill the nodata in the DSM, using smaller distance
fill_dsmfolder = os.path.join(root, 'fill_dsm')
if not os.path.exists(fill_dsmfolder): os.mkdir(fill_dsmfolder)

for dsm in os.listdir(dsmfolder):
    dsmfile = os.path.join(dsmfolder, dsm)
    print('The dsmfile is:', dsmfile)
    
    with rasterio.open(dsmfile) as src:
        profile = src.profile
        arr = src.read(1)
        arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=20, smoothing_iterations=0)
        out_meta = src.meta
        
    out_meta.update({"driver": "GTiff",
                 "compress": 'lzw'})
    
    newtif_file = os.path.join(fill_dsmfolder, dsm)
    with rasterio.open(newtif_file, 'w', **profile) as dest:
        dest.write_band(1, arr_filled)
        