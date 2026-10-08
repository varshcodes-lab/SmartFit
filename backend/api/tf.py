from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session
import cv2
import numpy as np

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
    Analyze exercise image using MediaPipe,
    draw skeleton, return result image,
    and auto-save workout to DB.
    """

    try:
        
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        
        result = predict_intensity(image, exercise)

        score = int(result.get("score", 0))
        reps = int(result.get("reps", 0))
        feedback = result.get("feedback", "")

        
        workout = Workout(
            user_id=user_id,
            exercise=exercise,
            score=score,
            reps=reps,
            feedback=feedback,
            duration=0,
        )

        db.add(workout)
        db.commit()
        db.refresh(workout)

       
        return {
            "success": True,
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
