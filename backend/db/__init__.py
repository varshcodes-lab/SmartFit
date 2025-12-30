from backend.db.database import Base, engine
from backend.models.workouts import Workout

def init_db():
    Base.metadata.create_all(bind=engine)
