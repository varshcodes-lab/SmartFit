import os
from openai import OpenAI
from typing import Dict

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


def get_coach_response(workout: Dict, user_message: str) -> str:
    """
    Generates AI coach feedback with posture, habit, and diet insights.
    Fully safe and will not crash the backend.
    """
    try:
        exercise = workout.get("exercise", "exercise")
        score = workout.get("score", "N/A")
        reps = workout.get("reps", "N/A")
        feedback = workout.get("feedback", "")
        habit = workout.get("habit", "Unknown")
        risk = workout.get("risk", "Unknown")
        diet = workout.get("diet", {})

        prompt = f"""
You are a professional AI fitness coach.

Workout details:
- Exercise: {exercise}
- Score: {score}
- Reps: {reps}
- Feedback: {feedback}

Fitness habit analysis:
- Consistency: {habit}
- Drop-off risk: {risk}

Diet & calorie insight:
- Estimated calories burned: {diet.get("calories_burned", "N/A")}
- Nutrition tip: {diet.get("tip", "")}

User question:
"{user_message}"

Respond with:
1. A brief posture explanation
2. One correction or improvement tip
3. One habit insight
4. One diet or nutrition suggestion
Use an encouraging and friendly tone.
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.6,
        )

        reply_text = response.output_text

        if not reply_text or reply_text.strip() == "":
            return "I couldn’t generate feedback this time. Please try again."

        return reply_text.strip()

    except Exception as e:
        return f"Coach error: {str(e)}"
