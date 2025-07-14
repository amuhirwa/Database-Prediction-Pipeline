import os
from pymongo import MongoClient, ASCENDING
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Load environment variable
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB configuration
DB_NAME = "CropYieldDB"
COLLECTION_NAME = "agriculture_data"

def get_mongo_client():
    return MongoClient(MONGO_URI)

def initialize_indexes():
    client = get_mongo_client()
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"Connected to MongoDB. Creating indexes on '{DB_NAME}.{COLLECTION_NAME}'...")

    # Baseline indexes for performance-critical fields
    collection.create_index([("country_id", ASCENDING)])
    collection.create_index([("crop_id", ASCENDING)])
    collection.create_index([("year", ASCENDING)])

    # Compound index for frequent lookups by country, crop, and year
    collection.create_index(
        [("country_id", ASCENDING), ("crop_id", ASCENDING), ("year", ASCENDING)],
        name="country_crop_year_idx"
    )

    print("Indexes created successfully.")
    client.close()

if __name__ == "__main__":
    initialize_indexes()
