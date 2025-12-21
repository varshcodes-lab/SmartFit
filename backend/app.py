from fastapi import FastAPI
from backend.performance_engine import calculate_performance
from backend.diet_engine import recommend_diet
from backend.habit_tracker import predict_habit
from backend.gym_recommender import recommend_gyms
from backend.smart_gym_iot import get_iot_data
from backend.virtual_gym_buddy import chat_response


app = FastAPI(title="SmartFit AI Internship Backend")

@app.get("/")
def home():
    return {"status": "SmartFit AI Backend Running"}

@app.get("/performance")
def performance(correct: int, total: int, time: int):
    score = calculate_performance(correct, total, time)
    return {"Performance Score": score}

@app.get("/diet")
def diet(weight: float, height: float):
    bmi = calculate_bmi(weight, height)
    return {"BMI": round(bmi, 2), "Diet Plan": recommend_diet(bmi)}

@app.get("/habit")
def habit(days_gap: int, missed: int):
    prob = predict_skip_probability(days_gap, missed)
    return {"Skip Probability": prob}

@app.get("/buddy")
def buddy(message: str):
    return {"Response": gym_buddy_response(message)}

@app.get("/iot")
def iot():
    data = get_sensor_data()
    return {
        "Sensor Data": data,
        "Suggestion": workout_adjustment(data)
    }
