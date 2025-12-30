from fastapi import APIRouter, UploadFile, File, Query, BackgroundTasks, HTTPException
import shutil
import os
import uuid

from backend.services.tf_video import analyze_video
from backend.db.database import SessionLocal
from backend.models.workouts import Workout

router = APIRouter(prefix="/tf", tags=["Video Analysis"])

video_jobs = {}


def process_video_job(job_id: str, video_path: str, exercise: str):
    db = SessionLocal()
    try:
        video_jobs[job_id]["status"] = "processing"

        result = analyze_video(video_path, exercise)

        
        workout = Workout(
            user_id="demo_user",
            exercise=exercise,
            reps=result.get("reps", 0),
            duration=result.get("frames", 0)
        )
        db.add(workout)
        db.commit()

        video_jobs[job_id]["status"] = "completed"
        video_jobs[job_id]["result"] = result

    except Exception as e:
        video_jobs[job_id]["status"] = "failed"
        video_jobs[job_id]["error"] = str(e)

    finally:
        db.close()
        if os.path.exists(video_path):
            os.remove(video_path)


@router.post("/analyze-video")
async def analyze_video_api(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    exercise: str = Query("squat")
):
    os.makedirs("temp", exist_ok=True)

    job_id = str(uuid.uuid4())
    video_path = f"temp/{job_id}_{file.filename}"

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video_jobs[job_id] = {
        "status": "queued",
        "result": None
    }

    background_tasks.add_task(
        process_video_job,
        job_id,
        video_path,
        exercise
    )

    return {
        "success": True,
        "job_id": job_id,
        "message": "Video analysis started"
    }


@router.get("/video-status/{job_id}")
def get_video_status(job_id: str):
    job = video_jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"]
    }


@router.get("/video-result/{job_id}")
def get_video_result(job_id: str):
    job = video_jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job['status']}"
        )

    return {
        "job_id": job_id,
        "result": job["result"]
    }
