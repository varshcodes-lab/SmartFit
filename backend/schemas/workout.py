from pydantic import BaseModel
from datetime import datetime

class WorkoutCreate(BaseModel):
    user_id: str
    exercise: str
    score: int
    reps: int | None = None
    feedback: str

class WorkoutResponse(WorkoutCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
