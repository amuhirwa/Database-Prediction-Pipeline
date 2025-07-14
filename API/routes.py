from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from db_connector import get_db_connection
from models import AgricultureDataCreate, AgricultureDataResponse, PredictionCreate, PredictionResponse
import psycopg2

router = APIRouter()

@router.post("/agriculture-data/", status_code=201, response_model=AgricultureDataResponse)
def create_agriculture_data(data: AgricultureDataCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CALL insert_agriculture_data(%s, %s, %s, %s, %s, %s, %s)",
            (
                data.country_name,
                data.crop_name,
                data.year,
                data.yield_value,
                data.rainfall,
                data.pesticides,
                data.temperature,
            )
        )
        conn.commit()
        cursor.execute("""
            SELECT ad.record_id, c.country_id, cr.crop_id,
                   c.name as country_name, cr.name as crop_name,
                   ad.year, ad.yield as yield_value, ad.rainfall, ad.pesticides, ad.temperature
            FROM AgricultureData ad
            JOIN Countries c ON ad.country_id = c.country_id
            JOIN Crops cr ON ad.crop_id = cr.crop_id
            ORDER BY ad.record_id DESC LIMIT 1
        """)
        new_record = cursor.fetchone()
        return new_record
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/agriculture-data/", response_model=List[AgricultureDataResponse])
def get_agriculture_data(
    country: Optional[str] = None,
    crop: Optional[str] = None,
    year: Optional[int] = None,
    min_yield: Optional[int] = None,
    max_yield: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT ad.record_id, c.country_id, cr.crop_id,
                   c.name as country_name, cr.name as crop_name,
                   ad.year, ad.yield as yield_value, ad.rainfall, ad.pesticides, ad.temperature
            FROM AgricultureData ad
            JOIN Countries c ON ad.country_id = c.country_id
            JOIN Crops cr ON ad.crop_id = cr.crop_id
            WHERE 1=1
        """
        params = []

        if country:
            query += " AND c.name = %s"
            params.append(country)
        if crop:
            query += " AND cr.name = %s"
            params.append(crop)
        if year:
            query += " AND ad.year = %s"
            params.append(year)
        if min_yield is not None:
            query += " AND ad.yield >= %s"
            params.append(min_yield)
        if max_yield is not None:
            query += " AND ad.yield <= %s"
            params.append(max_yield)

        query += " ORDER BY ad.year DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()

@router.get("/agriculture-data/latest", response_model=Optional[AgricultureDataResponse])
def get_latest_agriculture_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ad.record_id, c.country_id, cr.crop_id,
                   c.name as country_name, cr.name as crop_name,
                   ad.year, ad.yield as yield_value, ad.rainfall, ad.pesticides, ad.temperature
            FROM AgricultureData ad
            JOIN Countries c ON ad.country_id = c.country_id
            JOIN Crops cr ON ad.crop_id = cr.crop_id
            ORDER BY ad.record_id DESC
            LIMIT 1
        """)
        latest_record = cursor.fetchone()
        if not latest_record:
            raise HTTPException(status_code=404, detail="No records found")
        return latest_record
    finally:
        cursor.close()
        conn.close()


@router.get("/agriculture-data/{record_id}", response_model=AgricultureDataResponse)
def get_agriculture_record(record_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ad.record_id, c.country_id, cr.crop_id,
                   c.name as country_name, cr.name as crop_name,
                   ad.year, ad.yield as yield_value, ad.rainfall, ad.pesticides, ad.temperature
            FROM AgricultureData ad
            JOIN Countries c ON ad.country_id = c.country_id
            JOIN Crops cr ON ad.crop_id = cr.crop_id
            WHERE ad.record_id = %s
        """, (record_id,))
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    finally:
        cursor.close()
        conn.close()

@router.put("/agriculture-data/{record_id}", response_model=AgricultureDataResponse)
def update_agriculture_record(record_id: int, data: AgricultureDataCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert or get country
        cursor.execute("""
            INSERT INTO Countries (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
        """, (data.country_name,))
        cursor.execute("SELECT country_id FROM Countries WHERE name = %s", (data.country_name,))
        country = cursor.fetchone()
        if not country:
            raise HTTPException(status_code=500, detail="Failed to fetch or create country")

        # Insert or get crop
        cursor.execute("""
            INSERT INTO Crops (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
        """, (data.crop_name,))
        cursor.execute("SELECT crop_id FROM Crops WHERE name = %s", (data.crop_name,))
        crop = cursor.fetchone()
        if not crop:
            raise HTTPException(status_code=500, detail="Failed to fetch or create crop")
        # Update the agriculture record
        cursor.execute("""
            UPDATE AgricultureData
            SET country_id = %s, crop_id = %s, year = %s,
                yield = %s, rainfall = %s, pesticides = %s, temperature = %s
            WHERE record_id = %s
            RETURNING record_id
        """, (
            country['country_id'], crop['crop_id'], data.year,
            data.yield_value, data.rainfall, data.pesticides,
            data.temperature, record_id
        ))
        updated_record = cursor.fetchone()
        if not updated_record:
            raise HTTPException(status_code=404, detail="Record not found")

        conn.commit()
        print("Done updating")
        return get_agriculture_record(record_id)

    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.delete("/agriculture-data/{record_id}", status_code=204)
def delete_agriculture_record(record_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM AgricultureData WHERE record_id = %s RETURNING record_id", (record_id,))
        deleted = cursor.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

@router.post("/predictions", status_code=201, response_model=PredictionResponse)
def create_prediction(prediction: PredictionCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Predictions (record_id, predicted_yield)
            VALUES (%s, %s)
            RETURNING prediction_id, record_id, predicted_yield, created_at
        """, (prediction.record_id, prediction.predicted_yield))
        saved_prediction = cursor.fetchone()
        print(saved_prediction)
        conn.commit()
        return {
            "prediction_id": saved_prediction['prediction_id'],
            "record_id": saved_prediction['record_id'],
            "predicted_yield": saved_prediction['predicted_yield'],
            "created_at": saved_prediction['created_at']
        }
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
