import cv2
import mediapipe as mp

def analyze_pose(image_path: str):
    # Lazy initialization (CRITICAL)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)

    image = cv2.imread(image_path)
    if image is None:
        return {"error": "Invalid image path or image not found"}

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return {
            "pose_detected": False,
            "message": "No human pose detected"
        }

    landmarks_count = len(results.pose_landmarks.landmark)

    return {
        "pose_detected": True,
        "landmarks_detected": landmarks_count,
        "status": "Posture analyzed successfully"
    }
