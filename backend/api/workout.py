from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.workouts import Workout
from schemas.workout import WorkoutCreate, WorkoutResponse

router = APIRouter(prefix="/workout", tags=["Workout"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/save", response_model=WorkoutResponse)
def save_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db)
):
    db_workout = Workout(**workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/history/{user_id}", response_model=list[WorkoutResponse])
def get_workout_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.created_at.desc())
        .all()
    )
