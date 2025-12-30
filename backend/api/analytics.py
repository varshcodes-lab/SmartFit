from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import SessionLocal
from models.workouts import Workout

router = APIRouter(
    prefix="/workout",
    tags=["Workout Analytics"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats/{user_id}")
def get_workout_stats(user_id: str, db: Session = Depends(get_db)):
    total_workouts = (
        db.query(func.count(Workout.id))
        .filter(Workout.user_id == user_id)
        .scalar()
    )

    total_reps = (
        db.query(func.coalesce(func.sum(Workout.reps), 0))
        .filter(Workout.user_id == user_id)
        .scalar()
    )

    avg_score = (
        db.query(func.coalesce(func.avg(Workout.score), 0))
        .filter(Workout.user_id == user_id)
        .scalar()
    )

    by_exercise = (
        db.query(
            Workout.exercise,
            func.count(Workout.id).label("sessions"),
            func.sum(Workout.reps).label("total_reps"),
            func.avg(Workout.score).label("avg_score")
        )
        .filter(Workout.user_id == user_id)
        .group_by(Workout.exercise)
        .all()
    )

    exercise_stats = [
        {
            "exercise": e.exercise,
            "sessions": e.sessions,
            "total_reps": e.total_reps,
            "avg_score": round(e.avg_score, 2)
        }
        for e in by_exercise
    ]

    return {
        "user_id": user_id,
        "total_workouts": total_workouts,
        "total_reps": total_reps,
        "average_score": round(avg_score, 2),
        "exercise_breakdown": exercise_stats
    }
