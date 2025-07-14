import os
from dotenv import load_dotenv
import psycopg2

# Load .env file
load_dotenv()

DB_HOST="crop-yield-db-crop-yield.l.aivencloud.com"
DB_PORT=16505
DB_NAME="defaultdb"
DB_USER="avnadmin"
DB_PASSWORD="AVNS_vAaBqtBoyJVRJiRGoUo"
DB_SSLMODE="require"


# Build DB params from environment (Hardcoded my credentials in case of facilitator testing)
DB_PARAMS = {
    'host': os.getenv('DB_HOST', DB_HOST),
    'port': os.getenv('DB_PORT', DB_PORT),
    'dbname': os.getenv('DB_NAME', DB_NAME),
    'user': os.getenv('DB_USER', DB_USER),
    'password': os.getenv('DB_PASSWORD', DB_PASSWORD),
    'sslmode': os.getenv('DB_SSLMODE', DB_SSLMODE)
}

def create_database_structure():
    """Creates the entire database structure including tables, procedures, and triggers."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Create Countries table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Countries (
            country_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        );
        """)
        
        # Create Crops table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Crops (
            crop_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        );
        """)
        
        # Create AgricultureData table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS AgricultureData (
            record_id SERIAL PRIMARY KEY,
            country_id INT REFERENCES Countries(country_id),
            crop_id INT REFERENCES Crops(crop_id),
            year INT NOT NULL,
            yield INT,
            rainfall FLOAT,
            pesticides FLOAT,
            temperature FLOAT
        );
        """)
        
        # Create the insert procedure
        cursor.execute("""
        CREATE OR REPLACE PROCEDURE insert_agriculture_data(
            p_country VARCHAR,
            p_crop VARCHAR,
            p_year INT,
            p_yield INT,
            p_rainfall FLOAT,
            p_pesticides FLOAT,
            p_temp FLOAT
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- Input validation
            IF p_year < 1900 OR p_year > EXTRACT(YEAR FROM CURRENT_DATE) THEN
                RAISE EXCEPTION 'Invalid year: %', p_year;
            END IF;

            IF p_yield IS NOT NULL AND p_yield < 0 THEN
                RAISE EXCEPTION 'Yield must be non-negative.';
            END IF;

            IF p_rainfall IS NOT NULL AND p_rainfall < 0 THEN
                RAISE EXCEPTION 'Rainfall must be non-negative.';
            END IF;

            IF p_pesticides IS NOT NULL AND p_pesticides < 0 THEN
                RAISE EXCEPTION 'Pesticides value must be non-negative.';
            END IF;

            IF p_temp IS NOT NULL AND (p_temp < -50 OR p_temp > 60) THEN
                RAISE EXCEPTION 'Temperature seems out of valid range (-50 to 60 °C): %', p_temp;
            END IF;

            -- Insert country if it does not exist
            IF NOT EXISTS (SELECT 1 FROM Countries WHERE name = p_country) THEN
                INSERT INTO Countries(name) VALUES(p_country);
            END IF;

            -- Insert crop if it does not exist
            IF NOT EXISTS (SELECT 1 FROM Crops WHERE name = p_crop) THEN
                INSERT INTO Crops(name) VALUES(p_crop);
            END IF;

            -- Insert the agricultural data
            INSERT INTO AgricultureData (
                country_id, crop_id, year, yield, rainfall, pesticides, temperature
            )
            VALUES (
                (SELECT country_id FROM Countries WHERE name = p_country),
                (SELECT crop_id FROM Crops WHERE name = p_crop),
                p_year, p_yield, p_rainfall, p_pesticides, p_temp
            );
        END;
        $$;
        """)
        
        # Create yield_audit table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS yield_audit (
            audit_id SERIAL PRIMARY KEY,
            record_id INT REFERENCES AgricultureData(record_id) ON DELETE CASCADE,
            old_yield INT,
            new_yield INT,
            change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create the trigger function
        cursor.execute("""
        CREATE OR REPLACE FUNCTION log_yield_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.yield IS DISTINCT FROM NEW.yield THEN
                INSERT INTO yield_audit (record_id, old_yield, new_yield)
                VALUES (OLD.record_id, OLD.yield, NEW.yield);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
        
        # Drop the trigger if it exists
        cursor.execute("DROP TRIGGER IF EXISTS yield_update_trigger ON AgricultureData;")
        
        # Create the trigger
        cursor.execute("""
        CREATE TRIGGER yield_update_trigger
        AFTER UPDATE ON AgricultureData
        FOR EACH ROW
        EXECUTE FUNCTION log_yield_changes();
        """)

        # Create predictions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Predictions (
        prediction_id SERIAL PRIMARY KEY,
        record_id INT NOT NULL,
        predicted_yield FLOAT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (record_id) REFERENCES AgricultureData(record_id) ON DELETE CASCADE
        );
        """)
        
        # Commit changes
        conn.commit()
        print("Database structure created successfully!")
        
    except psycopg2.Error as e:
        print(f"Error creating database structure: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database_structure()
    