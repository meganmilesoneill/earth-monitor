import osgeo.ogr
import psycopg2

connection = psycopg2.connect(database="earth-monitor")
cursor = connection.cursor()

cursor.execute("DELETE FROM faults")

shapefile = osgeo.ogr.Open("./qfaults/sectionsALL.shp")
layer = shapefile.GetLayer(0)

for i in range(layer.GetFeatureCount()):
    feature  = layer.GetFeature(i)
    faultId     = feature.GetField("fault_id")
    name     = feature.GetField("name")
    url     = feature.GetField("CFM_URL")
    age     = feature.GetField("age")
    ftype = feature.GetField("ftype")
    geometry = feature.GetGeometryRef()

    if geometry is not None:
    	wkt = geometry.ExportToWkt()
    	print("adding fault record for %s" % name)
    	cursor.execute("INSERT INTO faults (fault_id, name, url, age, ftype, geometry) VALUES (%s, %s, %s, %s, %s, ST_GeogFromText(%s))", (faultId, name, url, age, ftype, wkt))
    else:
    	print("no geometry for %s" % name)

connection.commit()