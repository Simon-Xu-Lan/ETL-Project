# 🍏 Dependencies
# Python libraries
import requests
import pymongo
import time

# Customized modules
from Resources.companies import compInfo
from geo_polygons import Polygons


# 🍏 MONGODB
# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Define database and collection
db = client.scooters_DB
collection = db.scooters


# 🍏 # Create a Polygons instance/object
polygons = Polygons()


# 🍏 Initialize recent last_updated data
recent_last_updated = {}
for company in compInfo:
    recent_last_updated[company["name"]] = 0


# 🍏 FUNCTIONS
def scooters_data():
    for company in compInfo:
        name = company["name"]

        print("$$$ ", name)

        try:
            response = requests.get(company["url"])
            data = response.json()
        except:
            # If a company url doesn't work, continue next company url, print the url that is not work
            print(f"{name} url has issue")
            continue

        # Assign the value of last_updated to varialbe "last_updated"
        # if data doesn't have last_updated attibute, use current time as "last_updated"
        # Make sure the last_updated is integer for future use
        try:
            last_updated = int(data["last_updated"])
        except:
            # 🍎Issue, using current time would save much more records, need modify later
            last_updated = int(time.time())

        # Retrieve data by layers
        for layer in company["layers"]:
            data = data[layer]

        # If last_updated changes, save data to mongoDB
        if last_updated > recent_last_updated[name]:
            # Process data and save data to MongoDB
            doc_sets = process_data(data, name, last_updated)
            collection.insert_many(doc_sets)

        # update recent_last_updated
        recent_last_updated[name] = last_updated


def process_data(data, name, last_updated):
    doc_sets = []
    for each_data in data:
        new_doc = {}
        new_doc["company"] = name
        new_doc["last_updated"] = last_updated
        new_doc["bike_id"] = each_data["bike_id"]
        new_doc["saved_at"] = int(time.time())
        point = [float(each_data["lon"]), float(each_data["lat"])]
        new_doc["tractid"] = polygons.get_tractid(point)
        doc_sets.append(new_doc)

    return doc_sets