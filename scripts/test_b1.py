from osgeo import gdal,osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *

work_folder = "../result/"
work_folder += "40" + "/"
source_folder = "../uploads"
sentinel_file = source_folder + "/citra/"
shp_file = source_folder + "/area/"
clipped_file = ""
grid_file = ""
raster_tahun_tanam = ""
kode_area = "18"

null_value = -9999
format_file = "GTiff"
pixel_size = 10.0

vector_path = "D:/Indra/Tesis/Ngoprek6/Basemap/Best Agro/SPLIT"
sentinel_file = "C:/xampp/htdocs/pkt/uploads/citra/18/S2B_MSIL2A_20190822_bestagro B1_super_resolved.tif"

for id in range(1,177,1):
	shp_file = vector_path + "/id_" + str(id) + ".gpkg"
	clipped_file = vector_path + "/id_" + str(id) + ".tif"	

	warp_opts = gdal.WarpOptions(
	    format=format_file,
	    cutlineDSName=shp_file,
	    cropToCutline=True,
	    dstNodata=null_value,
	    xRes=pixel_size,
	    yRes=pixel_size,
	)
	gdal.Warp(clipped_file, sentinel_file, options=warp_opts)

print("DONE!")