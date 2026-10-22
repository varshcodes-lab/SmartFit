from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def sample_result():
    return {
        "goal": "muscle_gain",
        "experience": "beginner",
        "equipment": ["dumbbell"],
        "model": None,
        "recommendations": [
            {
                "id": "dumbbell_floor_press",
                "name": "Dumbbell Floor Press",
                "muscles": ["chest", "triceps"],
                "goals": ["muscle_gain", "strength"],
                "levels": ["beginner"],
                "equipment": ["dumbbell"],
                "difficulty": "beginner",
                "impact": "low",
                "description": "A dumbbell pressing exercise.",
                "score": 80.0,
                "selection_score": 80.0,
                "score_breakdown": {"goal": 20},
                "reasons": ["Matches the requested chest target."],
                "movement_pattern": "horizontal_push",
            }
        ],
        "explanation": "The exercise matches your goal and equipment.",
        "retrieved_knowledge": [],
        "sources": [],
        "warning": "General fitness information only.",
    }


def test_health_endpoint():
    response = client.get("/recommendations/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_preserves_recommendation_metadata():
    expected = sample_result()

    with patch(
        "api.recommendations.generate_recommendations",
        return_value=expected,
    ):
        response = client.post(
            "/recommendations/generate",
            json={
                "goal": "muscle_gain",
                "experience": "beginner",
                "equipment": ["dumbbell"],
                "target_muscles": ["chest"],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]
    assert body["recommendations"][0]["score_breakdown"]["goal"] == 20
    assert body["recommendations"][0]["movement_pattern"] == "horizontal_push"
    assert body["recommendations"][0]["reasons"]


def test_invalid_goal_returns_422():
    response = client.post(
        "/recommendations/generate",
        json={"goal": "marathon_training"},
    )
    assert response.status_code == 422


def test_invalid_experience_returns_422():
    response = client.post(
        "/recommendations/generate",
        json={"experience": "expert"},
    )
    assert response.status_code == 422


def test_value_error_returns_422():
    with patch(
        "api.recommendations.generate_recommendations",
        side_effect=ValueError("Unsupported goal"),
    ):
        response = client.post(
            "/recommendations/generate",
            json={"goal": "general_fitness"},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Unsupported goal"


def test_runtime_error_returns_503():
    with patch(
        "api.recommendations.generate_recommendations",
        side_effect=RuntimeError("Service unavailable"),
    ):
        response = client.post(
            "/recommendations/generate",
            json={"goal": "general_fitness"},
        )

    assert response.status_code == 503


def test_unexpected_error_returns_safe_502():
    with patch(
        "api.recommendations.generate_recommendations",
        side_effect=Exception("internal details"),
    ):
        response = client.post(
            "/recommendations/generate",
            json={"goal": "general_fitness"},
        )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Recommendation service failed. Check backend logs."
    )
    assert "internal details" not in response.text


def test_api_preserves_complete_recommendation_metadata():
    expected = sample_result()

    with patch(
        "api.recommendations.generate_recommendations",
        return_value=expected,
    ):
        response = client.post(
            "/recommendations/generate",
            json={
                "goal": "muscle_gain",
                "experience": "beginner",
                "equipment": ["dumbbell"],
                "target_muscles": ["chest"],
            },
        )

    assert response.status_code == 200

    item = response.json()["recommendations"][0]

    assert item["score"] == 80.0
    assert item["selection_score"] == 80.0
    assert item["score_breakdown"] == {"goal": 20}
    assert item["reasons"] == ["Matches the requested chest target."]
    assert item["movement_pattern"] == "horizontal_push"
    assert item["equipment"] == ["dumbbell"]


def test_api_preserves_bodyweight_equipment_explanation():
    expected = sample_result()
    expected["recommendations"][0]["id"] = "push_up"
    expected["recommendations"][0]["name"] = "Push-Up"
    expected["recommendations"][0]["equipment"] = ["none"]
    expected["recommendations"][0]["reasons"] = [
        "can be performed without equipment"
    ]

    with patch(
        "api.recommendations.generate_recommendations",
        return_value=expected,
    ):
        response = client.post(
            "/recommendations/generate",
            json={
                "goal": "muscle_gain",
                "experience": "beginner",
                "equipment": ["dumbbell"],
                "target_muscles": ["chest"],
            },
        )

    assert response.status_code == 200

    item = response.json()["recommendations"][0]

    assert item["equipment"] == ["none"]
    assert "can be performed without equipment" in item["reasons"]
    assert "uses equipment you have available" not in item["reasons"]
