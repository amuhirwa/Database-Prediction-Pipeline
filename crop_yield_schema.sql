-- Stores a list of countries involved in agricultural data
CREATE TABLE Countries (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Stores types of crops being tracked
CREATE TABLE Crops (
    crop_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Stores annual agricultural data per crop and country
CREATE TABLE AgricultureData (
    record_id SERIAL PRIMARY KEY,
    country_id INT REFERENCES Countries(country_id),
    crop_id INT REFERENCES Crops(crop_id),
    year INT NOT NULL,
    yield INT,
    rainfall FLOAT,
    pesticides FLOAT,
    temperature FLOAT
);


-- Procedure to insert agricultural data with validation.
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