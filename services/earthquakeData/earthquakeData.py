from flask import Flask, jsonify
from flask.ext.cors import CORS

import json
import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
	return 'Earthquake Data Service is Running!'

@app.route('/faults')
def getFaults():
	try:
		data = None;
		with open('static/Holocene_LatestPleistocene.json') as f:
			data = json.loads(f.read())

		return jsonify(data);
	except:
		return sys.exc_info()[0]


@app.route('/events')
def getEvents():
	return 'event data!'

if __name__ == "__main__":
	app.run(debug=True)
