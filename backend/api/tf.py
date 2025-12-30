from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from services.tf_model import predict_intensity
from db.database import SessionLocal
from models.workouts import Workout

router = APIRouter(prefix="/tf", tags=["Pose Analysis"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    exercise: str = Query("squat"),
    user_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Analyze exercise image and auto-save workout
    """

    try:
        
        image_bytes = await file.read()

        
        result = predict_intensity(image_bytes, exercise)

        score = int(result.get("score", 0))
        reps = int(result.get("reps", 1))
        feedback = result.get("feedback", "")

        workout = Workout(
            user_id=user_id,
            exercise=exercise,
            reps=reps,
            score=score,
            feedback=feedback,
            duration=0,
        )

        db.add(workout)
        db.commit()
        db.refresh(workout)

        return {
            "success": True,
            "message": "Workout analyzed and saved",
            "result": result,
            "workout": {
                "id": workout.id,
                "user_id": user_id,
                "exercise": exercise,
                "score": score,
                "reps": reps,
                "feedback": feedback,
                "created_at": workout.created_at,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
