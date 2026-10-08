from fastapi import APIRouter

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)

@router.get("/joints")
def joint_metrics():
    return {
        "angles": {
            "elbow": 45,
            "knee": 90
        }
    }
