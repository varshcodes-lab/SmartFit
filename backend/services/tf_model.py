import cv2
import mediapipe as mp
import numpy as np
import base64
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    """
    Calculate angle between three points
    Angle at point b
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
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return {
                "exercise": exercise,
                "pose_detected": False,
                "score": 0,
                "feedback": "No human pose detected",
                "image": None
            }

        landmarks = results.pose_landmarks.landmark

        
        shoulder = (
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        )
        elbow = (
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y
        )
        wrist = (
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y
        )
        hip = (
            landmarks[mp_pose.PoseLandmark.LEFT_HIP].x,
            landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
        )
        knee = (
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x,
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y
        )
        ankle = (
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x,
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y
        )

        score = 0
        feedback = []

        
        if exercise == "squat":
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)

            score = 30

            if knee_angle < 100:
                score += 40
                feedback.append("Good squat depth")
            else:
                feedback.append("Go deeper in squat")

            if hip_angle < 120:
                score += 30
                feedback.append("Good hip posture")
            else:
                feedback.append("Lean forward less")

            form = "Good Squat" if score >= 70 else "Bad Squat"

            result_data = {
                "knee_angle": knee_angle,
                "hip_angle": hip_angle,
                "form": form
            }

      
        elif exercise == "pushup":
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            body_angle = calculate_angle(shoulder, hip, ankle)

            score = 40

            if elbow_angle < 90:
                score += 40
                feedback.append("Good depth")
            else:
                feedback.append("Lower your body more")

            if body_angle > 165:
                score += 20
                feedback.append("Body straight")
            else:
                feedback.append("Keep body straight")

            form = "Good Push-up" if score >= 70 else "Bad Push-up"

            result_data = {
                "elbow_angle": elbow_angle,
                "body_angle": body_angle,
                "form": form
            }

       
        elif exercise == "pullup":
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            body_angle = calculate_angle(shoulder, hip, ankle)

            score = 40

            if elbow_angle < 70:
                score += 40
                feedback.append("Good pull height")
            else:
                feedback.append("Pull higher")

            if body_angle > 165:
                score += 20
                feedback.append("Body straight")
            else:
                feedback.append("Avoid swinging")

            form = "Good Pull-up" if score >= 70 else "Bad Pull-up"

            result_data = {
                "elbow_angle": elbow_angle,
                "body_angle": body_angle,
                "form": form
            }

        else:
            return {
                "exercise": exercise,
                "pose_detected": False,
                "score": 0,
                "feedback": "Unsupported exercise",
                "image": None
            }

        score = min(score, 100)

    
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        _, buffer = cv2.imencode(".jpg", annotated_image)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        return {
            "exercise": exercise,
            "pose_detected": True,
            "score": score,
            "feedback": ", ".join(feedback),
            "image": image_base64,
            **result_data
        }
