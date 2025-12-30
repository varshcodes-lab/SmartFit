from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    exercise = Column(String, index=True)
    reps = Column(Integer)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
