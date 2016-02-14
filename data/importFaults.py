import osgeo.ogr
import psycopg2

def importFaultData():	

	query = "INSERT INTO faults " \
		"(slipdirect, length, sectionid, name, fcode, slipsense, agecat, age, objectid, facode, mappedscal, faultid, slipcode, ftype, dipdirecti, num, secondaries, cooperator, acode, azimuth, sliprate, url, code, geometry) " \
		"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeogFromText(%s))"

	shapefile = osgeo.ogr.Open("./qfaults/sectionsALL.shp")
	layer = shapefile.GetLayer(0)

	connection = psycopg2.connect(database="earth-monitor")
	cursor = connection.cursor()

	cursor.execute("DELETE FROM faults")

	print("importing faults.  %s found" % layer.GetFeatureCount())

	for feature in layer:
		geometry = feature.GetGeometryRef()

		if geometry is not None:
			wkt = geometry.ExportToWkt()
			name = feature.GetField("name")
			agecat = feature.GetField("age")
			try:
				age = int(''.join([c for c in agecat if c not in (',', '<')]))
			except:
				age = 0
				
			data = (
				feature.GetField("slipdirect"), 
				feature.GetField("length"), 
				feature.GetField("section_id"), 
				name, 
				feature.GetField("fcode"), 
				feature.GetField("slipsense"), 
				agecat, 
				age, 
				feature.GetField("objectid"), 
				feature.GetField("FACODE"), 
				feature.GetField("mappedscal"), 
				feature.GetField("fault_id"), 
				feature.GetField("slipcode"), 
				feature.GetField("ftype"), 
				feature.GetField("dipdirecti"), 
				feature.GetField("num"), 
				feature.GetField("secondarys"), 
				feature.GetField("cooperator"), 
				feature.GetField("acode"), 
				feature.GetField("azimuth"), 
				feature.GetField("sliprate"), 
				feature.GetField("CFM_URL"), 
				feature.GetField("code"), 
				wkt
			)

			try:
				cursor.execute(query, data)
				print('creating fault record: %s' % name)
			except:
				print('ERROR creating earthquake record: %s\n%s' % (name, sys.exc_info()[0]))
				continue
		else:
			print("no geometry for %s" % name)

	connection.commit()



def main():
	importFaultData()

if __name__ == "__main__":
	main()
