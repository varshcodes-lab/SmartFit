from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import SessionLocal
from models.gamification import UserGamification

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_leaderboard(
    user_id: str | None = None,
    db: Session = Depends(get_db),
):
    profiles = (
        db.query(UserGamification)
        .order_by(
            UserGamification.total_points.desc(),
            UserGamification.longest_streak.desc(),
            UserGamification.user_id.asc(),
        )
        .all()
    )

    entries = [
        {
            "rank": index,
            "user_id": profile.user_id,
            "total_points": profile.total_points,
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak,
        }
        for index, profile in enumerate(profiles, start=1)
    ]

    current_user = next(
        (entry for entry in entries if entry["user_id"] == user_id),
        None,
    )

    return {
        "leaderboard": entries,
        "current_user": current_user,
    }
