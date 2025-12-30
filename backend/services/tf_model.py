import cv2
import mediapipe as mp
import numpy as np
import base64

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def predict_intensity(image: np.ndarray, exercise: str):
    """
    Uses MediaPipe Pose + OpenCV
    Always returns:
    - score
    - reps
    - feedback
    - image (BASE64 skeleton image)
    """

    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    )

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    annotated_image = image.copy()

    if not results.pose_landmarks:
        return {
            "exercise": exercise,
            "score": 0,
            "reps": 0,
            "feedback": "Invalid image",
            "image": None,
        }

    
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
    )

   
    score = 7
    reps = 1

    feedback_map = {
        "squat": "Good squat posture. Keep knees outward and back straight.",
        "pushup": "Good push-up form. Maintain a straight body line.",
        "pullup": "Good pull-up form. Avoid swinging.",
    }

    feedback = feedback_map.get(exercise, "Good form.")

    
    _, buffer = cv2.imencode(".jpg", annotated_image)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "exercise": exercise,
        "score": score,
        "reps": reps,
        "feedback": feedback,
        "image": image_base64,
    }
