from pydantic import BaseModel

class PerformanceResponse(BaseModel):
    score: float
