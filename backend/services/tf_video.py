import cv2
import mediapipe as mp
import numpy as np
import math

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = abs(radians * 180.0 / math.pi)
    if angle > 180:
        angle = 360 - angle

    return angle

def analyze_video(video_path: str, exercise: str = "squat"):
    cap = cv2.VideoCapture(video_path)

    reps = 0
    stage = None
    frame_count = 0
    last_rep_frame = 0
    MIN_FRAMES_BETWEEN_REPS = 15  

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if not results.pose_landmarks:
                continue

            lm = results.pose_landmarks.landmark

           
            if exercise == "squat":
                hip = (lm[23].x, lm[23].y)
                knee = (lm[25].x, lm[25].y)
                ankle = (lm[27].x, lm[27].y)

                angle = calculate_angle(hip, knee, ankle)

                if angle < 100:
                    stage = "down"

                if angle > 160 and stage == "down":
                    if frame_count - last_rep_frame > MIN_FRAMES_BETWEEN_REPS:
                        reps += 1
                        last_rep_frame = frame_count
                        stage = "up"

            
            elif exercise == "pushup":
                shoulder = (lm[11].x, lm[11].y)
                elbow = (lm[13].x, lm[13].y)
                wrist = (lm[15].x, lm[15].y)

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle < 90:
                    stage = "down"

                if angle > 160 and stage == "down":
                    if frame_count - last_rep_frame > MIN_FRAMES_BETWEEN_REPS:
                        reps += 1
                        last_rep_frame = frame_count
                        stage = "up"

            
            elif exercise == "pullup":
                shoulder = (lm[11].x, lm[11].y)
                elbow = (lm[13].x, lm[13].y)
                wrist = (lm[15].x, lm[15].y)

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 150:
                    stage = "down"

                if angle < 70 and stage == "down":
                    if frame_count - last_rep_frame > MIN_FRAMES_BETWEEN_REPS:
                        reps += 1
                        last_rep_frame = frame_count
                        stage = "up"

    cap.release()

    return {
        "success": True,
        "exercise": exercise,
        "frames": frame_count,
        "reps": reps
    }
