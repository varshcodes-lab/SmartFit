import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def run_workout_tracker():
    cap = cv2.VideoCapture(0)
    reps = 0
    stage = "up"

    with mp_pose.Pose(min_detection_confidence=0.6,
                      min_tracking_confidence=0.6) as pose:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                lm = results.pose_landmarks.landmark
                hip = [lm[23].x, lm[23].y]
                knee = [lm[25].x, lm[25].y]
                ankle = [lm[27].x, lm[27].y]

                angle = calculate_angle(hip, knee, ankle)

                if angle < 100:
                    stage = "down"
                if angle > 160 and stage == "down":
                    reps += 1
                    stage = "up"

                cv2.putText(image, f"Reps: {reps}",
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0), 2)
            except:
                pass

            mp_draw.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow("SmartFit AI Gym Trainer", image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_workout_tracker()
