# Dependencies
import time
from scooters import scooters_data
from weather import weather_data
from mongo_to_sql import scooters_mongo_to_sql, weather_mongo_to_sql

i = 1
while i < 6:
    scooters_data()
    weather_data()
    time.sleep(60)
    i += 1
    if i % 2 == 0:
        scooters_mongo_to_sql()
        weather_mongo_to_sql()
    print(i)


