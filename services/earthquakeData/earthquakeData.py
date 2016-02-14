from flask import Flask, jsonify, request
from flask.ext.cors import CORS

import json
import sys

import psycopg2
import datetime
import logging

app = Flask(__name__)
CORS(app)

_fault_data = None

@app.route('/')
def index():
	return 'Earthquake Data Service is Running!'

@app.route('/faults')
def getFaults():
	# default bounding box is the San Francisco Bay Area, United States
	minlongitude = request.args.get('minlongitude', -125.69510773828125, type=float)
	minlatitude = request.args.get('minlatitude', 38.79394764206436, type=float)
	maxlongitude = request.args.get('maxlongitude', -119.31754426171875, type=float)
	maxlatitude = request.args.get('maxlatitude', 36.682994957749884, type=float)

	try:
		data = None

		connection = psycopg2.connect(database="earth-monitor")
		cursor = connection.cursor()
		cursor.execute("SELECT row_to_json(fc) FROM (SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (SELECT 'Feature' As type, ST_AsGeoJSON(fa.geometry)::json As geometry, row_to_json(p) As properties FROM faults As fa INNER JOIN (SELECT id, fault_id, name, url FROM faults) As p ON fa.id = p.id WHERE fa.geometry && ST_MakeEnvelope(%4.6f, %4.6f, %4.6f, %4.6f, 4326) AND fa.fault_id IS NOT NULL AND age <> '<1,600,000') as f) as fc;" % (minlongitude, minlatitude, maxlongitude, maxlatitude))
		data = cursor.fetchall()
		cursor.close()
		connection.close()

		return jsonify(data[0][0]);
	except:
		return sys.exc_info()[0]


@app.route('/earthquakes')
def getEarthquakes():
	# default bounding box is the San Francisco Bay Area, United States
	minlongitude = request.args.get('minlongitude', -125.69510773828125, type=float)
	minlatitude = request.args.get('minlatitude', 38.79394764206436, type=float)
	maxlongitude = request.args.get('maxlongitude', -119.31754426171875, type=float)
	maxlatitude = request.args.get('maxlatitude', 36.682994957749884, type=float)
	starttime = request.args.get('starttime', "NULL")
	endtime = request.args.get('endtime', "NULL")

	if starttime != "NULL":
		startdate = datetime.datetime.strptime(starttime, '%Y-%m-%d')
	else:
		startdate = datetime.datetime.utcnow() - datetime.timedelta(days=30)

	timefilter = " AND e.time >= %s" % (startdate.timestamp() * 1000)

	if endtime != "NULL":
		enddate = datetime.datetime.strptime(endtime, '%Y-%m-%d')
		timefilter = " AND e.time <= %s" % (enddate.timestamp() * 1000)

	query = "SELECT row_to_json(fc) FROM (SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features FROM (SELECT 'Feature' As type, ST_AsGeoJSON(e.geometry)::json As geometry, row_to_json(p) As properties FROM earthquakes As e INNER JOIN (SELECT id, eventid, mag, place, time, url, detail FROM earthquakes) As p ON e.id = p.id WHERE e.geometry && ST_MakeEnvelope(%4.6f, %4.6f, %4.6f, %4.6f, 4326)%s) as f) as fc;" % (minlongitude, minlatitude, maxlongitude, maxlatitude, timefilter)

	try:
		data = None

		connection = psycopg2.connect(database="earth-monitor")
		cursor = connection.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		connection.close()

		if(data):
			return jsonify(data[0][0])
		else:
			return None
	except:
		return sys.exc_info()[0]

if __name__ == "__main__":
	app.run(debug=True)
