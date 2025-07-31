import numpy as np
from collections import deque
import time
import json
import os

# ------- Calibration settings loader -------
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings", "gesture_settings.json")
DEFAULT_SETTINGS = {
    "hold_duration_required": 0.8,
    "swipe_horizontal_threshold": 0.05,
    "scroll_vertical_threshold": 0.04,
    "finger_motion_cooldown": 0.8,
    "zoom_cooldown": 0.6,
    "smoothing_window": 5
}

def load_gesture_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
            return {**DEFAULT_SETTINGS, **data}
        except Exception as e:
            print(f"[WARN] Failed to load calibration: {e}")
    return DEFAULT_SETTINGS.copy()
# ------------------------------------------

class GestureDetector:
    """
    Robust gesture recognition:
    - Static: open palm, fist, thumbs up, peace, OK sign, number gestures
    - Instant: zoom (pinch/spread)
    - Dynamic: index & middle finger horizontal (slide) and vertical (scroll) gestures
    - Added static: L Gesture, Single Point, C-Shape, Rock Sign / Horns
    """

    def __init__(self):
        # Load calibration settings
        settings = load_gesture_settings()
        self.finger_motion_cooldown = settings["finger_motion_cooldown"]
        self.zoom_cooldown = settings["zoom_cooldown"]
        self.finger_motion_buffer = deque(maxlen=10)  # You could set maxlen to settings["smoothing_window"] if desired
        self.swipe_threshold = settings["swipe_horizontal_threshold"]
        self.scroll_threshold = settings["scroll_vertical_threshold"]

        self.FINGER_TIPS = [4, 8, 12, 16, 20]
        self.FINGER_PIPS = [3, 6, 10, 14, 18]

        self.last_finger_motion_time = 0

        # For zoom gesture history
        self.zoom_history = deque(maxlen=5)
        self.last_zoom_action_time = 0

    # --- Static Gestures Helper ---

    def fingers_up(self, l):
        fingers = []
        # Thumb: right hand logic
        fingers.append(l[4][0] < l[3][0])
        for ti, pi in zip(self.FINGER_TIPS[1:], self.FINGER_PIPS[1:]):
            fingers.append(l[ti][1] < l[pi][1])
        return fingers  # list of bools [thumb, index, middle, ring, pinky]

    def fingers_count(self, l):
        return sum(self.fingers_up(l))
    
    def is_fist(self, l):
        fingers = self.fingers_up(l)
        all_fingers_down = not any(fingers)
        thumb_tip = l[4][:2]
        wrist = l[0][:2]
        index_base = l[5][:2]
        thumb_dist = np.min([np.linalg.norm(thumb_tip - wrist), np.linalg.norm(thumb_tip - index_base)])
        return all_fingers_down or (not any(fingers[1:]) and thumb_dist < 0.09)

    def is_thumbs_up(self, l):
        fingers = self.fingers_up(l)
        thumb_up = fingers[0]
        others_down = not any(fingers[1:])
        thumb_tip = l[4][:2]
        wrist = l[0][:2]
        thumb_dist = np.linalg.norm(thumb_tip - wrist)
        return thumb_up and others_down and thumb_dist > 0.13

    def is_open_palm(self, l):
        return all(self.fingers_up(l))

    def is_peace(self, l):
        fingers = self.fingers_up(l)
        return fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]

    def is_ok_sign(self, l):
        thumb_tip = l[4][:2]
        index_tip = l[8][:2]
        dist = np.linalg.norm(thumb_tip - index_tip)
        fingers = self.fingers_up(l)
        return dist < 0.06 and not fingers[3] and not fingers[4]

    def palm_direction(self, l):
        base_vec = l[5][:2] - l[17][:2]
        if abs(base_vec[1]) < 0.03:
            return None
        if base_vec[1] > 0.03:
            return "Palm Left"
        elif base_vec[1] < -0.03:
            return "Palm Right"
        return None

    def number_gesture(self, l):
        fingers = self.fingers_up(l)
        count = sum(fingers)
        if count == 3:
            return "Three Fingers"
        elif count == 4:
            return "Four Fingers"
        elif count == 5:
            return "Five Fingers"
        return None

    # --- New Static Gestures ---

    def is_L_gesture(self, l):
        fingers = self.fingers_up(l)
        return (fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4])

    def is_single_point(self, l):
        fingers = self.fingers_up(l)
        return (not fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4])

    def is_c_shape(self, l):
        fingers = self.fingers_up(l)
        thumb_tip = l[4][:2]
        wrist = l[0][:2]
        middle_pip = l[10][:2]
        middle_tip = l[12][:2]
        thumb_far = np.linalg.norm(thumb_tip - wrist) > 0.1
        middle_bent = middle_tip[1] > middle_pip[1]
        not_open_palm = not all(fingers)
        some_fingers_up = sum(fingers) > 0 and sum(fingers) < 5
        return thumb_far and middle_bent and not_open_palm and some_fingers_up

    def is_rock_sign(self, l):
        fingers = self.fingers_up(l)
        return (not fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and fingers[4])

    # --- Dynamic Finger Motion Gestures ---

    def update_finger_motion_buffer(self, l):
        index_tip = l[8][:2]
        middle_tip = l[12][:2]
        avg_x = (index_tip[0] + middle_tip[0]) / 2
        avg_y = (index_tip[1] + middle_tip[1]) / 2
        self.finger_motion_buffer.append((avg_x, avg_y))

    def detect_finger_motion_gesture(self):
        if len(self.finger_motion_buffer) < 5:
            return None
        start_pos = self.finger_motion_buffer[0]
        end_pos = self.finger_motion_buffer[-1]
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        abs_dx, abs_dy = abs(dx), abs(dy)

        HORIZONTAL_THRESHOLD = self.swipe_threshold
        VERTICAL_THRESHOLD = self.scroll_threshold

        now = time.time()
        if now - self.last_finger_motion_time < self.finger_motion_cooldown:
            return None

        if abs_dx > HORIZONTAL_THRESHOLD and abs_dx > abs_dy:
            self.last_finger_motion_time = now
            self.finger_motion_buffer.clear()
            return 'fingers_swipe_right' if dx > 0 else 'fingers_swipe_left'
        elif abs_dy > VERTICAL_THRESHOLD and abs_dy > abs_dx:
            self.last_finger_motion_time = now
            self.finger_motion_buffer.clear()
            return 'fingers_scroll_up' if dy < 0 else 'fingers_scroll_down'
        return None

    # --- Zoom In/Out by pinching/spreading fingers ---

    def _fingertip_dist_sum(self, l):
        thumb, index, middle = l[4][:2], l[8][:2], l[12][:2]
        d1 = np.linalg.norm(thumb - index)
        d2 = np.linalg.norm(thumb - middle)
        d3 = np.linalg.norm(index - middle)
        return (d1 + d2 + d3) / 3

    def detect_zoom(self, l):
        current_dist = self._fingertip_dist_sum(l)
        self.zoom_history.append(current_dist)
        if len(self.zoom_history) < self.zoom_history.maxlen:
            return None
        now = time.time()
        if now - self.last_zoom_action_time < self.zoom_cooldown:
            return None
        delta = self.zoom_history[-1] - self.zoom_history[0]
        threshold = 0.05
        if delta > threshold:
            self.last_zoom_action_time = now
            self.zoom_history.clear()
            return "Zoom In"
        elif delta < -threshold:
            self.last_zoom_action_time = now
            self.zoom_history.clear()
            return "Zoom Out"
        return None

    # --- Main gesture detect method ---

    def detect_gesture(self, l):
        # Priority: Zoom first
        zoom_gesture = self.detect_zoom(l)
        if zoom_gesture:
            return zoom_gesture

        # Static gestures
        if self.is_open_palm(l):
            return "Open Palm"
        if self.is_peace(l):
            return "Peace"
        if self.is_thumbs_up(l):
            return "Thumbs Up"
        if self.is_fist(l):
            return "Fist"
        if self.is_ok_sign(l):
            return "OK Sign"
        palm_dir = self.palm_direction(l)
        if palm_dir:
            return palm_dir
        num_g = self.number_gesture(l)
        if num_g:
            return num_g

        # New static gestures (check order to avoid conflicts)
        if self.is_L_gesture(l):
            return "L Gesture"
        if self.is_single_point(l):
            return "Single Point"
        if self.is_c_shape(l):
            return "C Shape"
        if self.is_rock_sign(l):
            return "Rock Sign"

        # Dynamic finger motion gestures
        self.update_finger_motion_buffer(l)
        fm_gesture = self.detect_finger_motion_gesture()
        if fm_gesture:
            return fm_gesture

        return None

    # Optional: draw finger motion for debugging
    def draw_motion_trace(self, frame, h, w):
        import cv2
        for i, (x, y) in enumerate(self.finger_motion_buffer):
            px, py = int(x * w), int(y * h)
            cv2.circle(frame, (px, py), 7, (128, 255, 80), -1)
        return frame
