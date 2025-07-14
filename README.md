# Crop Yield Prediction Pipeline

This project implements a full data pipeline for crop yield prediction. It uses PostgreSQL for structured data, MongoDB for flexible logging, and FastAPI to expose REST endpoints. A trained machine learning model predicts crop yields based on environmental and agricultural factors.

Repository: [https://github.com/amuhirwa/Database-Prediction-Pipeline](https://github.com/amuhirwa/Database-Prediction-Pipeline)

## Key Features

- **Area (Country)** – 101 unique countries (categorical)
- **Item (Crop Type)** – Includes Wheat, Maize, Rice, and others
- **Year** – Harvest year (1990–2019)
- **hg/ha_yield** – Crop yield (target variable) in hectograms per hectare
- **average_rain_fall_mm_per_year** – Yearly average rainfall
- **pesticides_tonnes** – Pesticide usage in tonnes
- **avg_temp** – Average temperature in Celsius

---

## Project Structure

```bash
.
│   .env                     # Environment variables
│   .gitignore
│   README.md
│   requirements.txt
│
├───API/
│   ├── db_connector.py      # Manages DB connections
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # Pydantic data models
│   └── routes.py            # API routes
│
├───databases/
│   ├── import_crop_yield.py         # Imports CSV data into PostgreSQL and MongoDB
│   ├── yield_df.csv
│   ├───mongodb/
│   │   ├── agri_data_document_example.json
│   │   ├── country_document_example.json
│   │   ├── crop_document_example.json
│   │   └── initialize_mongo_indexes.py
│   └───postgresql/
│       ├── agriculture_schema_base.png
│       ├── create_postgres.py
│       ├── crop_yield_schema.sql
│       └── schema_base.png
│
└───prediction/
    ├── best_model.joblib     # Trained ML model
    ├── predict.py            # Predicts yield for most recent entry
    └── preprocessor.joblib   # Preprocessing pipeline
````

---

## Environment Variables (.env)

Your `.env` file should follow this structure:

```ini
DB_HOST=crop-yield-db-crop-yield.l.aivencloud.com
DB_PORT=16505
DB_NAME=defaultdb
DB_USER=admin
DB_PASSWORD=Password
DB_SSLMODE=require

MONGO_URI=mongodb+srv://username:password@Host.com/?retryWrites=true&w=majority&appName=CropYield
```

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/amuhirwa/Database-Prediction-Pipeline.git
cd Database-Prediction-Pipeline
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Running the Application

### 1. Start the API

```bash
uvicorn API.main:app --reload
```

Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

---

## Scripts

### Import All Data

Use this to import the dataset into both PostgreSQL and MongoDB.

```bash
python databases/import_crop_yield.py
```

* Loads `yield_df.csv` into PostgreSQL tables
* Inserts `yield_df.csv` into MongoDB collections

### Predict Latest Entry

Use this to get the yield prediction for the most recently added database entry.

```bash
python prediction/predict.py
```

* Fetches the latest record via API
* Fills in missing data with average of similar entries
* Preprocesses the input using `preprocessor.joblib`
* Predicts using `best_model.joblib`
* Logs prediction into MongoDB

---

## API Endpoints Summary

| Method | Endpoint                        | Description                                                                      |
| ------ | ------------------------------- | -------------------------------------------------------------------------------- |
| POST   | `/agriculture-data/`            | Create a new agriculture data record (uses a stored procedure in PostgreSQL).    |
| GET    | `/agriculture-data/`            | Retrieve all records with optional filters (country, crop, year, yield range).   |
| GET    | `/agriculture-data/latest`      | Get the most recently added agriculture record.                                  |
| GET    | `/agriculture-data/{record_id}` | Retrieve a specific agriculture record by ID.                                    |
| PUT    | `/agriculture-data/{record_id}` | Update an existing record. Automatically inserts country or crop if not present. |
| DELETE | `/agriculture-data/{record_id}` | Delete a specific agriculture record by its ID.                                  |
