from fastapi import APIRouter
from backend.services.smart_gym_iot import get_iot_data

router = APIRouter()

@router.get("/")
def iot_data():
    data = get_iot_data()
    return {
        "sensor_data": data,
        "suggestion": "Increase intensity" if data["heart_rate"] < 90 else "Maintain pace"
    }
