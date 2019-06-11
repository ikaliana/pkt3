def ClassificationValue(val,unsur):
	retval = 0
	if unsur == "N":
		if val > 2.7: retval = 6
		elif val <= 2.7 and val > 2.5: retval = 5
		elif val <= 2.5 and val > 2.3: retval = 4 
		elif val <= 2.3 and val > 2.1: retval = 3 
		elif val <= 2.1 and val > 1.9: retval = 2 
		elif val <= 1.9: retval = 1 
	if unsur == "P":
		if val > 0.17: retval = 6
		elif val <= 0.17 and val > 0.15: retval = 5
		elif val <= 0.15 and val > 0.13: retval = 4 
		elif val <= 0.13 and val > 0.11: retval = 3 
		elif val <= 0.11 and val > 0.09: retval = 2 
		elif val <= 0.09: retval = 1 
	if unsur == "K":
		if val > 1.2: retval = 6
		elif val <= 1.2 and val > 1.0: retval = 5
		elif val <= 1.0 and val > 0.8: retval = 4 
		elif val <= 0.8 and val > 0.6: retval = 3 
		elif val <= 0.6 and val > 0.4: retval = 2 
		elif val <= 0.4: retval = 1 
	if unsur == "Mg":
		if val > 0.26: retval = 6
		elif val <= 0.26 and val > 0.24: retval = 5
		elif val <= 0.24 and val > 0.22: retval = 4 
		elif val <= 0.22 and val > 0.20: retval = 3 
		elif val <= 0.20 and val > 0.18: retval = 2 
		elif val <= 0.18: retval = 1 
	if unsur == "N-Tanah":
		if val > 0.25: retval = 6
		elif val <= 0.25 and val > 0.15: retval = 5
		elif val <= 0.15 and val > 0.12: retval = 4 
		elif val <= 0.12 and val > 0.08: retval = 3 
		elif val <= 0.08 and val > 0.04: retval = 2 
		elif val <= 0.04: retval = 1 
	if unsur == "P-Tanah":
		if val > 60: retval = 6
		elif val <= 60 and val > 40: retval = 5
		elif val <= 40 and val > 25: retval = 4 
		elif val <= 25 and val > 10: retval = 3 
		elif val <= 10 and val > 5: retval = 2 
		elif val <= 5: retval = 1 
	if unsur == "K-Tanah":  		# this value in PPM or mg/kg. To convert from cmol/kg, just multiply by 390 (weight of K = 39)
		if val > 117: retval = 6
		elif val <= 117 and val > 97.5: retval = 5
		elif val <= 97.5 and val > 78: retval = 4 
		elif val <= 78 and val > 31.2: retval = 3 
		elif val <= 31.2 and val > 16: retval = 2 
		elif val <= 16: retval = 1 


	return retval	

def ClassificationValue2(prev_val,new_val):
	retval = 0
	tempval = ((new_val - prev_val) / prev_val) * 100.00
	if tempval < 0: tempval = 0
	if tempval >= 0 and tempval <= 50: retval = 3
	elif tempval > 50 and tempval <= 100: retval = 2
	elif tempval > 100: retval = 1
	elif tempval < 0 and tempval >= -50: retval = 4
	elif tempval < -50 and tempval >= -100: retval = 5
	elif tempval < -100: retval = 6

	return retval

def CalculateDosisPupuk(nama_unsur,critical_value,current_value,prev_value,komposisi_value):
	retval = 0
	if current_value == 0: return 0
	
	kode_unsur = nama_unsur[:1]
	if kode_unsur not in ["N","P","K"]: kode_unsur = nama_unsur[:2]

	if (nama_unsur.replace(kode_unsur,"")) == "": 			# perhitungan pupuk berdasarkan nutrisi daun
		retval = ( critical_value / current_value ) * prev_value
	else:								# perhitungan pupuk berdasarkan nutrisi tanah
		# R = 2 							# radius perakaran: 2 m (TM) / 1 m (TBM)
		# L = math.pi * math.pow(R,2) 	# luas area perakaran 
		# L = 1 * L 						# asumsi dalam 1 pixel ada 4 area perakaran --> jadinya pake 1 lingkaran
		# D = 0.2 	#0.6 				# kedalamanan perakaran: 0.2 m
		# BV = 1000  						# Berat jenis tanah. asumsi = 1000 kg/m3
		# retval = ( critical_value - current_value ) *  L * D * BV
		# if retval <= 0: retval = 0
		# retval = retval * 100 / komposisi_value	
		L = math.pow(10,2)
		D = 0.2
		BV = 1000
		retval = ( critical_value - current_value )
		if retval <= 0: retval = 0
		else:
			retval = retval * L * D * BV
			if kode_unsur == "N":
				retval = retval / 100
			if kode_unsur == "P":
				retval = retval / 1000000
				retval = retval * 142 / 62
			if kode_unsur == "K":
				retval = retval / 1000000
				retval = retval * 94 / 39
			retval = retval * 100 / komposisi_value
		retval = 0

	return retval

def ClassifyPupuk(data):
	retval = "TUNGGAL"
	count = 0
	if data["N"] != 0: count+=1
	if data["P"] != 0: count+=1
	if data["K"] != 0: count+=1
	if data["Mg"] != 0: count+=1
	if count > 1: retval = "MAJEMUK"

	return retval
