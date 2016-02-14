import osgeo.ogr
import psycopg2

import json
import datetime
import sys

def setLastSuccess(dt):
	with open('earthquake.config', 'w') as f:
		f.write(str(dt.timestamp()))

def getLastSucess():
	try:
		with open('earthquake.config', 'r') as f:
			tss = f.readline()

		ts = float(tss)
		dt = datetime.datetime.utcfromtimestamp(ts)
	except:
		dt = datetime.datetime(2013, 1, 1)

	return dt

def getNextTimeRange():
	startdate = getLastSucess()
	print("last successful startdate: %s" % str(startdate))
	enddate = startdate + datetime.timedelta(days=30)
	if(enddate > datetime.datetime.now()):
		enddate = None

	return (startdate, enddate)

def importEarthquakeData(startdate, enddate):	
	url = "http://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=%s" % startdate.strftime("%Y-%m-%d")
	if (enddate is not None):
		url += "&endtime=%s" % enddate.strftime("%Y-%m-%d")
	url+="&orderby=time-asc&eventtype=earthquake"

	print("Importing earthquake data from: %s" % url)

	query = "INSERT INTO earthquakes " \
	    "(eventid, mag, place, time, updated, tz, url, detail, felt, cdi, mmi, alert, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type, geometry) " \
	    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeogFromText(%s))"

	datasource = osgeo.ogr.Open(url)
	if not datasource:
		sys.exit("ERROR: Cannot open GeoJSON datasource: %s" % query)

	layer = datasource.GetLayer('OGRGeoJSON')

	connection = psycopg2.connect(database="earth-monitor")
	cursor = connection.cursor()

	# If the startdate is 1/1/2013, we're loading from the initial date, so delete existing data
	# TODO: create a method purge the data
	if(startdate.year == 2013 and startdate.month == 1 and startdate.day == 1):
		cursor.execute("DELETE FROM earthquakes")

	i = 0
	total = layer.GetFeatureCount()

	for feature in layer:
		i += 1
		progress_text = "....... (%s of %s) %3.2f%% complete" % (i, total, i/total * 100)

		geometry = feature.GetGeometryRef()

		if geometry is not None:
			wkt = geometry.ExportToWkt()
			ts = feature.GetField("time") / 1000
			data = (
					feature.GetField("id"), 
					feature.GetField("mag"), 
					feature.GetField("place"), 
					feature.GetField("time"), 
					feature.GetField("updated"), 
					feature.GetField("tz"), 
					feature.GetField("url"), 
					feature.GetField("detail"), 
					feature.GetField("felt"), 
					feature.GetField("cdi"), 
					feature.GetField("mmi"), 
					feature.GetField("alert"), 
					feature.GetField("tsunami"), 
					feature.GetField("sig"), 
					feature.GetField("net"), 
					feature.GetField("code"), 
					feature.GetField("ids"), 
					feature.GetField("sources"), 
					feature.GetField("types"), 
					feature.GetField("nst"), 
					feature.GetField("dmin"), 
					feature.GetField("rms"), 
					feature.GetField("gap"), 
					feature.GetField("magType"), 
					feature.GetField("type"), 
					wkt
				)

			try:
				cursor.execute(query, data)
				print('creating earthquake record: %s' % progress_text)
			except:
				print('ERROR creating earthquake record: %s\n%s' % (progress_text, sys.exc_info()[0]))
				continue
		else:
			print("no geometry for %s" % feature.GetField("eventid"))

	connection.commit()	
	cursor.close()
	connection.close()

	setLastSuccess(datetime.datetime.utcfromtimestamp(ts))


def main():
	print("Starting import.")
	startdate, enddate = getNextTimeRange()
	print("Next time range: %s - %s" % (str(startdate), str(enddate)))

	today = datetime.datetime.now()

	while(startdate <= today):
		print("Importing next range")
		importEarthquakeData(startdate, enddate)
		
		startdate, enddate = getNextTimeRange()

	print("Import complete.")

if __name__ == "__main__":
	main()

