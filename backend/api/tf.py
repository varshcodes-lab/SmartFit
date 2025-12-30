from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
import cv2
import numpy as np

from backend.services.tf_model import predict_intensity
from backend.db.database import SessionLocal
from backend.models.workouts import Workout

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
    exercise: str = Query(...),   
    db=Depends(get_db)
):
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        result = predict_intensity(image, exercise)

       
        workout = Workout(
            user_id="Varshith432",   
            exercise=exercise,
            reps=1,
            duration=0,
            score=result.get("score"),
            feedback=result.get("feedback")
        )

        db.add(workout)
        db.commit()

        return {
            "success": True,
            "filename": file.filename,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
