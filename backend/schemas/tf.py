from pydantic import BaseModel

class TFResponse(BaseModel):
    predicted_intensity: str
    confidence: float
