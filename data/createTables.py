import psycopg2
import osgeo.ogr
import shapely

connection = psycopg2.connect(database="earth-monitor")
cursor = connection.cursor()
	
cursor.execute("DROP TABLE IF EXISTS faults")

cursor.execute("CREATE TABLE faults (" +
                   "id SERIAL PRIMARY KEY," +
                   "fault_id VARCHAR NULL," +
                   "name VARCHAR NULL," +
                   "url VARCHAR NULL," +
                   "age VARCHAR NULL," +
                   "ftype VARCHAR NULL," +
                   "geometry GEOGRAPHY)")


cursor.execute("CREATE INDEX fault_index ON faults USING GIST(geometry)")

cursor.execute("DROP TABLE IF EXISTS earthquakes")

# Fields based on USGS documentation for geojson here: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
cursor.execute("CREATE TABLE earthquakes (" +
                   "id SERIAL PRIMARY KEY," +
                   "eventid VARCHAR NULL," +
                   "mag decimal NULL," +
                   "place VARCHAR NULL," +
                   "time bigint NULL," +
                   "updated bigint NULL," +
                   "tz smallint NULL," +
                   "url VARCHAR NULL," +
                   "detail VARCHAR NULL," +
                   "felt smallint NULL," +
                   "cdi decimal NULL," +
                   "mmi decimal NULL," +
                   "alert VARCHAR NULL," +
                   "status VARCHAR NULL," +
                   "tsunami smallint NULL," +
                   "sig smallint NULL," +
                   "net VARCHAR NULL," +
                   "code VARCHAR NULL," +
                   "ids VARCHAR NULL," +
                   "sources VARCHAR NULL," +
                   "types VARCHAR NULL," +
                   "nst smallint NULL," +
                   "dmin decimal NULL," +
                   "rms decimal NULL," +
                   "gap decimal NULL," +
                   "magType VARCHAR NULL," +
                   "type VARCHAR NULL," +
                   "geometry GEOGRAPHY)")

cursor.execute("CREATE INDEX earthquake_index ON earthquakes USING GIST(geometry)")

connection.commit()