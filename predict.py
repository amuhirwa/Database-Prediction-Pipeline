import requests
import joblib
import pandas as pd

API_BASE_URL = "http://localhost:8000/agriculture-data"
PREDICTION_API_URL = "http://localhost:8000/predictions"
MODEL_PATH = "best_model.joblib"
PREPROCESSOR_PATH = "preprocessor.joblib"

def fetch_latest_entry():
    response = requests.get(f"{API_BASE_URL}/latest")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch latest data: {response.text}")
    return response.json()

def query_average_for_field(country, crop, field):
    response = requests.get(
        API_BASE_URL,
        params={"country": country, "crop": crop, "limit": 1000}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to query records: {response.text}")
    
    data = response.json()
    values = [entry[field] for entry in data if entry[field] is not None]
    if not values:
        raise Exception(f"No valid '{field}' data for country={country}, crop={crop}")
    return sum(values) / len(values)

def handle_missing_values(entry):
    country = entry["country_name"]
    crop = entry["crop_name"]
    for field in ["rainfall", "pesticides", "temperature"]:
        if entry[field] is None:
            avg = query_average_for_field(country, crop, field)
            entry[field] = avg
    return entry

def load_model_and_preprocessor():
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor

def prepare_input(entry, preprocessor):
    df = pd.DataFrame([entry])
    # Rename to match training column names
    df = df.rename(columns={
        "rainfall": "average_rain_fall_mm_per_year",
        "pesticides": "pesticides_tonnes",
        "temperature": "avg_temp",
        "crop_name": "Item",
        "country_name": "Area",
        "year": "Year"
    })
    return preprocessor.transform(df)
