#Hand_tracking.py
#Hand Tracker with Enhanced Features


import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class HandTracker:
    def __init__(
        self,
        max_num_hands=2,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.7,
        model_complexity=0.6,  # 0.6 for speed, 1 for accuracy change as u wish
        smoothing_window=5 # Smoothing window for landmark history
    ):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.smoothing_window = smoothing_window
        # For each hand, keep history for smoothing
        self.landmark_history = [deque(maxlen=smoothing_window) for _ in range(max_num_hands)]

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        smoothed_landmarks = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Store & Smooth landmarks
                landmarks = np.array([(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark])
                self.landmark_history[idx].append(landmarks)
                # Compute average across history window
                smoothed = np.mean(self.landmark_history[idx], axis=0)
                smoothed_landmarks.append(smoothed)
        else:
            # Clear histories if no hands detected
            for hist in self.landmark_history:
                hist.clear()

        return frame, smoothed_landmarks

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(
        max_num_hands=2,
        min_detection_confidence=0.8,  # More robust detection
        min_tracking_confidence=0.7,   # More robust tracking
        model_complexity=1,            # High accuracy, if speed is sufficient
        smoothing_window=5             # Smoothing over 5 recent frames
    )

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        annotated_frame, smoothed_landmarks = tracker.process_frame(frame)
        # Optionally display smoothed landmarks (debugging or advanced overlays)

        cv2.imshow("Enhanced Hand Tracking", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# This code is a simple hand tracking application using MediaPipe.
# It captures video from the webcam, processes each frame to detect hands,
# and displays the annotated video with hand landmarks drawn.  
# Press 'q' to exit the application.
# Ensure you have the required libraries installed:
# LIBRARIY :- pip install opencv-python mediapipe
# Note: The webcam must be accessible for this code to run.
