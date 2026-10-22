import pytest

from services.recommendation_engine import rank_exercises


def base_profile(**overrides):
    profile = {
        "goal": "muscle_gain",
        "experience": "beginner",
        "equipment": ["dumbbell"],
        "target_muscles": ["chest"],
        "preferences": ["upper body"],
        "workout_history": [],
    }
    profile.update(overrides)
    return profile


def test_recommendations_include_explanation_metadata():
    results = rank_exercises(base_profile(), limit=5)

    assert results

    for item in results:
        assert item.get("id")
        assert isinstance(item.get("reasons"), list)
        assert item.get("reasons")
        assert isinstance(item.get("score_breakdown"), dict)
        assert item.get("movement_pattern")
        assert isinstance(item.get("score"), (int, float))
        assert isinstance(item.get("selection_score"), (int, float))


def test_score_breakdown_matches_base_score():
    results = rank_exercises(base_profile(), limit=10)

    assert results

    for item in results:
        expected = round(
            max(0.0, sum(item["score_breakdown"].values())), 2
        )
        assert item["score"] == expected, item["id"]


def test_selection_score_does_not_overwrite_base_score():
    results = rank_exercises(
        base_profile(target_muscles=["chest", "triceps"]),
        limit=10,
    )

    assert results

    for item in results:
        expected = round(
            max(0.0, sum(item["score_breakdown"].values())), 2
        )
        assert item["score"] == expected, item["id"]


def test_high_performance_adjustment_is_recorded():
    results = rank_exercises(
        base_profile(performance_score=90),
        limit=10,
    )

    assert results

    for item in results:
        breakdown = item["score_breakdown"]
        assert breakdown["performance_adjustment"] == 2
        assert item["score"] == round(
            max(0.0, sum(breakdown.values())), 2
        )


def test_recent_exercise_penalty_is_explained():
    results = rank_exercises(
        base_profile(
            workout_history=[
                {"exercise": "push_up", "date": "2026-10-17", "reps": 10}
            ]
        ),
        limit=10,
    )

    assert results

    repeated = next(
        (item for item in results if item["id"] == "push_up"), None
    )

    assert repeated is not None
    assert repeated["score_breakdown"]["recent_exercise_penalty"] == -20
    assert any(
        "recently" in reason.lower()
        for reason in repeated["reasons"]
    )


def test_selection_score_is_numeric_and_non_negative():
    results = rank_exercises(base_profile(), limit=10)

    assert results

    for item in results:
        assert item["selection_score"] >= 0
        assert item["score"] >= 0
