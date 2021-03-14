import pandas as pd
import pymongo
import time
from sqlalchemy import create_engine
from config import POSTGRES_PASSWORD

# Create PostgreSQL engine
engine = create_engine(f'postgres://postgres:{POSTGRES_PASSWORD}@localhost:5432/Scooters_DB')

conn = 'mongodb://localhost:27017'

def scooters_mongo_to_sql():
    """
    Retrieve data from MongoDB, clean the data, then save the cleaned data to PostgreSQL
    :return: None
    """
    # # Create PostgreSQL engine
    # engine = create_engine(f'postgres://postgres:{POSTGRES_PASSWORD}@localhost:5432/Scooters_DB')


    # Retrieve the most recent "save_at" time from table "process_log" at "scooters_DB"
    last_saved = list(engine.execute("SELECT MAX(last_saved) FROM process_log"))[0][0]
    # There is no data at first time run. Set last_saved as o in such case
    if not last_saved:
        last_saved = 0


    # Retrieve data from MongoDB
    # Only retrieve the new data since last last
    # conn = 'mongodb://localhost:27017'
    with pymongo.MongoClient(conn) as client:
        db = client.scooters_DB
        collection = db.scooters
        data = collection.find({"saved_at": {"$gt": last_saved}})
        # max_saved_at = collection


    # Using pandas to clean data
    df = pd.DataFrame(list(data))
    last_saved = df["saved_at"].max()

    new_df = df[["company", "last_updated", "bike_id", "tractid"]].copy()
    df1 = new_df.dropna()
    df2 = df1.drop_duplicates()

    # For records that only have last_updated different, Keep the records with minimum last_updated and drop others
    df3 = df2.groupby(["company", "bike_id", "tractid"]).min()
    cleaned_df = df3.reset_index()


    # Data for the table "process_log"
    qty = len(cleaned_df)
    log_record = {}
    log_record["last_saved"] = last_saved
    log_record["saved_records"] = qty
    log_df = pd.DataFrame([log_record])





    # Save data to PostgreSQL
    with engine.connect() as connection:
        cleaned_df.to_sql(name='scooter_records', con=connection, if_exists='append', index=False)
        log_df.to_sql(name='process_log', con=connection, if_exists='append', index=False)


def weather_mongo_to_sql():
    with pymongo.MongoClient(conn) as client:
        db = client.scooters_DB
        collection = db.weather
        data = collection.find()

    # Using pandas to clean data
    df = pd.DataFrame(list(data))
    last_saved = df["saved_at"].max()

    new_df = df[["air_temp", "humidity", "visibility", "wind_speed", "last_updated", "tractid"]].copy()
    df1 = new_df.dropna()
    cleaned_df = df1.drop_duplicates()

    # Save data to PostgreSQL
    with engine.connect() as connection:
        cleaned_df.to_sql(name='weather_records', con=connection, if_exists='append', index=False)

    # After save data to postgreSQL, delete processed data from MongoDB, so don't get the same data processed repeatedly
    with pymongo.MongoClient(conn) as client:
        db = client.scooters_DB
        collection = db.weather
        collection.delete_many({"save_at": {"$lte": last_saved}})

