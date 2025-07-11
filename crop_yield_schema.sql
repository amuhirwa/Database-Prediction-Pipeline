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
