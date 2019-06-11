from osgeo import gdal,osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
from PIL import Image
from rasterstats import zonal_stats
from pyproj import Proj,transform
import json

null_value = -9999

def SaveDataToTiff(nama_raster,arraydata,g):
	driver = gdal.GetDriverByName("GTiff")
	ds = driver.Create(nama_raster, g.RasterXSize, g.RasterYSize, 1, g.GetRasterBand(1).DataType)
	CopyDatasetInfo(g,ds)
	bandOut=ds.GetRasterBand(1)
	bandOut.SetNoDataValue(null_value)
	BandWriteArray(bandOut, arraydata)

def SaveDataToPNG(nama_raster,arraydata,cols,rows):
	pilImage = Image.frombuffer("RGBA",(cols, rows),arraydata,"raw","RGBA",0,1)
	pilImage.save(nama_raster)

def SaveStatsToGeojsonString(shp_file,nama_raster,prefix,json_data,p1,p2):
	stats_text = "count min mean max sum"
	stats_array = stats_text.split()
	stats_set = frozenset(stats_array)
	stats = zonal_stats(shp_file, nama_raster, stats=stats_text, geojson_out=True, prefix=prefix)

	blank_json_data = False

	if not json_data:
		json_data = {}
		json_data["type"] = "FeatureCollection"
		json_data["features"] = []
		blank_json_data = True

	for idx,item in enumerate(stats):
		if blank_json_data:
			temp_item = {}
			for key in item.keys():
				if key != "geometry":
					temp_item[key] = item[key]
				else:
					temp_geom = {}
					item_geom = item[key]
					temp_geom["type"] = item_geom["type"]
					temp_geom["coordinates"] = []
					temp_geom["coordinates"].append([])
					temp_coords = temp_geom["coordinates"][0]
					item_coords = item_geom["coordinates"][0]
					for coord in item_coords:
						xc,yc = transform(p1,p2,coord[0],coord[1])
						temp_geom["coordinates"][0].append([xc,yc])
					temp_item[key] = temp_geom
			json_data["features"].append(temp_item)
		else:
			for key in json_data["features"][idx].keys():
				if key == "properties":
					for propkey in item[key].keys():
						temp_key = propkey.replace(prefix,"")
						if temp_key in stats_set:
							json_data["features"][idx][key][propkey] = item[key][propkey]

		# if blank_json_data: 
			# json_data["features"].append(temp_item)
			# SaveJsonToFile()

	# return json.dumps(json_data)
	return json_data

def SaveJsonToFile(nama_file,json_data):
	with open(nama_file, 'w') as outfile:
		json.dump(json_data, outfile)	

def SaveStatsToGeojson(shp_file,nama_raster,output_geojson,prefix,p1,p2):
	stats = zonal_stats(shp_file, nama_raster, stats="count min mean max sum", geojson_out=True, prefix=prefix)
	json_data = {}
	json_data["type"] = "FeatureCollection"
	json_data["features"] = []
	for item in stats:
		temp_item = {}
		for key in item.keys():
			if key != "geometry":
				temp_item[key] = item[key]
			else:
				temp_geom = {}
				item_geom = item[key]
				temp_geom["type"] = item_geom["type"]
				temp_geom["coordinates"] = []
				temp_geom["coordinates"].append([])
				temp_coords = temp_geom["coordinates"][0]
				item_coords = item_geom["coordinates"][0]
				for coord in item_coords:
					xc,yc = transform(p1,p2,coord[0],coord[1])
					temp_geom["coordinates"][0].append([xc,yc])
				temp_item[key] = temp_geom
		json_data["features"].append(temp_item)

	with open(output_geojson, 'w') as outfile:
		json.dump(json_data, outfile)


