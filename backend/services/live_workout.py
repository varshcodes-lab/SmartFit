import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from services.tf_model import calculate_angle

mp_pose = mp.solutions.pose

# MediaPipe landmark indices
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28


@dataclass
class LiveWorkoutSession:
    exercise: str
    reps: int = 0
    state: str = "up"
    scores: List[float] = field(default_factory=list)
    feedback_counts: Dict[str, int] = field(default_factory=dict)
    last_score: float = 0
    last_feedback: str = "Position yourself in the camera view"
    last_angles: Dict[str, float] = field(default_factory=dict)

    def _point(self, landmarks, index: int) -> Tuple[float, float]:
        landmark = landmarks[index]
        return landmark.x, landmark.y

    def _visible(self, landmarks, indices, threshold=0.55) -> bool:
        return all(landmarks[i].visibility >= threshold for i in indices)

    def _average(self, values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _score_and_feedback(self, angle: float) -> Tuple[int, str]:
        if self.exercise == "squat":
            if 65 <= angle <= 100:
                return 95, "Excellent squat depth"
            if 100 < angle <= 120:
                return 78, "Good squat — try going slightly deeper"
            if angle > 120:
                return 45, "Bend your knees more"
            return 75, "Controlled squat"

        if self.exercise == "pushup":
            if 45 <= angle <= 75:
                return 95, "Excellent push-up depth"
            if 75 < angle <= 100:
                return 78, "Good push-up — go a little lower"
            if angle > 100:
                return 45, "Lower your body more"
            return 75, "Controlled push-up"

        if self.exercise == "pullup":
            if angle <= 55:
                return 95, "Great pull-up — strong top position"
            if angle <= 90:
                return 78, "Good pull-up — pull a little higher"
            return 45, "Pull your body higher"

        return 50, "Exercise not configured"

    def process_landmarks(self, landmarks) -> Dict:
        exercise = self.exercise

        if exercise == "squat":
            indices = [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]
            if not self._visible(landmarks, indices):
                return self._no_pose()

            left = calculate_angle(self._point(landmarks, LEFT_HIP), self._point(landmarks, LEFT_KNEE), self._point(landmarks, LEFT_ANKLE))
            right = calculate_angle(self._point(landmarks, RIGHT_HIP), self._point(landmarks, RIGHT_KNEE), self._point(landmarks, RIGHT_ANKLE))
            angle = self._average([left, right])
            self.last_angles = {"knee_angle": round(angle, 1), "left_knee_angle": round(left, 1), "right_knee_angle": round(right, 1)}

            score, feedback = self._score_and_feedback(angle)
            # A rep is counted after reaching the down position and returning to standing.
            if angle < 105 and self.state == "up":
                self.state = "down"
            elif angle > 160 and self.state == "down":
                self.reps += 1
                self.state = "up"

        elif exercise == "pushup":
            indices = [LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST]
            if not self._visible(landmarks, indices):
                return self._no_pose()

            left = calculate_angle(self._point(landmarks, LEFT_SHOULDER), self._point(landmarks, LEFT_ELBOW), self._point(landmarks, LEFT_WRIST))
            right = calculate_angle(self._point(landmarks, RIGHT_SHOULDER), self._point(landmarks, RIGHT_ELBOW), self._point(landmarks, RIGHT_WRIST))
            angle = self._average([left, right])
            self.last_angles = {"elbow_angle": round(angle, 1), "left_elbow_angle": round(left, 1), "right_elbow_angle": round(right, 1)}

            score, feedback = self._score_and_feedback(angle)
            if angle < 100 and self.state == "up":
                self.state = "down"
            elif angle > 160 and self.state == "down":
                self.reps += 1
                self.state = "up"

        elif exercise == "pullup":
            indices = [LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST]
            if not self._visible(landmarks, indices):
                return self._no_pose()

            left = calculate_angle(self._point(landmarks, LEFT_SHOULDER), self._point(landmarks, LEFT_ELBOW), self._point(landmarks, LEFT_WRIST))
            right = calculate_angle(self._point(landmarks, RIGHT_SHOULDER), self._point(landmarks, RIGHT_ELBOW), self._point(landmarks, RIGHT_WRIST))
            angle = self._average([left, right])
            self.last_angles = {"elbow_angle": round(angle, 1), "left_elbow_angle": round(left, 1), "right_elbow_angle": round(right, 1)}

            score, feedback = self._score_and_feedback(angle)
            if angle < 90 and self.state == "down":
                self.state = "up"
            elif angle > 150 and self.state == "up":
                self.reps += 1
                self.state = "down"

        else:
            score, feedback = 0, f"Unsupported exercise: {exercise}"

        self.last_score = score
        self.scores.append(score)
        self.feedback_counts[feedback] = self.feedback_counts.get(feedback, 0) + 1
        self.last_feedback = feedback

        return {
            "pose_detected": True,
            "exercise": exercise,
            "reps": self.reps,
            "state": self.state,
            "score": round(score),
            "average_score": round(sum(self.scores) / len(self.scores)),
            "feedback": feedback,
            "angles": self.last_angles,
        }

    def _no_pose(self) -> Dict:
        self.last_feedback = "Move into the camera view"
        return {
            "pose_detected": False,
            "exercise": self.exercise,
            "reps": self.reps,
            "state": self.state,
            "score": 0,
            "average_score": round(sum(self.scores) / len(self.scores)) if self.scores else 0,
            "feedback": self.last_feedback,
            "angles": self.last_angles,
        }

    def summary(self) -> Dict:
        average_score = round(sum(self.scores) / len(self.scores)) if self.scores else 0
        common_feedback = max(self.feedback_counts, key=self.feedback_counts.get) if self.feedback_counts else "No feedback available"
        return {
            "exercise": self.exercise,
            "reps": self.reps,
            "score": average_score,
            "average_score": average_score,
            "feedback": common_feedback,
            "frames_analyzed": len(self.scores),
        }


class LiveWorkoutAnalyzer:
    def __init__(self, exercise: str):
        self.session = LiveWorkoutSession(exercise=exercise)
        # Reuse one MediaPipe instance for the whole live session. This is much cheaper
        # than constructing a new model for every camera frame.
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.55,
            min_tracking_confidence=0.55,
        )

    def process_jpeg(self, jpeg_bytes: bytes) -> Dict:
        array = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            return {"pose_detected": False, "error": "Invalid frame"}

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if not results.pose_landmarks:
            return self.session._no_pose()

        response = self.session.process_landmarks(results.pose_landmarks.landmark)
        # Send only normalized landmarks. The frontend can draw the skeleton over the
        # local camera feed without receiving the video back from the server.
        response["landmarks"] = [
            {
                "x": round(lm.x, 5),
                "y": round(lm.y, 5),
                "visibility": round(float(lm.visibility), 3),
            }
            for lm in results.pose_landmarks.landmark
        ]
        return response

    def close(self):
        self.pose.close()
