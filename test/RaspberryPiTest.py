import requests
import json

url = "http://18.136.197.29:5000/"
r = requests.get(url, verify=False)
j = json.loads(r.text)
if j["success"]:
    exit()
else:
    exit(1)
