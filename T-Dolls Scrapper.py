from bs4 import BeautifulSoup

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import urllib.request
import requests
import re#gex
import os

#####

web_url = 'https://en.gfwiki.com/wiki/T-Doll_Index'

def download_image(url, path): # https://stackoverflow.com/questions/30229231
	img_data = requests.get(url).content;
	with open(path, 'wb') as handler:
		handler.write(img_data);

#####

font_name = ImageFont.truetype("timesbd.ttf", 30);
font_number = ImageFont.truetype("cour.ttf", 32);

url_ref = urllib.request.urlopen(web_url);
html_bytearray = url_ref.read();

html_str = html_bytearray.decode('utf8');
url_ref.close();

soup = BeautifulSoup(html_str, 'html.parser');

html_sub1 = soup.find('div', {'class':'mw-content-ltr'});
html_sub2 = html_sub1.find_all('div', {'class':'card-bg-small', 'style':'display:inline-block'});

leg_offset = 0;
count = 1;

final_dir = "./Girls Frontline";
if not os.path.exists(final_dir):
	os.makedirs(final_dir);

for div in html_sub2:
	href = div.find('div').find('a').get('href');
	name = div.find('div').find('a').get('title');

	doll_webpage = 'https://en.gfwiki.com' + href;
	print(count,'|| Tactical doll', name, '@', doll_webpage);

	#Getting lower data
	
	doll_url_ref = urllib.request.urlopen(doll_webpage);
	doll_byte_array = doll_url_ref.read();

	doll_html_str = doll_byte_array.decode('utf8');
	doll_url_ref.close();

	salted_soup = BeautifulSoup(doll_html_str, 'html.parser');

	d_lv1 = salted_soup.find('div', {'id':'mw-content-text'});
	d_lv2 = salted_soup.find('table', {'class':'floatright'}).find_all('img');
	d_lv3 = salted_soup.find('table', {'class':'floatright'}).find_all('span');


	output_path = './out/' + d_lv3[1].text + '_' + name + "/";
	if not os.path.exists(output_path):
		os.makedirs(output_path);

	stars = -1;
	typestr = "UN";
	download_image('https://en.gfwiki.com/images/8/86/Icon_star.png', output_path + '/Star.png');
	download_image(salted_soup.find('table', {'class':'floatright'}).find('img', {'id':'fullart_S'}).get('src'), 
		output_path + 'Illustration.png');
			#download_image(image.get('src'), output_path + name + '_S.png');

	for image in d_lv2:
		ipath = os.path.split(image.get('src'));
		iext = os.path.splitext(ipath[1]);

		if (iext[0] == 'Icon_star'):
			stars += 1;

		elif (iext[0].startswith('Infobox_name')):
			download_image(image.get('src'), output_path + '/Infobox.png');
		elif (iext[0].startswith('Infobox_border')):
			download_image(image.get('src'), output_path + '/Border.png');
		elif (re.search(r'Icon_[A-Z]{2}_[0-9]star', iext[0])): # 2 Letters
			download_image(image.get('src'), output_path + '/TypeIcon.png');
			typestr = iext[0][5:-6];
		elif (re.search(r'Icon_[A-Z]{3}_[0-9]star', iext[0])): # 3 Letters
			download_image(image.get('src'), output_path + '/TypeIcon.png');
			typestr = iext[0][5:-6];

	# https://stackoverflow.com/questions/31273592
	images = [
		Image.open(output_path + "/Border.png").convert("RGB"),
		Image.open(output_path + "/Illustration.png").convert("RGBA"),
		Image.open(output_path + "/Infobox.png").convert("RGBA"),
		Image.open(output_path + "/Star.png").convert("RGBA"),
		Image.open(output_path + "/TypeIcon.png").convert("RGBA")
	];

	x_offset = int(images[0].size[1] / 4);
	sqr_size = images[0].size[1];
	padded = d_lv3[1].text.zfill(3);

	im_r = Image.new('RGBA', (sqr_size, sqr_size), (255, 255, 255, 0));
	im_b = Image.new('RGBA', images[0].size, (255, 0, 0, 255));

	# https://stackoverflow.com/questions/5324647
	# https://stackoverflow.com/questions/28407462

	im_r.paste(images[0], (0 + x_offset, 0));
	im_r.paste(images[1], (0 + x_offset, 21), images[1]);
	im_r.paste(images[2], (0 + x_offset, 355), images[2]);
	im_r.paste(images[4], (1 + x_offset, 1), images[4]);

	# Artificial legendaries
	if (stars == 4):
		leg_offset += 1;
		if (leg_offset % 10 == 0):
			stars += 1;
			print("Is an artificial legendary");

	for i in range(stars):
		im_r.paste(images[3], (225 - (i * 25) + x_offset, 2), images[3]);

	# https://stackoverflow.com/questions/16373425
	draw = ImageDraw.Draw(im_r);
	draw.text((2 + x_offset, 355 + 10), name, (0, 0, 0), font = font_name);
	draw.text((195 + x_offset, 421), d_lv3[1].text, (255, 255, 255), font = font_number);

	#im_r.show();
	#Image.composite(image, Image.new('RGB', image.size, 'white'), image).show()
	for im in images:
		im.close();

	output = open('./Girls Frontline/' + padded + '_' + name + '.json', 'w');

	output.write("{\n");
	output.write("\t\"id\":\"" + re.sub('[^0-9a-zA-Z_]+', '_', name).lower() + "\",\n"); # https://stackoverflow.com/questions/12985456/
	output.write("\t\"edition\":\"girls_frontline\",\n");

	rboard = ['???', 'com', 'unc', 'rar', 'anc', 'leg'];
	output.write("\t\"rarity\":\"" + rboard[stars] + "\",\n\n");

	sname = re.sub('[^0-9a-zA-Z_-]+', ' ', name);
	output.write("\t\"name\":\"" + sname + "\",\n");

	cboard = {'UN':'ERROR', 'HG':'Hand Gun', 'AR':'Assault Rifle', 'SMG':'Sub Machine Gun', 'RF':'Rifle', 'MG':'Machine Gun', 'SG':'Shotgun'};
	output.write("\t\"category\":\"" + cboard[typestr] + "\",\n");

	sapth = "Girls Frontline/" + padded + '_' + sname;
	output.write("\t\"asset\":\"" + sapth + "\",\n");
	im_r.save("./" + sapth + ".png", "png");
	im_r.close();

	wboard = [99, 8, 6, 4, 2, 1];
	output.write("\t\"weight\":" + str(wboard[stars]) + "\n");
	output.write("}\n");

	output.close();

	print('=====-----=====');

	count += 1;

