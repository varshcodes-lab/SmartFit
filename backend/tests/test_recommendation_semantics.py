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


def test_target_muscle_reasons_match_catalog_muscles():
    profile = base_profile(
        target_muscles=["chest", "triceps"],
    )
    results = rank_exercises(profile, limit=25)

    requested = set(profile["target_muscles"])

    for item in results:
        reasons = [
            reason for reason in item["reasons"]
            if reason.startswith("targets ")
        ]

        for reason in reasons:
            claimed = {
                muscle.strip()
                for muscle in reason[len("targets "):].split(",")
            }

            assert claimed
            assert claimed <= set(item.get("muscles", []))
            assert claimed <= requested


def test_goal_reason_requires_catalog_goal_match():
    results = rank_exercises(base_profile(), limit=25)

    for item in results:
        if "matches your fitness goal" in item["reasons"]:
            assert "muscle_gain" in item.get("goals", [])


def test_experience_reason_matches_catalog_difficulty():
    profile = base_profile(experience="beginner")
    results = rank_exercises(profile, limit=25)

    difficulty = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3,
    }
    user_level = difficulty[profile["experience"]]

    for item in results:
        reasons = item["reasons"]
        exercise_level = difficulty[item["difficulty"]]

        if "matches your experience level" in reasons:
            assert exercise_level == user_level

        if (
            "offers a lower-complexity option for your experience level"
            in reasons
        ):
            assert exercise_level < user_level

        if (
            "may be challenging for your current experience level"
            in reasons
        ):
            assert exercise_level > user_level


def test_equipment_compliance_for_every_returned_exercise():
    profiles = [
        base_profile(equipment=["none"]),
        base_profile(equipment=["dumbbell"]),
        base_profile(equipment=["resistance_band"]),
    ]

    for profile in profiles:
        available = set(profile["equipment"])
        results = rank_exercises(profile, limit=25)

        for item in results:
            required = set(item.get("equipment", []))

            assert (
                required == {"none"}
                or required <= available
            ), f"{item['id']} requires {required}, available: {available}"


def test_high_performance_bonus_has_an_explanation():
    results = rank_exercises(
        base_profile(performance_score=90),
        limit=25,
    )

    for item in results:
        if item["score_breakdown"]["performance_adjustment"] == 2:
            assert any(
                "performance" in reason.lower()
                for reason in item["reasons"]
            ), f"Missing performance explanation for {item['id']}"


def test_equipment_reason_is_not_claimed_for_unavailable_equipment():
    profile = base_profile(equipment=["none"])
    results = rank_exercises(profile, limit=25)

    for item in results:
        assert set(item.get("equipment", [])) == {"none"}

        if "uses equipment you have available" in item["reasons"]:
            assert set(item.get("equipment", [])) == {"none"}


def test_equipment_explanations_match_exercise_requirements():
    profiles = [
        base_profile(equipment=["none"]),
        base_profile(equipment=["dumbbell"]),
        base_profile(equipment=["resistance_band"]),
    ]

    for profile in profiles:
        results = rank_exercises(profile, limit=25)

        for item in results:
            reasons = item["reasons"]
            required = set(item.get("equipment", []))

            if required == {"none"}:
                assert (
                    "uses equipment you have available" not in reasons
                ), f"{item['id']} needs no equipment but claims it uses equipment"

            else:
                assert (
                    "uses equipment you have available" in reasons
                ), f"{item['id']} requires {required} but has no equipment explanation"
