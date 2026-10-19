from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.gamification import UserGamification

APP_TIMEZONE = ZoneInfo("Asia/Kolkata")
DAILY_WORKOUT_POINTS = 10
STREAK_BONUSES = {3: 20, 7: 50, 30: 200}


def award_workout_points(
    db: Session, user_id: str, today: date | None = None
) -> UserGamification:
    """Award points once per IST calendar day."""
    if today is None:
        today = datetime.now(APP_TIMEZONE).date()

    profile = (
        db.query(UserGamification)
        .filter(UserGamification.user_id == user_id)
        .with_for_update()
        .first()
    )

    if profile is None:
        try:
            # A savepoint lets us recover from a concurrent first insert
            # without rolling back the enclosing workout transaction.
            with db.begin_nested():
                profile = UserGamification(
                    user_id=user_id,
                    total_points=0,
                    current_streak=0,
                    longest_streak=0,
                    last_activity_date=None,
                )
                db.add(profile)
                db.flush()
        except IntegrityError:
            profile = (
                db.query(UserGamification)
                .filter(UserGamification.user_id == user_id)
                .with_for_update()
                .one()
            )

    if profile.last_activity_date == today:
        return profile

    if profile.last_activity_date == today - timedelta(days=1):
        profile.current_streak += 1
    else:
        profile.current_streak = 1

    profile.total_points += DAILY_WORKOUT_POINTS
    profile.total_points += STREAK_BONUSES.get(profile.current_streak, 0)
    profile.longest_streak = max(
        profile.longest_streak, profile.current_streak
    )
    profile.last_activity_date = today

    db.flush()
    return profile
