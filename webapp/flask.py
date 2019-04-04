from flask import Flask
from flask import jsonify
app = Flask(__name__)

import requests
@app.route("/")
def hello():
    url = "https://116.15.140.189:5332/data.php"
    r = requests.get(url, verify=False)
    result={}
    if r.status_code == 200:
        result["success"]=True
    else:
        result["success"]=False
    return jsonify(result)
