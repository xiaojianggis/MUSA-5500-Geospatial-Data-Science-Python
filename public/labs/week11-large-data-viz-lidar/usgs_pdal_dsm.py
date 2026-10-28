## This script is used to generate the digital surface model and dem 
## based on the lidar cloud point

## last modified by Xiaojiang Li, Temple University, this is used to handle
## the cases that some cities need more LiDAR patches, Dec 29, 2023

## last modified by Xiaojiang Li, Temple University, to make the script more 
## organized therefore, can be called as function, Jan 24, 2024

## last modified by Xiaojiang Li, UPenn, to seperate the dsm generation and the
## the gap filling, therefore, it is more flexible, on Mar 1st, 2025

import pdal
import fiona
import os, os.path
from shapely.geometry import shape
import rasterio
from rasterio.fill import fillnodata
import shutil


def usgs_pdal_dsm(lidar_patchs, root, cityname, epsg_code):
    '''
    This function is used to download the LiDAR data and generate the DSM
    
    Parameters:
        lidar_patchs: a list of the lidar patches, like ['FL_Peninsular_FDEM_Duval_2018', 'FL_Peninsular_FDEM_Clay_2018']
        root: the walking directory
        cityname: str, the city name, like philadelphia
        epsg_code: the epsg code for different cities
    '''
    
    print("using usgs to start the LiDAR data processing")

    cityfolder = os.path.join(root, cityname)
    if not os.path.exists(cityfolder):
        os.mkdir(cityfolder)

    # the extent shapefile that you want to download the LiDAR data,
    shpfile = os.path.join(cityfolder, 'spatial-data/city_limit_3857.shp') # for florida, heat expos, pedestrian

    lyr = fiona.open(shpfile)
    for feat in lyr:
        props = feat['properties']
        # name = props['NAME']
        
        bounds = shape(feat['geometry']).bounds
        try:
            name = props['name']
            print('the props and bounds are:', name, bounds)
        except:
            print("There is no name attribute")

    leftX = bounds[0]
    rightX = bounds[2]
    topY = bounds[3]
    bottomY = bounds[1]

    print("The boud is:--------------", bounds)

    tilesize = 2000 
    buffsize = 150

    tilewidth = (rightX - leftX)/tilesize
    tileheigh = (topY - bottomY)/tilesize

    tilenumX = int((rightX - leftX)/tilesize) + 1
    tilenumY = int((topY - bottomY)/tilesize) + 1

    # for each patch, because some cities need more than one patch
    for lidar_patch in lidar_patchs:
        patchesfolder = os.path.join(cityfolder, 'patches')
        if not os.path.exists(patchesfolder): os.mkdir(patchesfolder)
        
        patch_root = os.path.join(patchesfolder, lidar_patch)
        if not os.path.exists(patch_root): os.mkdir(patch_root)
        lasfolder = os.path.join(patch_root, 'las')
        demfolder = os.path.join(patch_root, 'dem')
        dsmfolder = os.path.join(patch_root, 'dsm')
        
        if not os.path.exists(lasfolder): os.mkdir(lasfolder)
        if not os.path.exists(demfolder): os.mkdir(demfolder)
        if not os.path.exists(dsmfolder): os.mkdir(dsmfolder)

        for x in range(tilenumX):
            for y in range(tilenumY):
                tile_leftx = leftX + x*tilesize - buffsize
                tile_rightx = leftX + (x+1)*tilesize + buffsize
                tile_topy = bottomY + (y + 1)*tilesize + buffsize
                tile_bottomy = bottomY + y*tilesize - buffsize
                
                print('The x, y, and tile_leftx, tile_rightx, tile_topy, tile_bottomy', x, y, tile_leftx, tile_rightx, tile_bottomy, tile_topy)
                tilename = 'row%s-col%s'%(y, x)
                las_pathname = os.path.join(lasfolder, tilename+'.las')
                dem_pathname = os.path.join(demfolder, tilename+'.tif')
                dsm_pathname = os.path.join(dsmfolder, tilename+'.tif')
                
                # if the file existed
                if os.path.exists(dem_pathname) and os.path.exists(dsm_pathname):
                    continue
                
                # from USGS
                dsmjson = """
                    {
                        "pipeline": [
                            {
                                "type": "readers.ept",
                                "filename":"https://s3-us-west-2.amazonaws.com/usgs-lidar-public/%s/ept.json",
                                "bounds": "([%s, %s], [%s, %s])",
                                "resolution": 3
                            },
                            {
                                "type":"filters.reprojection",
                                "in_srs": "EPSG:3857",
                                "out_srs": "EPSG:%s"
                            },
                            {
                                "type": "writers.las",
                                "compression": "true",
                                "minor_version": "2",
                                "dataformat_id": "0",
                                "filename": "%s"
                            },
                            {
                                "type": "filters.range",
                                "limits": "returnnumber[1:1]"
                            },
                            {
                                "filename": "%s",
                                "gdaldriver": "GTiff",
                                "output_type": "idw",
                                "resolution": "3.0",
                                "type": "writers.gdal",
                                "radius": 10
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
                                "resolution": 3,
                                "radius": 6,
                                "output_type":"idw",
                                "output_type": "mean",
                                "type": "writers.gdal"
                            }
                            
                        ]
                    }"""%(lidar_patch, tile_leftx, tile_rightx, tile_bottomy, tile_topy, epsg_code, las_pathname, dsm_pathname, dem_pathname)
                
                try:
                    # create the dsm based on the dsm pipeline
                    pipeline = pdal.Pipeline(dsmjson)
                    count = pipeline.execute()
                except:
                    print('something wrong or the .las is not available', pipeline)
                

## the generated DEM/DSM tiles are not complete, therefore, we need to fill
## the gaps
def fill_desm(patch_root, root, cityname):
        '''The will loop all dem/dsm tiles and fill the gap and delete the 
        raw dem/dsm tile
        '''
        cityfolder = os.path.join(root, cityname)
        # for each patch, because some cities need more than one patch
        for lidar_patch in lidar_patchs:
            patchesfolder = os.path.join(cityfolder, 'patches')
            if not os.path.exists(patchesfolder): os.mkdir(patchesfolder)
            
            patch_root = os.path.join(patchesfolder, lidar_patch)
            if not os.path.exists(patch_root): os.mkdir(patch_root)
            demfolder = os.path.join(patch_root, 'dem')
            dsmfolder = os.path.join(patch_root, 'dsm')

            # ## Fill the nodata in the DEM
            # fill_demfolder = os.path.join(patch_root, 'fill_dem')
            # if not os.path.exists(fill_demfolder): os.mkdir(fill_demfolder)

            # for dem in os.listdir(demfolder):
            #     if not dem.endswith(".tif"): continue
            #     demfile = os.path.join(demfolder, dem)
            #     print('The demfile is:', demfile)

            #     with rasterio.open(demfile) as src:
            #         profile = src.profile
            #         arr = src.read(1)
            #         arr_filled = fillnodata(arr, mask=src.read_masks(1), max_search_distance=200, smoothing_iterations=0)
            #         out_meta = src.meta

            #     out_meta.update({"driver": "GTiff",
            #                 "compress": 'lzw'})

            #     newtif_file = os.path.join(fill_demfolder, dem)
            #     with rasterio.open(newtif_file, 'w', **profile) as dest:
            #         dest.write_band(1, arr_filled)

            # shutil.rmtree(demfolder)


            ## Fill the nodata in the DSM, using smaller distance
            fill_dsmfolder = os.path.join(patch_root, 'fill_dsm')
            if not os.path.exists(fill_dsmfolder): os.mkdir(fill_dsmfolder)
            
            for dsm in os.listdir(dsmfolder):
                if not dsm.endswith(".tif"): continue
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

            ## remove the original dem/dsm folder, this will be used to record the tiles
            shutil.rmtree(dsmfolder)


if __name__ == '__main__':    
    lidar_patch = 'USGS_LPC_DE_DelawareValley_HD_2015_LAS_2017'
    lidar_patch = 'FL_Peninsular_FDEM_Orange_2018' #orlando
    lidar_patch = 'USGS_LPC_NC_Phase4_Mecklenburg_2016_LAS_2019' #Charllote
    lidar_patch = 'USGS_LPC_TN_ShelbyCo_2017_LAS_2019' #memphis
    lidar_patch = 'USGS_LPC_OH_Columbus_2019' #columbus, OH
    lidar_patch = 'USGS_LPC_IN_MarionCo_2011_LAS_2016' #indianaplis
    lidar_patch = 'USGS_LPC_NV_LasVegas_QL1_2016_LAS_2018' #las vegas
    # lidar_patch = 'USGS_LPC_MO_StLouis_2017_LAS_2018' #St. Louis
    lidar_patch = 'TN_Nashville_2011'#'TN_Nashville_2011' #nashville
    lidar_patch = 'FL_Peninsular_FDEM_Duval_2018' #Jacksonville, FL
    lidar_patch = 'USGS_LPC_UT_Wasatch_L4_2013_LAS_2016' #for Utah, salt lake city
    lidar_patch = 'USGS_LPC_CO_SoPlatteRiver_Lot5_2013_LAS_2015' #denver
    lidar_patch = 'USGS_LPC_DE_DelawareValley_HD_2015_LAS_2017' #delaware county,
    lidar_patch = 'USGS_LPC_DE_DelawareValleyHD_5A_2015_LAS_2017' #delaware county,
    lidar_patch = 'USGS_LPC_CO_Central_Western_2016_LAS_2018' #colorado
    lidar_patch = 'TN_DavidsonCo_1_2022' # Nashville, TN
    lidar_patch = 'USGS_LPC_TX_Central_B1_2017_LAS_2019' #austin, TX
    lidar_patch = 'USGS_LPC_CA_NoCAL_Wildfires_B5a_2018' #Sacramento, CA
    lidar_patch = 'CA_UpperSouthAmerican_Eldorado_2019' #Sacramento, CA 2, second part
    # lidar_patch = 'AZ_MaricopaPinal_1_2020'

    lidar_patch = 'FL_Peninsular_FDEM_Duval_2018' #Jacksonville, FL
    lidar_patch = 'FL_HillsboroughCo_2007' #Tampa, FL

    # it is interesting, for the flatten state, Albers projection it 
    # is easy to find the ft epsg code
    epsg_code = '2264' #for North Carolina
    epsg_code = '2274' # for memphis, TN
    epsg_code = '3735' # for Columbus, south Ohio
    epsg_code = '2965' # for indianapolis, IN
    epsg_code = '3421' # for Las Vegas, East Nevada
    epsg_code = '2274' # for Nashville, TN
    epsg_code = '2236' # for Florida East
    epsg_code = '3560' # for Salt Lake City, Utah
    epsg_code = '2231' # for Colorado North
    epsg_code = '2272' # for delaware county, pa
    epsg_code = '2272' # for delaware county, 5A, pa, extension
    epsg_code = '3505' # for colorado
    epsg_code = '2274' #for nashville, tn, should use ft as the unit not meter
    epsg_code = '2279' #for Austin, TX, south texas
    epsg_code = '2226' #for Sacramento, CA
    # epsg_code = '2868' # for Pheonix, AZ

    epsg_code = '2236' # for Florida East, jacksonville, tampa

    # some areas need more than one patch

    lidar_patchs = ['FL_Peninsular_Lake_2018', 'FL_Peninsular_Volusia_2018', 'FL_Peninsular_FDEM_Orange_2018', 'FL_Peninsular_Seminole_2018', 'USGS_LPC_FL_Upper_Saint_Johns_2017_LAS_2019', 'FL_Peninsular_FDEM_Osceola_2018', 'FL_Peninsular_FDEM_Polk_2018']
    cityname = 'orlando'

    lidar_patchs = ['USGS_LPC_FL_SuwanneeRiver_2017_LAS_2018', 'FL_Peninsular_FDEM_Alachua_2018'] #gainsville
    cityname = 'gainsville'

    lidar_patchs = ['FL_HillsboroughCo_2007', 'FL_PascoCo_2011', 'FL_HillsboroughCo-Lot2_2011']
    cityname = 'tampa'

    lidar_patchs = ['FL_Peninsular_FDEM_Duval_2018', 'FL_Peninsular_FDEM_Clay_2018']
    cityname = 'jacksonville'
    # miamia using pdal-las2dem.py

    epsg_code = '2236' # for Florida East, jacksonville, tampa, orlando


    ## for phila, nj...
    lidar_patchs = ['USGS_LPC_DE_DelawareValley_HD_2015_LAS_2017']
    epsg_code = '2272'
    cityname = 'phila_nj'



    # root = r'/data/shade-energy/data/'+lidar_patch
    # root = r'/home/tul69181/research/shade-energy/data/' + lidar_patch
    # root = r'/home/tul69181/research/thermal-env/data/' + lidar_patch
    root = r'/home/tul69181/research/thermal-env/data/florida/' + cityname # for florida, heat expo pedestrians
    root = r'/home/tul69181/research/thermal-env/data/florida/'

    
    root = r'/mnt/f/heat-mitigation/data/'

    # usgs_pdal_dsm(lidar_patchs, root, cityname, epsg_code)
    fill_desm(lidar_patchs, root, cityname)