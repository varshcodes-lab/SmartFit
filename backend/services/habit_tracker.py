import random

def predict_habit(workout_days):
    """
    Predicts fitness habit consistency based on workout frequency
    """
    if workout_days >= 5:
        return {
            "habit": "Highly Consistent",
            "confidence": "High"
        }
    elif workout_days >= 3:
        return {
            "habit": "Moderately Consistent",
            "confidence": "Medium"
        }
    else:
        return {
            "habit": "Needs Improvement",
            "confidence": "Low"
        }
