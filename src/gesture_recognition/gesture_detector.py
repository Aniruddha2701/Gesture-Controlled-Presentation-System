# gesture_detector.py

import numpy as np

class GestureDetector:
    """
    Detects simple static hand gestures based on numpy arrays of hand landmarks.
    Each hand landmarks input is a numpy array of shape (21, 3) containing normalized x,y,z.

    Landmarks order follows MediaPipe convention:
    0: wrist, 1-4: thumb, 5-8: index, 9-12: middle, 13-16: ring, 17-20: pinky
    """

    def __init__(self):
        # Indexes of relevant landmarks for fingertip and PIP joints
        self.FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb tip, Index tip, Middle tip, Ring tip, Pinky tip
        self.FINGER_PIPS = [3, 6, 10, 14, 18]  # Thumb IP, Index PIP, Middle PIP, Ring PIP, Pinky PIP

    def fingers_up(self, landmarks_np: np.ndarray) -> list:
        """
        Determine which fingers are up (extended).

        :param landmarks_np: np.ndarray shape (21,3) with x,y,z normalized coords
        :return: List of bools [thumb, index, middle, ring, pinky]
        """
        fingers = []

        # Thumb: check if tip.x is to left of IP joint.x (for right hand)
        # You might want to adapt this if you anticipate left hand usage.
        if landmarks_np[4][0] < landmarks_np[3][0]:
            fingers.append(True)
        else:
            fingers.append(False)

        # For other fingers: fingertip y should be less (higher) than PIP joint y to count as up
        for tip_idx, pip_idx in zip(self.FINGER_TIPS[1:], self.FINGER_PIPS[1:]):
            if landmarks_np[tip_idx][1] < landmarks_np[pip_idx][1]:
                fingers.append(True)
            else:
                fingers.append(False)

        return fingers

    def detect_gesture(self, landmarks_np: np.ndarray) -> str | None:
        """
        Classify gestures based on fingers up.

        :param landmarks_np: np.ndarray shape (21,3)
        :return: Gesture name string or None if no match
        """
        fingers = self.fingers_up(landmarks_np)

        # Open Palm: all fingers up
        if all(fingers):
            return "Open Palm"

        # Fist: no fingers up
        if not any(fingers):
            return "Fist"

        # Thumbs Up: thumb up, others down
        if fingers[0] and not any(fingers[1:]):
            return "Thumbs Up"

        # Peace sign: index and middle up, others down
        if fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
            return "Peace"

        # You can add more gestures here by defining patterns of extended fingers.

        return None
        