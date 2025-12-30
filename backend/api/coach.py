from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone

from backend.db.database import SessionLocal
from backend.models.workouts import Workout
from backend.services.coach_ai import get_coach_response

router = APIRouter(prefix="/coach", tags=["SmartFit Coach"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CoachChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict] = None



def predict_habit(workouts):
    if not workouts:
        return "No Data", "Unknown"

    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)

    
    recent = []
    for w in workouts:
        created = w.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created >= last_7_days:
            recent.append(w)

    if len(recent) >= 4:
        habit = "Highly Consistent"
    elif len(recent) >= 2:
        habit = "Moderately Consistent"
    else:
        habit = "Irregular"

    last_workout = workouts[0].created_at
    if last_workout.tzinfo is None:
        last_workout = last_workout.replace(tzinfo=timezone.utc)

    gap_days = (now - last_workout).days
    risk = "High" if gap_days >= 3 else "Low"

    return habit, risk



def diet_recommendation(exercise, score, duration):
    base_calories = {
        "squat": 8,
        "pushup": 7,
        "pullup": 9,
    }

    burn_rate = base_calories.get(exercise, 6)
    duration = duration if duration and duration > 0 else 5

    calories_burned = burn_rate * duration

    if score >= 8:
        calories_burned *= 1.1
    elif score <= 5:
        calories_burned *= 0.9

    return {
        "calories_burned": int(calories_burned),
        "tip": "Include protein-rich foods and stay well hydrated today."
    }



@router.post("/chat")
def chat_with_coach(
    payload: CoachChatRequest = Body(...),
    db: Session = Depends(get_db)
):
    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == payload.user_id)
        .order_by(Workout.created_at.desc())
        .all()
    )

   
    if payload.context:
        workout_data = payload.context
    elif workouts:
        w = workouts[0]
        workout_data = {
            "exercise": w.exercise,
            "score": w.score,
            "reps": w.reps,
            "feedback": w.feedback,
            "duration": w.duration,
        }
    else:
        return {
            "reply": "I don’t see any workout data yet. Please analyze a workout first 💪"
        }

    habit, risk = predict_habit(workouts)
    diet = diet_recommendation(
        workout_data.get("exercise", "squat"),
        workout_data.get("score", 5),
        workout_data.get("duration", 5),
    )

    enriched_context = {
        **workout_data,
        "habit": habit,
        "risk": risk,
        "diet": diet,
    }

    reply = get_coach_response(enriched_context, payload.message)

    if not reply or reply.strip() == "":
        reply = "I couldn’t generate feedback right now. Please try again."

    return {"reply": reply}
