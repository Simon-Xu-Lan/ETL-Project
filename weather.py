import requests
import pymongo
import time

from geo_polygons import Polygons

URL = 'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/152/query?where=1%3D1&outFields=OBJECTID,AIRTEMP,RELATIVEHUMIDITY,VISIBILITY,WINDSPEED,DATADATETIME&outSR=4326&f=json'


# 🍏 MONGODB
# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.scooters_DB
collection = db.weather


def weather_data():
    response = requests.get(URL)
    weather_data = response.json()['features']

    doc_sets = process_weather_data(weather_data)

    # Save "doc_sets" to MongoDB
    collection.insert_many(doc_sets)


def process_weather_data(data):
    polygons = Polygons()
    doc_sets = []
    for each_record in data:
        lat = float(each_record["geometry"]["y"])
        lon = float(each_record["geometry"]["x"])
        point = [lon, lat]
        tractid = polygons.get_tractid(point)

        new_doc = {}
        new_doc["air_temp"] = each_record["attributes"]["AIRTEMP"]
        new_doc["humidity"] = each_record["attributes"]["RELATIVEHUMIDITY"]
        new_doc["visibility"] = each_record["attributes"]["VISIBILITY"]
        new_doc["wind_speed"] = each_record["attributes"]["WINDSPEED"]
        new_doc["last_updated"] = int(int(each_record["attributes"]["DATADATETIME"]) / 1000)
        new_doc["tractid"] = tractid
        new_doc["saved_at"] = int(time.time())

        doc_sets.append(new_doc)

    return doc_sets



  
