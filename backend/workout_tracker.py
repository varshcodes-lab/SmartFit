
import cv2
import mediapipe as mp
import numpy as np
from collections import deque

# --------------------------------------------------
# MEDIAPIPE SETUP
# --------------------------------------------------

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


# --------------------------------------------------
# CALCULATE JOINT ANGLE
# --------------------------------------------------

def calculate_angle(a, b, c):
    """
    Calculate the angle ABC in degrees.
    B is the joint (knee).
    """

    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)

    if denominator == 0:
        return None

    cosine = np.dot(ba, bc) / denominator
    cosine = np.clip(cosine, -1.0, 1.0)

    return float(np.degrees(np.arccos(cosine)))


# --------------------------------------------------
# SELECT THE MOST VISIBLE LEG
# --------------------------------------------------

def get_best_knee_angle(landmarks, min_visibility=0.60):
    """
    Evaluate both legs and use the leg whose hip, knee,
    and ankle are most reliably visible.
    """

    legs = {
        "Left": (23, 25, 27),
        "Right": (24, 26, 28)
    }

    best_result = None
    best_visibility = -1

    for side, ids in legs.items():
        hip_id, knee_id, ankle_id = ids

        hip_lm = landmarks[hip_id]
        knee_lm = landmarks[knee_id]
        ankle_lm = landmarks[ankle_id]

        visibility = min(
            hip_lm.visibility,
            knee_lm.visibility,
            ankle_lm.visibility
        )

        if visibility < min_visibility:
            continue

        hip = [hip_lm.x, hip_lm.y]
        knee = [knee_lm.x, knee_lm.y]
        ankle = [ankle_lm.x, ankle_lm.y]

        angle = calculate_angle(hip, knee, ankle)

        if angle is not None and visibility > best_visibility:
            best_visibility = visibility
            best_result = (angle, side, visibility)

    return best_result


# --------------------------------------------------
# MAIN WORKOUT TRACKER
# --------------------------------------------------

def run_workout_tracker():

    # Camera setup
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open your camera.")
        print("Check camera permissions or try another camera index.")
        return

    # Workout state
    reps = 0
    stage = "up"
    feedback = "Stand sideways and show your full body"

    # Angle smoothing
    angle_history = deque(maxlen=5)

    # Tune these thresholds based on observed angles
    DOWN_ANGLE = 110
    UP_ANGLE = 155

    # Landmark visibility requirement
    MIN_VISIBILITY = 0.60

    # Track whether pose was detected
    pose_detected = False

    print("SmartFit AI Squat Tracker started.")
    print("Stand sideways to the camera.")
    print("Press Q to quit.")

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as pose:

        while cap.isOpened():

            success, frame = cap.read()

            if not success:
                print("ERROR: Could not read a camera frame.")
                break

            # Mirror the camera for a natural preview
            frame = cv2.flip(frame, 1)

            # MediaPipe requires RGB input
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False

            results = pose.process(rgb)

            rgb.flags.writeable = True

            angle = None
            selected_leg = None
            visibility = None
            pose_detected = False

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                best_result = get_best_knee_angle(
                    landmarks,
                    MIN_VISIBILITY
                )

                if best_result is not None:

                    raw_angle, selected_leg, visibility = best_result
                    angle_history.append(raw_angle)

                    # Smooth small frame-to-frame fluctuations
                    angle = float(np.mean(angle_history))
                    pose_detected = True

                    # --------------------------------------
                    # REP COUNTING STATE MACHINE
                    # --------------------------------------

                    if stage == "up":

                        feedback = "Lower into your squat"

                        # Enter the down stage only after
                        # crossing the lower-angle threshold
                        if angle < DOWN_ANGLE:
                            stage = "down"
                            feedback = "Good! Now stand up"

                    elif stage == "down":

                        feedback = "Stand up to complete the rep"

                        # Count one rep after returning to
                        # the standing position
                        if angle > UP_ANGLE:
                            reps += 1
                            stage = "up"
                            feedback = "Rep completed!"

                else:
                    feedback = (
                        "Show your hip, knee and ankle clearly"
                    )
                    angle_history.clear()

                # Draw detected skeleton
                mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            else:
                feedback = "Move into the camera view"
                angle_history.clear()

            # ----------------------------------------------
            # DISPLAY WORKOUT INFORMATION
            # ----------------------------------------------

            cv2.putText(
                frame,
                f"Reps: {reps}",
                (25, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame,
                f"Stage: {stage.upper()}",
                (25, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 0),
                2
            )

            if angle is not None:

                cv2.putText(
                    frame,
                    f"Knee Angle: {angle:.1f} deg",
                    (25, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Tracking: {selected_leg} leg",
                    (25, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

            # Feedback
            cv2.putText(
                frame,
                feedback,
                (25, 205),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

            # Threshold guide
            cv2.putText(
                frame,
                f"Down < {DOWN_ANGLE} deg | Up > {UP_ANGLE} deg",
                (25, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )

            cv2.imshow("SmartFit AI Gym Trainer", frame)

            # Quit when Q is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    print("\nWorkout Summary")
    print("----------------")
    print(f"Total squats completed: {reps}")


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_workout_tracker()
