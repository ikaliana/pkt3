from osgeo import gdal,osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
from pyproj import Proj,transform
import numpy as np
import math
import sys
import os
import time
import json
import palettable.cmocean.sequential as c 
import palettable.cubehelix as c1 
import palettable.matplotlib as c2
import palettable.colorbrewer.sequential as c3
# from rasterstats import zonal_stats

# custom library
import gridify
import rasterize
import helper
import dbhelper as db
import savetofile as save

# ==============================================================================================================================

## ==================== VARIABLES  ====================

# kelompok_unsur = ["N", "P", "K", "N-Tanah", "P-Tanah", "K-Tanah"]
kelompok_unsur = ["N", "P", "K", "Mg"]
nama_unsur = { "N" : "Nitrogen", "P" : "Fosfor", "K" : "Kalium", "Mg": "Magnesium", "N-Tanah" : "Nitrogen", "P-Tanah" : "Fosfor", "K-Tanah" : "Kalium" }
null_value = -9999
format_file = "GTiff"
pixel_size = 10.0

class_color = [0x00000000,0xFF0000FF,0xFF2DFFFC,0xFF48FE6A,0xFF30C602,0xFFDCE620,0xFF8F3A12]
class_color_2 = [0x00000000,0xFF1C19D7,0xFF5390F6,0xFF9ADFFF,0xFF9EF0DC,0xFF62CC8A,0xFF41961A]
# data_color = c.Algae_20.hex_colors
# data_color = c.Ice_15.hex_colors[::-1]
# data_color = c1.purple_16.hex_colors[::-1]	#additional '[::-1]' --> reverse the array
# data_color = c2.Viridis_20.hex_colors[::-1]
# data_color = c3.Blues_9.hex_colors
data_color = c.Ice_6.hex_colors[::-1]
data_color_size = np.size(data_color)

critical_value_daun = { "N" : 2.5, "P" : 0.15, "K" : 1.00, "Mg" : 0.24 }
critival_value_tanah = { "N" : 0.25, "P" : 40, "K" : 97.5, "Mg" : 0 }

id_analisis = str(sys.argv[1])

work_folder = "../result/"
if not os.path.isdir(work_folder + id_analisis):
	os.makedirs(work_folder + id_analisis,0o777)
	os.chmod(work_folder + id_analisis,0o777)

work_folder += id_analisis + "/"
source_folder = "../uploads"
sentinel_file = source_folder + "/citra/"
shp_file = source_folder + "/area/"
clipped_file = ""
grid_file = ""
raster_tahun_tanam = ""
unsur_id = {}

# load raster and shape filename and model ID from table Analisis
strquery = ""
strquery += "select kode_model_n,kode_model_p,kode_model_k,kode_model_mg,"
strquery += "kode_model_n_tanah,kode_model_p_tanah,kode_model_k_tanah,"
strquery += "tanggal_pemupukan,persentase_dosis,"
strquery += "a.kode_citra,c.nama_file as citra_file,c.kode_area,ar.nama_file as area_file,c.tanggal as tanggal_citra"
strquery += " from pkt_analisis a"
strquery += " left join pkt_citra c on a.kode_citra = c.kode_citra"
strquery += " left join pkt_area ar on c.kode_area = ar.kode_area"
strquery += " where a.kode_analisis = " + id_analisis
datavar = db.GetData(strquery,True)

#initiate working files
kode_area = datavar["kode_area"]
sentinel_file += str(kode_area) + "/" + datavar["citra_file"]
shp_file += str(kode_area) + "/" + datavar["area_file"][:-4] + ".shp"
clipped_file = work_folder + datavar["citra_file"][:-4] + "_clipped" + datavar["citra_file"][-4:]
grid_file = work_folder + datavar["area_file"][:-4] + "_grid" + ".shp"
raster_tahun_tanam = work_folder + datavar["area_file"][:-4] + "_tahuntanam" + ".tif"
tanggal_citra = datavar["tanggal_citra"]
tanggal_pemupukan = datavar["tanggal_pemupukan"]
persentase_dosis = datavar["persentase_dosis"]

# print "shapefile: ", shp_file
# print "tanggal citra: ", tanggal_citra
# print "tanggal pemupukan: ", tanggal_pemupukan
# print "dosis: ", persentase_dosis
# exit(0)

#initiate model ID
unsur_id["N"] = datavar["kode_model_n"]
unsur_id["P"] = datavar["kode_model_p"]
unsur_id["K"] = datavar["kode_model_k"]
unsur_id["Mg"] = datavar["kode_model_mg"]
# unsur_id["N-Tanah"] = datavar["kode_model_n_tanah"]
# unsur_id["P-Tanah"] = datavar["kode_model_p_tanah"]
# unsur_id["K-Tanah"] = datavar["kode_model_k_tanah"]

#initiate fertilizer composition
komposisi_pupuk = {}
# datapupuk = GetData("select * from pkt_pupuk",False)
datapupuk = db.GetData("select * from pkt_pupuk where kode_pupuk in (select distinct kode_pupuk from pkt_rekomendasi)",False)
for row in datapupuk:
	temp = {}
	temp["N"] = float(row["komposisi_n"])
	temp["P"] = float(row["komposisi_p"])
	temp["K"] = float(row["komposisi_k"])
	temp["Mg"] = float(row["komposisi_mg"])
	temp["ID"] = row["kode_pupuk"]
	temp["JENIS"] = helper.ClassifyPupuk(temp)
	komposisi_pupuk[row["nama_pupuk"]] = temp

# print komposisi_pupuk
# exit(0)

#initiate data rekomendasi pupuk PPKS
rekomendasi_pupuk = {}
strquery = ""
strquery += "select p.nama_pupuk,r.* from pkt_rekomendasi r "
strquery += "left join pkt_pupuk p on r.kode_pupuk = p.kode_pupuk "
strquery += "order by p.nama_pupuk,r.umur_tanaman"
datarekomendasi = db.GetData(strquery,False)

temp_nama = ""
for row in datarekomendasi:
	if temp_nama != row["nama_pupuk"]:
		rekomendasi_pupuk[row["nama_pupuk"]] = {}
		temp = rekomendasi_pupuk[row["nama_pupuk"]]
	temp_nama = row["nama_pupuk"]
	temp[row["umur_tanaman"]] = row["jumlah_pupuk"] 

#initiate data riwayat pupuk
riwayat_pupuk = {}
strquery = ""
strquery += "select p.nama_pupuk,r.kode_pupuk,r.tahun,r.dosis_pupuk "
strquery += "from pkt_riwayat r left join pkt_pupuk p on r.kode_pupuk = p.kode_pupuk "
strquery += "where r.kode_area = " + str(kode_area) + " "
strquery += "order by p.nama_pupuk,r.tahun "
datariwayat = db.GetData(strquery,False)

if datariwayat is not None:
	temp_nama = ""
	for row in datariwayat:
		if temp_nama != row["nama_pupuk"]:
			riwayat_pupuk[row["nama_pupuk"]] = {}
			temp = riwayat_pupuk[row["nama_pupuk"]]
		temp_nama = row["nama_pupuk"]
		temp[row["tahun"]] = row["dosis_pupuk"] 

# print work_folder
# print sentinel_file
# print shp_file
# print clipped_file
# print unsur_id
# print komposisi_pupuk
# print rekomendasi_pupuk
# print(riwayat_pupuk)
# exit()
print("Init variables done")

## ========== CLIP RASTER WITH SHAPEFILE  ====================

warp_opts = gdal.WarpOptions(
    format=format_file,
    cutlineDSName=shp_file,
    cropToCutline=True,
    dstNodata=null_value,
    xRes=pixel_size,
    yRes=pixel_size,
)
gdal.Warp(clipped_file, sentinel_file, options=warp_opts)
#cari opsi lain buat clip raster (lihat di sample GDAL di internet). bbrp titik hasilnya meleset
print("Clip raster done")
# exit()

## ========== CREATE GRID FILE  ====================

gridify.GenerateGrid(shp_file,grid_file)
print("Generate grid area done")

## ========== CREATE RASTER OF TahunTanam  ====================

field_name = "TahunTanam"

rasterize.VectorToRaster(pixel_size,null_value,shp_file,raster_tahun_tanam,field_name)
# exit()
print("Generate raster of TahunTanam done")

## ========== LOAD RASTER AND ITS BAND  ====================

g = gdal.Open(clipped_file)
rows = g.RasterYSize
cols = g.RasterXSize
# print rows,cols
x1, xres, xskew, y2, yskew, yres = g.GetGeoTransform()
x2 = x1 + g.RasterXSize * xres
y1 = y2 + g.RasterYSize * yres
prj = g.GetProjection()
srs = osr.SpatialReference(wkt=prj)
crs = srs.GetAttrValue("AUTHORITY",1)

p1 = Proj(init="epsg:"+crs)
p2 = Proj(init="epsg:4326")
x3,y3 = transform(p1,p2,x1,y1)
x4,y4 = transform(p1,p2,x2,y2)

#-- SAVE RASTER METADATA TO JSON FILE
raster_metadata = { "x1_original": x1 , "y1_original": y1, "x2_original": x2, "y2_original": y2, 
					"x1_4326": x3 , "y1_4326": y3, "x2_4326": x4, "y2_4326": y4, 
					"crs": crs }
with open(work_folder + "raster_metadata.json", 'w') as outfile:
		    json.dump(raster_metadata, outfile)

# --- LOAD RASTER DATA FOR EACH BAND --- #
band1 = BandReadAsArray(g.GetRasterBand(1))  	#Band 1
band2 = BandReadAsArray(g.GetRasterBand(2))		#Band 2
band3 = BandReadAsArray(g.GetRasterBand(3))		#Band 3
band4 = BandReadAsArray(g.GetRasterBand(4))		#Band 4
band5 = BandReadAsArray(g.GetRasterBand(5))		#Band 5
band6 = BandReadAsArray(g.GetRasterBand(6))		#Band 6
band7 = BandReadAsArray(g.GetRasterBand(7))		#Band 7
band8 = BandReadAsArray(g.GetRasterBand(8))		#Band 8
band8a = BandReadAsArray(g.GetRasterBand(9))	#Band 8A
band9 = BandReadAsArray(g.GetRasterBand(10))	#Band 9
band11 = BandReadAsArray(g.GetRasterBand(11))	#Band 11
band12 = BandReadAsArray(g.GetRasterBand(12))	#Band 12

# print(band3)
# exit()

# ---- LOAD TAHUN TANAM RASTER
g2 = gdal.Open(raster_tahun_tanam)
rows2 = g2.RasterYSize
cols2 = g2.RasterXSize
tahun_tanam_data = BandReadAsArray(g2.GetRasterBand(1)) 


## ========== INITIALIZE CALCULATION PLACEHOLDER  ====================

model = {}
raster_unsur = {}
raster_unsur_class = {}
raster_unsur_color = {}
pupuk = {}
luas_area = 0

for nama_pupuk in komposisi_pupuk:
	pupuk[nama_pupuk] = {}
	pupuk[nama_pupuk]["unsur_terpilih"] = ""

	for unsur in kelompok_unsur:
		temp = {}
		kode_unsur = unsur[:1]
		if kode_unsur not in ["N","P","K"]: kode_unsur = unsur[:2]
		temp["komposisi"] = komposisi_pupuk[nama_pupuk][kode_unsur]
		temp["peta_prev"] = np.empty((cols, rows),np.float32)
		temp["peta_prev"].shape=rows, cols
		temp["peta_dosis"] = np.empty((cols, rows),np.float32)
		temp["peta_dosis"].shape=rows, cols
		# temp["peta_dosis_warna"] = np.empty((cols, rows),np.uint32)
		# temp["peta_dosis_warna"].shape=rows, cols
		temp["peta_warna"] = np.empty((cols, rows),np.uint32)
		temp["peta_warna"].shape=rows, cols
		temp["peta_warna2"] = np.empty((cols, rows),np.uint32)
		temp["peta_warna2"].shape=rows, cols
		temp["dosis"] = 0.0
		pupuk[nama_pupuk][unsur] = temp;

## ========== GET MODEL FROM DATABASE  ====================
# --- LOOP FOR EACH UNSUR --- #
for unsur in kelompok_unsur:

	model[unsur] = db.GetData('SELECT * FROM pkt_model where id_model=' + str(unsur_id[unsur]),True)

	# --- INITIATE NUMPY ARRAY OF RASTER --- #
	raster_unsur[unsur] = np.empty([rows, cols],np.float64)
	raster_unsur_class[unsur] = np.empty((rows, cols),np.uint32)
	raster_unsur_color[unsur] = np.empty((cols, rows),np.uint32)
	raster_unsur_color[unsur].shape=rows, cols

	# --- PROCESS THE RASTER --- #
	for i in range(rows):
		for j in range(cols):

			tahun_tanam_null = True
			if i < rows2 and j < cols2: tahun_tanam_null = (tahun_tanam_data[i,j] == null_value)

			ndvi_value = (band8[i,j] - band4[i,j]) / (band8[i,j] + band4[i,j]) * 1.000
			is_vegetation = (ndvi_value >= 0.5000)

			# if band1[i,j] != null_value:
			if band1[i,j] != null_value and not tahun_tanam_null and is_vegetation:
				
				luas_area += 1
				tahun_tanam = tahun_tanam_data[i,j]  #ambil data ini dari raster/vector
				# tahun_now = int(tanggal_citra.strftime("%Y"))  #harusnya ngambil dari tanggal sensing citra sentinel
				tahun_now = int(tanggal_pemupukan.strftime("%Y"))  #ambil dari tanggal pemupukan (manual input)
				umur_tanaman = tahun_now - tahun_tanam

				# --- calculate nutrient using model --- #
				raster_unsur[unsur][i,j] = \
					band1[i,j] * model[unsur]["band1"] + band2[i,j] * model[unsur]["band2"] + band3[i,j] * model[unsur]["band3"] \
					+ band4[i,j] * model[unsur]["band4"] + band5[i,j] * model[unsur]["band5"] + band6[i,j] * model[unsur]["band6"] \
					+ band7[i,j] * model[unsur]["band7"] + band8[i,j] * model[unsur]["band8"] + band8a[i,j] * model[unsur]["band8a"] \
					+ band9[i,j] * model[unsur]["band9"] + band11[i,j] * model[unsur]["band11"] + band12[i,j] * model[unsur]["band12"] \
					+ (band1[i,j]**2) * model[unsur]["band1_2"] + (band2[i,j]**2) * model[unsur]["band2_2"] \
					+ (band3[i,j]**2) * model[unsur]["band3_2"] + (band4[i,j]**2) * model[unsur]["band4_2"] \
					+ (band5[i,j]**2) * model[unsur]["band5_2"] + (band6[i,j]**2) * model[unsur]["band6_2"] \
					+ (band7[i,j]**2) * model[unsur]["band7_2"] + (band8[i,j]**2) * model[unsur]["band8_2"] \
					+ (band8a[i,j]**2) * model[unsur]["band8a_2"] + (band9[i,j]**2) * model[unsur]["band9_2"] \
					+ (band11[i,j]**2) * model[unsur]["band11_2"] + (band12[i,j]**2) * model[unsur]["band12_2"] \
					+ model[unsur]["constant"] 
				
				# --- make it non negative value --- #
				if raster_unsur[unsur][i,j] < 0: raster_unsur[unsur][i,j] = 0
				# if pupuk[nama_pupuk][unsur]["komposisi"] = 0: raster_unsur[unsur][i,j] = 0

				# --- classify the nutrient value --- #
				raster_unsur_class[unsur][i,j] = helper.ClassificationValue(raster_unsur[unsur][i,j],unsur)

				for nama_pupuk in komposisi_pupuk:
					data_pupuk = pupuk[nama_pupuk][unsur]
					if data_pupuk["komposisi"] > 0:
						
						#Get Last year dosage value. If none, use PPKS recommendation value
						# data_pupuk["peta_prev"][i,j] = rekomendasi_pupuk[nama_pupuk] / 100.0
						riwayat_data_pupuk = False
						if nama_pupuk in riwayat_pupuk:
							if (tahun_now-1) in riwayat_pupuk[nama_pupuk]:
								data_pupuk["peta_prev"][i,j] = riwayat_pupuk[nama_pupuk][(tahun_now-1)] / 100.0
								riwayat_data_pupuk = True

						if not riwayat_data_pupuk:
							data_pupuk["peta_prev"][i,j] = rekomendasi_pupuk[nama_pupuk][umur_tanaman] / 100.0

						kode_unsur = unsur[:1]
						if kode_unsur not in ["N","P","K",""]: kode_unsur = unsur[:2]
						crValue = critival_value_tanah[kode_unsur]
						if (unsur.replace(kode_unsur,"")) == "": crValue = critical_value_daun[unsur]
						# print(kode_unsur,": ",crValue)

						data_pupuk["peta_dosis"][i,j] = helper.CalculateDosisPupuk(unsur,crValue,raster_unsur[unsur][i,j],data_pupuk["peta_prev"][i,j],komposisi_pupuk[nama_pupuk][kode_unsur])

						#update on 2019, Feb 26. Total dosis dikalikan persentase penerapan dosis pupuk 
						data_pupuk["peta_dosis"][i,j] = (persentase_dosis/100.000) * data_pupuk["peta_dosis"][i,j]

						#temporary solution: sampe model Mg bisa digunakan dengan akurasi tinggi
						if komposisi_pupuk[nama_pupuk]["JENIS"] == "MAJEMUK" and unsur == "Mg": 
							data_pupuk["peta_dosis"][i,j] = 0.0


						data_pupuk["peta_warna"][i,j] = helper.ClassificationValue2(data_pupuk["peta_prev"][i,j],data_pupuk["peta_dosis"][i,j])
						# data_pupuk["peta_warna"][i,j] = class_color_2[ data_pupuk["peta_warna"][i,j] ]
						data_pupuk["peta_warna2"][i,j] = class_color_2[ data_pupuk["peta_warna"][i,j] ]
						data_pupuk["dosis"] += data_pupuk["peta_dosis"][i,j]
					else:
						data_pupuk["peta_prev"][i,j] = null_value
						data_pupuk["peta_dosis"][i,j] = 0
						data_pupuk["peta_warna"][i,j] = 0
						data_pupuk["peta_warna2"][i,j] = class_color_2[0]

			else:
				raster_unsur[unsur][i,j] = null_value
				raster_unsur_class[unsur][i,j] = 0

				for nama_pupuk in komposisi_pupuk:
					data_pupuk = pupuk[nama_pupuk][unsur]
					data_pupuk["peta_prev"][i,j] = null_value
					data_pupuk["peta_dosis"][i,j] = null_value
					data_pupuk["peta_warna"][i,j] = 0
					data_pupuk["peta_warna2"][i,j] = class_color_2[0]

			raster_unsur_color[unsur][i,j] = class_color[ raster_unsur_class[unsur][i,j] ]
	# --- END OF PROCESS THE RASTER --- #

	# print(raster_unsur[unsur])

	# --- SAVE TO FILE --- #
	nama_raster = work_folder + "Citra_Unsur_" + unsur + ".tif"
	save.SaveDataToTiff(nama_raster,raster_unsur[unsur],g)

	nama_raster = work_folder + "Citra_Klasifikasi_" + unsur + ".png"
	save.SaveDataToPNG(nama_raster,raster_unsur_color[unsur].tostring(),cols,rows)

	for nama_pupuk in komposisi_pupuk:
		nama_raster = work_folder + "Citra_Pupuk_" + nama_pupuk + "_" + unsur + ".tif"
		save.SaveDataToTiff(nama_raster,pupuk[nama_pupuk][unsur]["peta_dosis"],g)

		# nama_raster = "Citra_Klasifikasi_Pupuk_" + nama_pupuk + "_" + unsur + ".png"
		# pilImage = Image.frombuffer("RGBA",(cols, rows),pupuk[nama_pupuk][unsur]["peta_warna"].tostring(),"raw","RGBA",0,1)
		# pilImage.save(nama_raster)

# --- END LOOP FOR EACH UNSUR --- #

area_hektar = (luas_area/len(kelompok_unsur))/100.00
# print("Luas area: ", round(area_hektar,2))

sql = "DELETE FROM pkt_analisis_detail WHERE kode_analisis = %s;"
data = (int(id_analisis),)
db.ExecuteQuery(sql,data,True,False)

# --- LOOP FOR EACH PUPUK, HITUNG TOTAL DOSIS UMUM --- #
# print komposisi_pupuk
for nama_pupuk in komposisi_pupuk:
	unsur_terpilih = ""
	temp_berat = 9999999
	json_pupuk_blok = {}

	jenis_pupuk = komposisi_pupuk[nama_pupuk]["JENIS"]
	kode_pupuk = komposisi_pupuk[nama_pupuk]["ID"]

	for unsur in kelompok_unsur:
		data_pupuk = pupuk[nama_pupuk][unsur]

		if data_pupuk["dosis"] != 0:
			if temp_berat > data_pupuk["dosis"]:
				temp_berat = data_pupuk["dosis"]
				unsur_terpilih = unsur

		dosis_total = data_pupuk["dosis"]
		dosis_hektar = dosis_total / area_hektar * 1.0
		dosis_pohon = dosis_hektar / 136

		print(nama_pupuk,"\t",jenis_pupuk,"\t",unsur,"\t",round(dosis_total,2),"\t",round(dosis_hektar,2),"\t",round(dosis_pohon,2))
		
		sql = "INSERT INTO pkt_analisis_detail (kode_analisis,kode_pupuk,nama_pupuk,jenis_pupuk,nama_unsur,"
		sql += "dosis_total,dosis_hektar,dosis_pohon) VALUES "
		sql += "(%s,%s,%s,%s,%s,%s,%s,%s)"
		data = (int(id_analisis),kode_pupuk,nama_pupuk,jenis_pupuk,unsur,dosis_total,dosis_hektar,dosis_pohon,)
		db.ExecuteQuery(sql,data,True,False)

		# Create fertilizer stats based on BLOK and nutrient, save it to temporary data
		nama_raster = work_folder + "Citra_Pupuk_" + nama_pupuk + "_" + unsur + ".tif"
		# json_pupuk_blok = json.loads(SaveStatsToGeojsonString(shp_file, nama_raster, unsur + "_", json_pupuk_blok))
		json_pupuk_blok = save.SaveStatsToGeojsonString(shp_file, nama_raster, unsur + "_", json_pupuk_blok,p1,p2)
		# SaveJsonToFile(work_folder + "Data_Blok_Pupuk_" + nama_pupuk + "_" + unsur + ".geojson",json_pupuk_blok)

	# --- Create Fertilizer stats based on BLOK and save it to Geojson file --- #
	save.SaveJsonToFile(work_folder + "Data_Blok_Pupuk_" + nama_pupuk + ".geojson",json_pupuk_blok)

	if unsur_terpilih != "":
		pupuk[nama_pupuk]["unsur_terpilih"] = unsur_terpilih
		print("Unsur terpilih: ", unsur_terpilih)

		# --- SAVE SELECTED FERTILIZER DATA TO PNG FILE --- #
		nama_raster = work_folder + "Citra_Pupuk_" + nama_pupuk + ".tif"
		save.SaveDataToTiff(nama_raster,pupuk[nama_pupuk][unsur_terpilih]["peta_dosis"],g)


		# --- Create Fertilizer stats based on GRID file and save it to Geojson file --- #
		save.SaveStatsToGeojson(grid_file, nama_raster, work_folder + "Data_Grid_Pupuk_" + nama_pupuk + ".geojson","",p1,p2)


		# --- SAVE SELECTED FERTILIZER DOSAGE DATA TO PNG FILE --- #
		# nama_raster = work_folder + "Citra_Dosis_Pupuk_Percent_" + nama_pupuk + ".tif"
		# SaveDataToTiff(nama_raster,pupuk[nama_pupuk][unsur_terpilih]["peta_warna"],g)
		nama_raster = work_folder + "Citra_Dosis_Pupuk_" + nama_pupuk + ".png"
		save.SaveDataToPNG(nama_raster,pupuk[nama_pupuk][unsur_terpilih]["peta_warna2"].tostring(),cols,rows)

		
		# --- Classify fertilizer data and save to PNG --- #
		data_dosis = pupuk[nama_pupuk][unsur_terpilih]["peta_dosis"]
		dosis_max = np.ceil(np.amax(np.extract(data_dosis>=0,data_dosis)))
		# print "dosis max: ", dosis_max
		range_max = 1000
		for i in range(8,0,-1):
			if dosis_max <= (data_color_size * i): range_max = data_color_size * i 
		if dosis_max <= (data_color_size/2): range_max = data_color_size/2

		divider = range_max / (data_color_size * 1.0) #20.0
		range_value = np.arange(0,range_max+(divider/2.0),divider)

		raster_data = np.empty((cols, rows),numpy.uint32)
		raster_data.shape=rows, cols

		for i in range(rows):
			for j in range(cols):

				if data_dosis[i,j] != null_value:
					dosis_val = data_dosis[i,j]
					idx = range_value.searchsorted(dosis_val,'right')-1
					# if idx > 14: idx = 14
					if idx > (data_color_size-1): idx = (data_color_size-1)
					if idx < 0: idx = 0
					color_val = data_color[idx]
					color_val_new = '0xFF' + color_val[5:7] + color_val[3:5] + color_val[1:3] 
					raster_data[i,j] = eval(color_val_new)
				else:
					raster_data[i,j] = 0x00000000

		nama_raster = work_folder + "Citra_Klasifikasi_Pupuk_" + nama_pupuk + ".png"
		save.SaveDataToPNG(nama_raster,raster_data.tostring(),cols,rows)

		dosis_pupuk_meta = {}
		dosis_pupuk_meta["max"] = str(dosis_max)
		dosis_pupuk_meta["range"] = ",".join(range_value.astype(str));
		dosis_pupuk_meta["color"] = ",".join(data_color);
		save.SaveJsonToFile(work_folder + "Data_Klasifikasi_Pupuk_" + nama_pupuk + ".geojson",dosis_pupuk_meta)
		# print(dosis_pupuk_meta)


		# --- Calculate Fertilizer ideal for each BLOK area based on unsur terpilih ---- #
		json_file_name = work_folder + "Data_Blok_Pupuk_" + nama_pupuk + ".geojson"
		with open(json_file_name) as json_file:  
			json_data_all = json.load(json_file)
			for feature in json_data_all["features"]:
				data = feature["properties"]
				data_terpilih = data[unsur_terpilih + "_sum"]
				if data_terpilih is None: data_terpilih = 0

				N_sum = data["N_sum"] if data["N_count"] > 0 else 0
				P_sum = data["P_sum"] if data["P_count"] > 0 else 0
				K_sum = data["K_sum"] if data["K_count"] > 0 else 0
				Mg_sum = data["Mg_sum"] if data["Mg_count"] > 0 else 0

				N_ideal = N_sum if unsur_terpilih == "N" else (N_sum - data_terpilih)
				if N_ideal < 0: N_ideal = 0
				data["N_ideal"] = N_ideal

				P_ideal = P_sum if unsur_terpilih == "P" else (P_sum - data_terpilih)
				if P_ideal < 0: P_ideal = 0
				data["P_ideal"] = P_ideal

				K_ideal = K_sum if unsur_terpilih == "K" else (K_sum - data_terpilih)
				if K_ideal < 0: K_ideal = 0
				data["K_ideal"] = K_ideal

				Mg_ideal = Mg_sum if unsur_terpilih == "Mg" else (Mg_sum - data_terpilih)
				if Mg_ideal < 0: Mg_ideal = 0
				data["Mg_ideal"] = Mg_ideal

				data["Unsur_Terpilih"] = unsur_terpilih
				data["komposisi_n"] = komposisi_pupuk[nama_pupuk]["N"]
				data["komposisi_p"] = komposisi_pupuk[nama_pupuk]["P"]
				data["komposisi_k"] = komposisi_pupuk[nama_pupuk]["K"]

			save.SaveJsonToFile(json_file_name,json_data_all)


sql = "DELETE FROM pkt_analisis_summary WHERE kode_analisis = %s;"
data = (int(id_analisis),)
db.ExecuteQuery(sql,data,True,False)

sql = "INSERT INTO pkt_analisis_summary (kode_analisis,last_process,status_process,err_message,luas_area) "
sql += "VALUES (%s,now(),'OK','',%s)"
data = (int(id_analisis),area_hektar)
db.ExecuteQuery(sql,data,True,False)

sql = "UPDATE pkt_analisis SET status=True WHERE kode_analisis=%s"
data = (int(id_analisis),)
db.ExecuteQuery(sql,data,True,False)


print("DONE")