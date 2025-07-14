import pandas as pd
import psycopg2
from pymongo import MongoClient
import os

# Configs
PG_CONN_INFO = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSLMODE')
}

MONGO_URI = os.getenv('MONGO_URI')
CSV_FILE = "yield_df.csv"

def get_pg_connection():
    return psycopg2.connect(**PG_CONN_INFO)

def get_mongo_client():
    return MongoClient(MONGO_URI)

def insert_pg_data(cursor, row):
    """
    Calls the stored procedure to insert agriculture data into PostgreSQL.
    """
    cursor.execute(
    "CALL insert_agriculture_data(%s, %s, %s, %s, %s, %s, %s)",
    (
        row["Area"],
        row["Item"],
        int(row["Year"]),
        int(row["hg/ha_yield"]),
        float(row["average_rain_fall_mm_per_year"]),
        float(row["pesticides_tonnes"]),
        float(row["avg_temp"]),

    )
    )

def insert_mongo_data(mongo_db, row):
    """
    Inserts normalized agricultural data into MongoDB using references to Countries and Crops collections.
    """
    countries_col = mongo_db["Countries"]
    crops_col = mongo_db["Crops"]
    agri_col = mongo_db["AgricultureData"]

    country_name = row["Area"]
    crop_name = row["Item"]

    # Upsert (find or insert) Country
    country = countries_col.find_one({"name": country_name})
    if not country:
        country_id = countries_col.insert_one({"name": country_name}).inserted_id
    else:
        country_id = country["_id"]

    # Upsert (find or insert) Crop
    crop = crops_col.find_one({"name": crop_name})
    if not crop:
        crop_id = crops_col.insert_one({"name": crop_name}).inserted_id
    else:
        crop_id = crop["_id"]

    # Prepare document for AgricultureData
    doc = {
        "country_id": country_id,
        "crop_id": crop_id,
        "year": int(row["Year"]),
        "yield": int(row["hg/ha_yield"]) if pd.notnull(row["hg/ha_yield"]) else None,
        "rainfall": float(row["average_rain_fall_mm_per_year"]) if pd.notnull(row["average_rain_fall_mm_per_year"]) else None,
        "pesticides": float(row["pesticides_tonnes"]) if pd.notnull(row["pesticides_tonnes"]) else None,
        "temperature": float(row["avg_temp"]) if pd.notnull(row["avg_temp"]) else None
    }

    agri_col.insert_one(doc)

def main():
    # Load CSV with pandas
    df = pd.read_csv(CSV_FILE)

    # Connect to DBs
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    mongo_client = get_mongo_client()
    mongo_db = mongo_client["CropYieldDB"]
    mongo_collection = mongo_db["agriculture_data"]
    print("Starting import...")

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            insert_pg_data(pg_cursor, row)
            insert_mongo_data(mongo_collection, row)
        except Exception as e:
            print(f"Failed to insert row {row.to_dict()}: {e}")
        
        if i % 100 == 0:
            print(f"Inserted {i} rows so far...")

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()

    print("Import complete!")

if __name__ == "__main__":
    main()
