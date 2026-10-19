from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.gamification import UserGamification
from services.gamification_service import award_workout_points


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, autocommit=False
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def record_days(db, count, start=date(2026, 1, 1)):
    profile = None
    for offset in range(count):
        profile = award_workout_points(
            db, "test_user", today=start + timedelta(days=offset)
        )
        db.flush()
    return profile


def test_first_workout_awards_10_points(db):
    profile = award_workout_points(
        db, "test_user", today=date(2026, 1, 1)
    )
    assert profile.total_points == 10
    assert profile.current_streak == 1
    assert profile.longest_streak == 1


def test_duplicate_same_day_does_not_award_points(db):
    day = date(2026, 1, 1)
    award_workout_points(db, "test_user", today=day)
    profile = award_workout_points(db, "test_user", today=day)

    assert profile.total_points == 10
    assert profile.current_streak == 1


@pytest.mark.parametrize(
    ("days", "expected_points"),
    [(3, 50), (7, 140), (30, 570)],
)
def test_streak_milestone_totals(db, days, expected_points):
    profile = record_days(db, days)

    assert profile.total_points == expected_points
    assert profile.current_streak == days
    assert profile.longest_streak == days


def test_missed_day_resets_current_streak_but_preserves_points(db):
    start = date(2026, 1, 1)
    award_workout_points(db, "test_user", today=start)
    award_workout_points(db, "test_user", today=start + timedelta(days=1))
    before_gap = award_workout_points(
        db, "test_user", today=start + timedelta(days=2)
    )
    assert before_gap.current_streak == 3
    assert before_gap.total_points == 50

    after_gap = award_workout_points(
        db, "test_user", today=start + timedelta(days=4)
    )

    assert after_gap.current_streak == 1
    assert after_gap.longest_streak == 3
    assert after_gap.total_points == 60
