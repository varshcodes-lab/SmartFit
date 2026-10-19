from db.database import Base, engine
from models.workouts import Workout
from models.gamification import UserGamification


def init_db():
    Base.metadata.create_all(bind=engine)
