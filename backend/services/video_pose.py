import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

def analyze_video(video_path, exercise="squat"):
    cap = cv2.VideoCapture(video_path)

    pose = mp_pose.Pose(static_image_mode=False)

    frame_results = []
    frame_index = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        frame_data = {
            "frame": frame_index,
            "pose_detected": False
        }

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            
            hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
            ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

            angle = calculate_angle(
                (hip.x, hip.y),
                (knee.x, knee.y),
                (ankle.x, ankle.y)
            )

            frame_data.update({
                "pose_detected": True,
                "knee_angle": angle
            })

        frame_results.append(frame_data)
        frame_index += 1

    cap.release()
    pose.close()

    return {
        "exercise": exercise,
        "frames_processed": frame_index,
        "data": frame_results
    }


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)
