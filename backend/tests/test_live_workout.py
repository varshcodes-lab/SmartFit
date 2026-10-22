import pytest
from types import SimpleNamespace

from services.live_workout import LiveWorkoutSession


def make_landmarks():
    return [
        SimpleNamespace(x=0.0, y=0.0, visibility=1.0)
        for _ in range(33)
    ]


@pytest.mark.parametrize(
    ("exercise", "angles"),
    [
        ("squat", [90, 90, 90, 90, 170, 170, 170, 170]),
        ("pushup", [90, 90, 90, 90, 170, 170, 170, 170]),
        ("pullup", [170, 170, 170, 170, 40, 40, 40, 40]),
    ],
)
def test_rep_counting_state_transitions(monkeypatch, exercise, angles):
    import services.live_workout as live_module

    session = LiveWorkoutSession(exercise=exercise)
    angle_iter = iter(angles)

    monkeypatch.setattr(
        live_module,
        "calculate_angle",
        lambda *_args: next(angle_iter),
    )

    landmarks = make_landmarks()

    for _ in range(4):
        session.process_landmarks(landmarks)

    assert session.reps == 1


def test_invisible_landmarks_do_not_count_a_rep():
    session = LiveWorkoutSession(exercise="squat")
    landmarks = make_landmarks()

    for index in (23, 25, 27, 24, 26, 28):
        landmarks[index].visibility = 0.1

    result = session.process_landmarks(landmarks)

    assert result["pose_detected"] is False
    assert session.reps == 0


def test_session_summary_for_no_frames():
    session = LiveWorkoutSession(exercise="squat")

    result = session.summary()

    assert result["exercise"] == "squat"
    assert result["reps"] == 0
    assert result["frames_analyzed"] == 0
