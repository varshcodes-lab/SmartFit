import cv2
import mediapipe as mp
import numpy as np
import math
import base64

mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    """
    Calculate angle between three points
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = abs(radians * 180.0 / math.pi)
    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)


def predict_intensity(image, exercise="squat"):
    """
    Analyze a single image and return posture feedback
    """

    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return {
            "exercise": exercise,
            "score": 0,
            "feedback": "No human pose detected",
        }

    lm = results.pose_landmarks.landmark

    score = 0
    feedback = "Good posture"
    angles = {}

    
    if exercise == "squat":
        hip = (lm[23].x, lm[23].y)
        knee = (lm[25].x, lm[25].y)
        ankle = (lm[27].x, lm[27].y)

        knee_angle = calculate_angle(hip, knee, ankle)
        angles["knee_angle"] = knee_angle

        if knee_angle < 70:
            score = 90
            feedback = "Excellent squat depth!"
        elif knee_angle < 100:
            score = 70
            feedback = "Good squat, try going slightly deeper"
        else:
            score = 40
            feedback = "Bend your knees more for a proper squat"

    
    elif exercise == "pushup":
        shoulder = (lm[11].x, lm[11].y)
        elbow = (lm[13].x, lm[13].y)
        wrist = (lm[15].x, lm[15].y)

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        angles["elbow_angle"] = elbow_angle

        if elbow_angle < 60:
            score = 90
            feedback = "Excellent push-up depth!"
        elif elbow_angle < 90:
            score = 70
            feedback = "Good push-up, go a little lower"
        else:
            score = 40
            feedback = "Lower your body more during push-ups"

    
    elif exercise == "pullup":
        shoulder = (lm[11].x, lm[11].y)
        elbow = (lm[13].x, lm[13].y)
        wrist = (lm[15].x, lm[15].y)

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        angles["elbow_angle"] = elbow_angle

        if elbow_angle < 50:
            score = 90
            feedback = "Great pull-up form!"
        elif elbow_angle < 90:
            score = 70
            feedback = "Good pull-up, pull a bit higher"
        else:
            score = 40
            feedback = "Pull your chest closer to the bar"

  
    mp_drawing = mp.solutions.drawing_utils
    annotated = image.copy()
    mp_drawing.draw_landmarks(
        annotated,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    _, buffer = cv2.imencode(".jpg", annotated)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "exercise": exercise,
        "score": score,
        "feedback": feedback,
        "image": image_base64,
        **angles
    }
