from sqlalchemy import Column, String, Integer, Date
from db.database import Base


class UserGamification(Base):
    __tablename__ = "user_gamification"

    user_id = Column(String, primary_key=True, index=True)
    total_points = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date, nullable=True)
