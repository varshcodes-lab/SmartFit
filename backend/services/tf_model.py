import cv2
import base64
import numpy as np

import mediapipe as mp



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
    Analyze pose from image, draw skeleton, return score + feedback + skeleton image
    """

    if image is None:
        return {
            "exercise": exercise,
            "score": 0,
            "feedback": "Invalid image",
        }

    
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    annotated_image = image.copy()

    if not results.pose_landmarks:
        return {
            "exercise": exercise,
            "score": 0,
            "feedback": "No person detected. Please retry with a clear image.",
        }

    # Draw skeleton
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
    )

   
    score = 7

    if exercise.lower() == "squat":
        feedback = "Good squat posture. Keep knees outward and back straight."
    elif exercise.lower() == "pushup":
        feedback = "Nice push-up form. Maintain a straight body line."
    elif exercise.lower() == "pullup":
        feedback = "Good pull-up control. Avoid swinging."
    else:
        feedback = "Exercise detected. Keep consistent posture."

   
    success, buffer = cv2.imencode(".jpg", annotated_image)
    if not success:
        return {
            "exercise": exercise,
            "score": score,
            "feedback": feedback,
        }

    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "exercise": exercise,
        "score": score,
        "feedback": feedback,
        "image": image_base64,
    }
