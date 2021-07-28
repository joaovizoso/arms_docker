import tesserocr as tr
from PIL import Image
from pathlib import Path
import json 
import docManager

TESSDATA_PATH = str(Path.cwd().parents[0]/'tessdata')

def ocr(name,langs,batch_name):
	path = Path.cwd()/"tmp"/batch_name/name/"regions"
	regions = get_data(name,batch_name)
	lang = docManager.parse_langs(langs)
	pages_left = docManager.get_field(batch_name,name,'ocr')

	for i in range(pages_left,0,-1):
		page = "page_{}.tiff".format(i)
		for elem in regions:
			if elem['image'] == page:
				nr_regions = len(elem['regions'])

		for h in range(nr_regions,0,-1):
			image = path/"page_{}_{}.tiff".format(i,h)
			img = Image.open(image)	
			with tr.PyTessBaseAPI(path=TESSDATA_PATH, lang=lang, psm=tr.PSM.SINGLE_LINE) as api:
				api.SetImage(img)
				text = api.GetUTF8Text().replace("\n","").split()
				conf = api.AllWordConfidences()
				update_field(name,str(image),"text",text,batch_name)
				update_field(name,str(image),"word_conf",conf,batch_name)

		docManager.update_field(batch_name,name,'ocr',(i-1))
	

		

def update_data(name,data,batch_name):
	path = Path.cwd()/"tmp"/batch_name/name/"regions"/"regions.JSON"
	with open(path,'w') as file:
		json.dump(data,file)


def get_data(name,batch_name):
	path = Path.cwd()/"tmp"/batch_name/name/"regions"/"regions.JSON"
	with open(path,"rb") as file:
		data = json.load(file)
		return data

def update_field(name,image,field,value,batch_name):
	data = get_data(name,batch_name)

	for element in data:
		for region in element['regions']:
			if region['filename'] == image:
				in1 = data.index(element)
				in2 = data[in1]['regions'].index(region)
				data[in1]['regions'][in2][field] = value

	update_data(name,data,batch_name)
	
