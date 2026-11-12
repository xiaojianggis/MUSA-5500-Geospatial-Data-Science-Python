### This code is used to convert the LAS files into raster using ArcPy and
## the LAS tools in ArcGIS
## First vision May 8, 2020
## modified by Xiaojiang Li, on July 31, 2021 add the project specifiecation 
## when creating the LAS dataset
import arcpy
import os, os.path
from arcpy import env

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('3D')
root = r'F:\Xiaojiang\lidar-us\Houston'

# the output basename tif
demroot = os.path.join(root, 'dem-m')
if not os.path.exists(demroot): os.mkdir(demroot)
dsmroot = os.path.join(root, 'dsm-m')
if not os.path.exists(dsmroot): os.mkdir(dsmroot)


# loop all the zip files and extract as .las then convert to DSM/DEM
lasroot = r'F:\Xiaojiang\lidar-us\Houston\las'


for laszip in os.listdir(lasroot):
    laszipfile = os.path.join(lasroot, laszip)
    basename = os.path.splitext(laszip)
    if not basename.endswith('.las'): continue
    print('process', basename)
    base = basename[0]
    
    demtif = os.path.join(demroot, base + '.tif')
    dsmtif = os.path.join(dsmroot, base + '.tif')
    
    lasdroot = os.path.join(root, 'lasd')
    if not os.path.exists(lasdroot): os.mkdir(lasdroot)
    lasdpath = os.path.join(lasdroot, base+'.lasd')
    
    if os.path.exists(demtif): continue
    
    lasfile = os.path.join(lasroot, base + '.las')
    
    demLyr = arcpy.CreateUniqueName('dem')
    dsmLyr = arcpy.CreateUniqueName('dsm')
    
    # first step is to create las dataset, the wkt can be found from the ArcGIS LAS data creation function
    wkt = "PROJCS['NAD_1983_StatePlane_Texas_South_FIPS_4205_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',984250.0],PARAMETER['False_Northing',16404166.66666666],PARAMETER['Central_Meridian',-98.5],PARAMETER['Standard_Parallel_1',26.16666666666667],PARAMETER['Standard_Parallel_2',27.83333333333333],PARAMETER['Latitude_Of_Origin',25.66666666666667],UNIT['Foot_US',0.3048006096012192]],VERTCS['NAVD88 height',VDATUM['North American Vertical Datum 1988'],UNIT['Foot_US',0.3048006096012192]]"
    sr = arcpy.SpatialReference()
    sr.loadFromString(wkt)
    arcpy.CreateLasDataset_management(lasfile, lasdpath, "NO_RECURSION", "", sr)
    
    # make a las dataset
    lasLyr = arcpy.CreateUniqueName("TEMP")
    arcpy.management.MakeLasDatasetLayer(lasdpath, lasLyr, 2, 'Last Return') #DEM
    
    # Execute LasDatasetToRaster
    arcpy.conversion.LasDatasetToRaster(lasLyr, demtif, 'ELEVATION',
                              'BINNING AVERAGE LINEAR', 'FLOAT', 'CELLSIZE', 3, 1)
    
    # for the DSM
    lasLyr = arcpy.CreateUniqueName("TEMP")
    arcpy.management.MakeLasDatasetLayer(lasdpath, lasLyr) #DSM
    
    # Execute LasDatasetToRaster
    arcpy.conversion.LasDatasetToRaster(lasLyr, dsmtif, 'ELEVATION',
                              'BINNING Maximum LINEAR', 'FLOAT', 'CELLSIZE', 3, 1) #Using maximum for DSM
    
    
#     # delete the las file
# ##    os.remove(os.path.join(root, lasfile))
# ##    os.remove(os.path.join(root, base + '.xml'))

print('You are done')

