from datetime import datetime, timedelta, timezone
from typing import List


def predict_habit(workouts: List):
    """
    Predicts user's fitness habit using last 7 days of workouts.
    Safe for PostgreSQL timezone-aware datetimes.
    """

    if not workouts:
        return (
            "Inactive",
            "High",
            "No workouts recorded yet. Start with short sessions 💪"
        )

    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)

    recent_workouts = []

    for w in workouts:
        created_at = w.created_at

        
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        if created_at >= last_7_days:
            recent_workouts.append(created_at.date())

    days_worked = len(set(recent_workouts))

    if days_worked >= 5:
        return (
            "Consistent",
            "Low",
            "Excellent consistency! Keep pushing 🚀"
        )

    if 3 <= days_worked <= 4:
        return (
            "Irregular",
            "Medium",
            "You’re doing okay, but aim for 4–5 workouts per week."
        )

    return (
        "At Risk",
        "High",
        "Low activity detected. Try light workouts to rebuild momentum."
    )
