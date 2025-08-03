import requests
import time
import re
import tqdm
import os

headers = {
	"Accept": "application/json",
	"Referer": "https://www.pixiv.net/en/users/<id>/bookmarks/artworks",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
	"Cookie": "<Cookie>"
}

def get_bookmark(fr, to):
	res = requests.get(f"https://www.pixiv.net/ajax/user/<id>/illusts/bookmarks?tag=&offset={fr}&limit={to - fr}&rest=show&lang=en", headers = headers)
	print(f" from {fr} to {to}")
	print(res.text)
	print("")
	return res.json()["body"]["works"]

def get_all_bookmarks():
	bms = []
	bmt = []
	l = 0
	r = 48
	bmt = get_bookmark(0, 48)
	bms += bmt
	while len(bmt) > 0:
		l = r
		r += 48
		bmt = get_bookmark(l, r)
		bms += bmt
		time.sleep(1)
	return bms

def process_bookmarks(l):
	new_l = []
	for o in tqdm.tqdm(l):
		if o["url"] == "https://s.pximg.net/common/images/limit_unknown_360.png":
			continue
		
		pic_id = o["id"]
		res_raw = requests.get(f"https://www.pixiv.net/ajax/illust/{pic_id}?lang=en", headers = headers)
		res = res_raw.json()

		if not res_raw.ok:
			time.sleep(2)
			print("!ok, retring")
			res_raw = requests.get(f"https://www.pixiv.net/ajax/illust/{pic_id}?lang=en", headers = headers)
			if not res_raw.ok:
				print("fuck!")
			res = res_raw.json()

		if o["pageCount"] == 1:
			new_l.append({
				"id": pic_id,
				"url": res["body"]["urls"]["original"]
			})
		else:
			k = o["pageCount"]
			for i in range(0, k):
				new_l.append({
					"id": pic_id + "_" + str(i),
					"url": res["body"]["urls"]["original"].replace("p0", "p" + str(i))
				})
	return new_l

def download(url, name, type):
	path = "./img/" + name + "." + type
	if os.path.exists(path):
		return

	res = requests.get(url, headers = headers)
	with open(path, "wb") as f:
		f.write(res.content)

def download_all(l):
	for pic in tqdm.tqdm(l):
		download(pic["url"], pic["id"], re.match(r".*\.(.*)", pic["url"]).group(1))

download_all(new_l)