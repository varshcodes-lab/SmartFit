from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from services.pose_detector import analyze_pose
from schemas.pose import PoseResponse

router = APIRouter(tags=["Pose"])

class PoseResponse(BaseModel):
    pose_detected: bool = Field(..., example=True)
    landmarks_detected: int = Field(..., example=33)
    status: str = Field(..., example="Pose analyzed successfully")

@router.get("/", response_model=PoseResponse)
def pose():
    return analyze_pose("sample_pose.jpg")

def detect_pose(
    image_path: str = Query(..., description="Path to image file")
):
    result = analyze_pose(image_path)
    return result
