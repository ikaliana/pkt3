from PIL import Image

def GenerateDownloadableImage(unsur,source,target,legend):
	max_pixel_size = 960
	pic_padding = 50
	double_pic_padding = pic_padding * 2
	# nama_raster_legend = "Legend_Unsur_" + unsur + ".png"

	img = Image.open(source)
	curwidth,curheight = img.size

	imgWidth = max_pixel_size
	imgHeight = max_pixel_size

	if curwidth > curheight:
		imgWidth = max_pixel_size
		imgHeight = ( (curheight/curwidth) * 1.0000 ) * max_pixel_size 
	else:
		imgHeight = max_pixel_size
		imgWidth = ( (curwidth/curheight) * 1.00000 ) * max_pixel_size

	newsize = (int(imgWidth), int(imgHeight))
	imgr = img.resize(newsize)

	imgl = Image.open(legend)
	lwidth,lheight = imgl.size

	canvas_width = pic_padding + int(imgWidth) + pic_padding + lwidth + pic_padding
	canvas_height = pic_padding + int(imgHeight) + pic_padding + lheight + pic_padding
	canvas_size = (canvas_width, canvas_height)

	canvas = Image.new("RGBA",canvas_size,(255,255,255))
	canvas.paste(imgr,(pic_padding,pic_padding))
	canvas.paste(imgl,(int(imgWidth)+double_pic_padding,pic_padding))
	canvas.save(target)

# unsur = "N"
# nama_raster = "Citra_Klasifikasi_" + unsur + ".png"
# nama_raster_resize = "Citra_Klasifikasi_" + unsur + "_copy.png"

# GenerateDownloadableImage(nama_raster,nama_raster_resize,unsur)

