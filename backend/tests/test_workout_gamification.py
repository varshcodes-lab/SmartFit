from datetime import date
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.workout import get_db, router
from db.database import Base
from models.gamification import UserGamification
from models.workouts import Workout


def make_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app), TestingSessionLocal, engine


def test_saving_workout_persists_workout_and_awards_points():
    client, SessionLocal, engine = make_client()
    try:
        response = client.post(
            "/workout/save",
            json={
                "user_id": "test_user",
                "exercise": "squat",
                "score": 90,
                "reps": 10,
                "feedback": "Good form",
                "duration": 60,
            },
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == "test_user"
        assert response.json()["reps"] == 10

        db = SessionLocal()
        try:
            assert db.query(Workout).count() == 1
            profile = db.query(UserGamification).filter_by(
                user_id="test_user"
            ).one()
            assert profile.total_points == 10
            assert profile.current_streak == 1
        finally:
            db.close()
    finally:
        engine.dispose()


def test_multiple_workouts_same_day_only_award_points_once():
    client, SessionLocal, engine = make_client()
    try:
        payload = {
            "user_id": "test_user",
            "exercise": "squat",
            "score": 90,
            "reps": 10,
            "feedback": "Good form",
            "duration": 60,
        }

        first = client.post("/workout/save", json=payload)
        second = client.post("/workout/save", json=payload)

        assert first.status_code == 200
        assert second.status_code == 200

        db = SessionLocal()
        try:
            assert db.query(Workout).count() == 2
            profile = db.query(UserGamification).filter_by(
                user_id="test_user"
            ).one()
            assert profile.total_points == 10
            assert profile.current_streak == 1
        finally:
            db.close()
    finally:
        engine.dispose()


def test_failed_workout_insert_does_not_leave_points_behind():
    client, SessionLocal, engine = make_client()
    try:
        # reps is deliberately omitted. The API schema accepts it as optional,
        # but the database column is non-nullable, so the insert should fail.
        response = client.post(
            "/workout/save",
            json={
                "user_id": "failure_user",
                "exercise": "squat",
                "score": 90,
                "feedback": "Good form",
                "duration": 60,
            },
        )

        assert response.status_code == 500

        db = SessionLocal()
        try:
            assert db.query(Workout).count() == 0
            assert db.query(UserGamification).filter_by(
                user_id="failure_user"
            ).count() == 0
        finally:
            db.close()
    finally:
        engine.dispose()