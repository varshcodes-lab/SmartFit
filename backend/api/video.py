from fastapi import APIRouter, UploadFile, File, Query
import tempfile
import shutil
from services.video_pose import analyze_video
from services.rep_counter import count_reps

router = APIRouter(prefix="/video", tags=["Video Analysis"])

@router.post("/analyze")
async def analyze_video_api(
    file: UploadFile = File(...),
    exercise: str = Query("squat")
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    result = analyze_video(tmp_path, exercise)

    return {
        "success": True,
        "frames": result["frames_processed"],
        "exercise": exercise,
        "data_preview": result["data"][:10]  
    }
