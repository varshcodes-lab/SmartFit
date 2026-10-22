import pytest

from services.recommendation_engine import (
    generate_recommendations,
    rank_exercises,
    retrieve_knowledge,
)


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


def test_bodyweight_exercises_are_available_with_dumbbells():
    results = rank_exercises(base_profile(), limit=10)
    ids = {item["id"] for item in results}

    assert "push_up" in ids
    assert "bodyweight_squat" in ids
    assert "dumbbell_floor_press" in ids


def test_no_equipment_profile_gets_only_bodyweight_exercises():
    profile = base_profile(
        goal="general_fitness",
        equipment=["none"],
        target_muscles=["quadriceps", "glutes"],
        preferences=["lower body"],
    )

    results = rank_exercises(profile, limit=10)

    assert results
    assert all(
        set(item.get("equipment", [])) == {"none"}
        for item in results
    )


@pytest.mark.parametrize(
    ("equipment", "target", "expected_id"),
    [
        (["dumbbell"], ["chest"], "push_up"),
        (["resistance_band"], ["back"], "resistance_band_row"),
        (["none"], ["quadriceps", "glutes"], "bodyweight_squat"),
    ],
)
def test_targeted_profiles_rank_relevant_exercises(
    equipment, target, expected_id
):
    profile = base_profile(
        goal="general_fitness",
        equipment=equipment,
        target_muscles=target,
        preferences=[],
    )

    results = rank_exercises(profile, limit=5)

    assert results
    assert results[0]["id"] == expected_id


def test_score_breakdown_matches_base_score():
    results = rank_exercises(base_profile(), limit=5)

    assert results

    for item in results:
        breakdown = item["score_breakdown"]
        expected = round(max(0.0, sum(breakdown.values())), 2)
        assert item["score"] == expected


@pytest.mark.parametrize(
    ("query", "expected_id"),
    [
        ("Which exercises target chest muscles?", "chest_training_001"),
        ("What exercises can I do using dumbbells?", "equipment_matching_001"),
        ("Which rows train the back muscles?", "back_training_001"),
        (
            "What bodyweight exercises train quadriceps and glutes?",
            "lower_body_training_001",
        ),
        (
            "How should a beginner choose exercise difficulty?",
            "difficulty_selection_001",
        ),
        (
            "How should target muscles and preferences affect ranking?",
            "targeted_recommendations_001",
        ),
    ],
)
def test_knowledge_retrieval_returns_expected_document_first(
    query, expected_id
):
    results = retrieve_knowledge(query, limit=4)

    assert results
    assert results[0]["id"] == expected_id


def test_unsupported_goal_is_rejected():
    with pytest.raises(ValueError, match="Unsupported goal"):
        generate_recommendations(
            base_profile(goal="marathon_training")
        )


def test_unsupported_equipment_is_rejected():
    with pytest.raises(ValueError, match="Unsupported equipment"):
        generate_recommendations(
            base_profile(equipment=["kettlebell"])
        )
