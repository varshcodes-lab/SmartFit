from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from models.workouts import Workout
from schemas.workout import WorkoutCreate, WorkoutResponse
from services.gamification_service import award_workout_points

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
    db: Session = Depends(get_db),
):
    try:
        db_workout = Workout(**workout.dict())
        db.add(db_workout)
        db.flush()

        # The workout and its points are committed together.
        award_workout_points(db, workout.user_id)

        db.commit()
        db.refresh(db_workout)
        return db_workout
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save workout and update points.",
        ) from exc


@router.get("/history/{user_id}", response_model=list[WorkoutResponse])
def get_workout_history(
    user_id: str,
    db: Session = Depends(get_db),
):
    return (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.created_at.desc())
        .all()
    )
