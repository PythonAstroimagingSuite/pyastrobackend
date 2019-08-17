import requests
import shutil
import time

download_url = "http://127.0.0.1:8080/curldownload.json"
fileloc = "tmp.json"
ts=time.time()
with requests.get(download_url, stream=True) as r:
    with open(fileloc, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
te=time.time()
print(f'Download took {te-ts} seconds')