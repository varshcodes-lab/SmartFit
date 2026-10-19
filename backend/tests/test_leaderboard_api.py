from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.leaderboard import get_db, router
from db.database import Base
from models.gamification import UserGamification


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


def test_leaderboard_returns_expected_shape_and_current_user():
    client, SessionLocal, engine = make_client()
    try:
        db = SessionLocal()
        db.add_all([
            UserGamification(
                user_id="alice",
                total_points=100,
                current_streak=4,
                longest_streak=8,
            ),
            UserGamification(
                user_id="bob",
                total_points=50,
                current_streak=2,
                longest_streak=3,
            ),
        ])
        db.commit()
        db.close()

        response = client.get("/leaderboard?user_id=bob")
        assert response.status_code == 200
        data = response.json()

        assert set(data) == {"leaderboard", "current_user"}
        assert data["leaderboard"][0]["user_id"] == "alice"
        assert data["leaderboard"][0]["rank"] == 1
        assert data["leaderboard"][1]["user_id"] == "bob"
        assert data["leaderboard"][1]["rank"] == 2
        assert data["current_user"]["user_id"] == "bob"
        assert data["current_user"]["total_points"] == 50
    finally:
        engine.dispose()


def test_leaderboard_tie_breaks_by_longest_streak_then_user_id():
    client, SessionLocal, engine = make_client()
    try:
        db = SessionLocal()
        db.add_all([
            UserGamification(
                user_id="zoe",
                total_points=100,
                current_streak=2,
                longest_streak=5,
            ),
            UserGamification(
                user_id="alice",
                total_points=100,
                current_streak=1,
                longest_streak=5,
            ),
            UserGamification(
                user_id="bob",
                total_points=100,
                current_streak=3,
                longest_streak=7,
            ),
        ])
        db.commit()
        db.close()

        data = client.get("/leaderboard").json()
        assert [row["user_id"] for row in data["leaderboard"]] == [
            "bob", "alice", "zoe"
        ]
    finally:
        engine.dispose()


def test_unknown_current_user_returns_null():
    client, SessionLocal, engine = make_client()
    try:
        db = SessionLocal()
        db.add(UserGamification(
            user_id="alice",
            total_points=10,
            current_streak=1,
            longest_streak=1,
        ))
        db.commit()
        db.close()

        response = client.get("/leaderboard?user_id=unknown")
        assert response.status_code == 200
        assert response.json()["current_user"] is None
    finally:
        engine.dispose()


def test_empty_leaderboard_returns_empty_list():
    client, SessionLocal, engine = make_client()
    try:
        response = client.get("/leaderboard")
        assert response.status_code == 200
        assert response.json() == {
            "leaderboard": [],
            "current_user": None,
        }
    finally:
        engine.dispose()