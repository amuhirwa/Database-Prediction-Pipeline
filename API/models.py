from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CountryCreate(BaseModel):
    name: str

class CropCreate(BaseModel):
    name: str

class AgricultureDataCreate(BaseModel):
    country_name: str
    crop_name: str
    year: int
    yield_value: Optional[int] = None
    rainfall: Optional[float] = None
    pesticides: Optional[float] = None
    temperature: Optional[float] = None

    @validator('year')
    def validate_year(cls, v):
        if v < 1900 or v > datetime.now().year:
            raise ValueError('Year must be between 1900 and current year')
        return v

    @validator('yield_value', 'rainfall', 'pesticides')
    def validate_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and (v < -50 or v > 60):
            raise ValueError('Temperature must be between -50 and 60 °C')
        return v

class AgricultureDataResponse(AgricultureDataCreate):
    record_id: int
    country_id: int
    crop_id: int

class PredictionCreate(BaseModel):
    record_id: int
    predicted_yield: float

class PredictionResponse(PredictionCreate):
    prediction_id: int
    created_at: datetime
