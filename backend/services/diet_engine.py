from typing import List, Dict




def calculate_bmi(weight: float, height: float) -> float:
    """
    BMI = weight (kg) / height^2 (m)
    """
    return round(weight / (height ** 2), 2)


def recommend_diet(bmi: float) -> str:
    """
    Diet type based on BMI
    """
    if bmi < 18.5:
        return "High Protein Muscle Gain Diet"
    elif bmi <= 24.9:
        return "Balanced Fitness Diet"
    else:
        return "Low Carb Weight Loss Diet"




def estimate_calories(workouts: List[Dict]) -> int:
    """
    Rough calorie estimation based on exercise type and reps
    """
    calories = 0

    for w in workouts:
        exercise = w.get("exercise", "").lower()
        reps = int(w.get("reps", 1))

        if exercise == "squat":
            calories += reps * 0.5
        elif exercise == "pushup":
            calories += reps * 0.4
        elif exercise == "pullup":
            calories += reps * 0.7
        else:
            calories += reps * 0.3

    return int(calories)



def diet_recommendation(
    workouts: List[Dict],
    weight: float | None = None,
    height: float | None = None
) -> Dict:
    """
    Combines BMI + workout data to generate diet advice
    """

    calories_burned = estimate_calories(workouts)

    
    diet_type = "Balanced Fitness Diet"
    bmi = None

    if weight and height:
        bmi = calculate_bmi(weight, height)
        diet_type = recommend_diet(bmi)

    
    protein = round(calories_burned * 0.3 / 4, 1)
    carbs = round(calories_burned * 0.5 / 4, 1)
    fats = round(calories_burned * 0.2 / 9, 1)

    return {
        "bmi": bmi,
        "diet_type": diet_type,
        "calories_burned": calories_burned,
        "recommended_intake": {
            "protein_grams": protein,
            "carbs_grams": carbs,
            "fats_grams": fats,
        },
        "hydration": "Drink 2.5–3 liters of water today",
        "timing": "Eat within 45–60 minutes post workout",
    }
