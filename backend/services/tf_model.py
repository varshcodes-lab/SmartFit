import cv2
import mediapipe as mp
import base64
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def predict_intensity(image, exercise: str):
    """
    Run MediaPipe pose detection,
    draw skeleton,
    return score + feedback + base64 image
    """

    pose = mp_pose.Pose(static_image_mode=True)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return {
            "exercise": exercise,
            "score": 0,
            "reps": 0,
            "feedback": "No human pose detected",
            "image": None,
        }

    
    annotated = image.copy()
    mp_drawing.draw_landmarks(
        annotated,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
    )

    
    _, buffer = cv2.imencode(".jpg", annotated)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    
    score = 7
    reps = 1

    feedback_map = {
        "squat": "Good squat posture. Keep knees outward and back straight.",
        "pushup": "Good pushup posture. Keep body straight and core tight.",
        "pullup": "Good pull-up form. Control your movement.",
    }

    return {
        "exercise": exercise,
        "score": score,
        "reps": reps,
        "feedback": feedback_map.get(exercise, "Good form"),
        "image": image_base64,   
    }
