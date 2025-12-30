from fastapi import APIRouter
from backend.services.diet_engine import recommend_diet

router = APIRouter()

@router.get("/")
def diet(weight: float, height: float):
    bmi = weight / (height ** 2)
    return {
        "bmi": round(bmi, 2),
        "diet_plan": recommend_diet(bmi)
    }
