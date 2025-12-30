from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False, index=True)
    exercise = Column(String, nullable=False)

    reps = Column(Integer, nullable=False)

    duration = Column(Integer, default=0)

    score = Column(Integer, nullable=False)

    feedback = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
