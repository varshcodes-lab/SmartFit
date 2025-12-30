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


def predict_intensity(image_bytes: bytes, exercise: str):
    """
    Analyze pose image, draw skeleton, return score + base64 image
    """

    
    np_img = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if image is None:
        return {
            "exercise": exercise,
            "score": 0,
            "reps": 0,
            "feedback": "Invalid image",
            "image": None
        }

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    score = 0
    feedback = "Pose not detected"

    if results.pose_landmarks:
       
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2),
        )

        
        score = 7
        feedback = f"Good {exercise} posture. Keep knees outward and back straight."

    
    _, buffer = cv2.imencode(".jpg", image)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "exercise": exercise,
        "score": score,
        "reps": 1,
        "feedback": feedback,
        "image": image_base64
    }
