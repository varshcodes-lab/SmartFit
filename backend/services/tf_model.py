import cv2
import mediapipe as mp
import numpy as np
import base64


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5
)


def predict_intensity(image: np.ndarray, exercise: str):
    """
    Input:
        image (np.ndarray): BGR OpenCV image
        exercise (str): squat / pushup / pullup

    Output:
        dict with score, reps, feedback, image(base64)
    """

   
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

   
    if not results.pose_landmarks:
        return {
            "exercise": exercise,
            "score": 0,
            "reps": 0,
            "feedback": "Invalid image",
            "image": None,
        }

    
    annotated = image.copy()
    mp_drawing.draw_landmarks(
        annotated,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
    )

    
    score = 7
    reps = 1

    if exercise.lower() == "squat":
        feedback = "Good squat posture. Keep knees outward and back straight."
    elif exercise.lower() == "pushup":
        feedback = "Good pushup posture. Keep body straight."
    elif exercise.lower() == "pullup":
        feedback = "Good pull-up form. Control the movement."
    else:
        feedback = "Exercise detected."

    
    _, buffer = cv2.imencode(".jpg", annotated)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "exercise": exercise,
        "score": score,
        "reps": reps,
        "feedback": feedback,
        "image": image_base64,
    }
