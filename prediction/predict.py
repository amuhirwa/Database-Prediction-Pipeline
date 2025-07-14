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

def log_prediction(record_id, predicted_yield):
    payload = {
        "record_id": record_id,
        "predicted_yield": predicted_yield
    }
    response = requests.post(PREDICTION_API_URL, json=payload)
    if response.status_code != 201:
        raise Exception(f"Failed to log prediction: {response.text}")
    return response.json()

def main():
    latest_entry = fetch_latest_entry()
    record_id = latest_entry["record_id"]

    entry_filled = handle_missing_values(latest_entry)

    model, preprocessor = load_model_and_preprocessor()
    X = prepare_input(entry_filled, preprocessor)
    prediction = model.predict(X)[0]
    print(f"Predicted yield: {prediction}")

    result = log_prediction(record_id, prediction)
    print(f"Prediction logged for record {record_id}: Yield = {prediction}")

if __name__ == "__main__":
    main()
