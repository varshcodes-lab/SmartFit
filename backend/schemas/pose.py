from pydantic import BaseModel

class PoseResponse(BaseModel):
    pose_detected: bool
    landmarks_detected: int | None = None
    status: str | None = None
    error: str | None = None
