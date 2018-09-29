#!/usr/bin/env python3

import requests
import re
import json
import sys
import argparse

from tqdm import tqdm

API = "http://svp.vg.no/svp/api/v1/vgtv/assets/{0}?appName=vgtv-website"

# Used for the prgressbar
chunk_size = 1024


def validateURL(url):
	"""
	Validate the given url
	:param url: URL to the VGTV or VG page with the video
	:type url: str
	"""

	vgtv = "vgtv"
	vg = "vg"
	
	if vgtv in url:
		return "valid", vgtv

	elif vg in url:
		return "valid", vg

	else:
		return "not valid"


def download(fileURL, title, fname):
	"""
	Downloads the video file
	:param fileURL: URL of the MP4 file
	:type fileURL: str

	:param title: Title of the video or article
	:type title: str

	:param fname: File name of the video file
	:type fname: str
	"""

	try:
		print("\033[92mDownloading:\033[0m", title)

		r = requests.get(fileURL, stream = True)
		total_size = int(r.headers['content-length'])
			
		# I found this progress bar thing on youtube. I like it :)
		# https://www.youtube.com/watch?v=Xhw2l-hzoKk
		with open(fname, 'wb') as f:
			for data in tqdm(iterable = r.iter_content(chunk_size = chunk_size), total = total_size/chunk_size, unit = 'KB'):
				f.write(data)

			print("\033[92mDownloaded:\033[0m", fname)

	except KeyboardInterrupt:
		print("\nExiting")
		sys.exit()


def getdata(url, method):
	"""
	:param url: The given URL to extract the data from
	:type url: str

	:param method: Method to be used when downloading the video
	:type method: str
	"""

	if method == "vgtv":
		videoID = re.findall('vgtv.no\/video\/(\d+)', url)[0]

		r = requests.get(API.format(videoID))
		
		data = json.loads(r.text)
		
		title = data["title"]
		fileURL = data["streamUrls"]["mp4"]
		fname = title.replace(" ", "_") + ".mp4"

		download(fileURL=fileURL, title=title, fname=fname)	
    
    # when method is vg
	else:
		r = requests.get(url)
		html = r.text

		fileURL = re.findall('pseudostreaming"(.*?)",', html)[0]
		fileURL = fileURL.replace(':["', '')
		fileURL = fileURL.replace("\\u002F", "/")

		title = re.findall('headline":"(.*?)",', html)[0]
		fname = title.replace(" ", "_") + ".mp4"
		
		download(fileURL=fileURL, title=title, fname=fname)


def main():
    # These are used for testing
    #url = "https://www.vgtv.no/video/164927/skal-lande-blir-tatt-av-stormen"
    #url = "https://www.vg.no/nyheter/innenriks/i/7lOwEV/nrk-politikere-bedt-om-aa-bytte-mobil-etter-spionmistanke"

    parser = argparse.ArgumentParser(description = "Download videos from VGTV and VG")

    parser.add_argument('url', action="store", help="URL to the VGTV or VG page with the video")
    
    args = parser.parse_args()

    url = args.url
    
    is_valid = validateURL(url)

    if is_valid[0] == "valid":
    	if is_valid[1] == "vgtv":
    		getdata(url, method="vgtv")
    	
    	else:
    		getdata(url, method="vg")
    		
    else:
    	print("Invalid url")
    	sys.exit()

if __name__ == "__main__":
	main()