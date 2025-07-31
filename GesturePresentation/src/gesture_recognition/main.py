import sys
import os
import cv2
import time
import json
from gesture_recognition.hand_tracking import HandTracker
from gesture_recognition.gesture_detector import GestureDetector
from presentation_control.control import (
    next_slide, previous_slide, start_slideshow, stop_slideshow,
    zoom_in, zoom_out, pointer_toggle, scroll_up, scroll_down, play_feedback_sound
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# -------- Calibration settings loader -----------
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
# -------------------------------------------------

def main():
    # Load user/calibrated gesture settings
    settings = load_gesture_settings()
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.7,
        model_complexity=1,
        smoothing_window=settings["smoothing_window"]
    )
    detector = GestureDetector()

    command_mode = False
    last_command_time = 0
    mode_cooldown = 0.8
    gesture_active = None
    gesture_start_time = 0
    hold_duration_required = settings["hold_duration_required"]
    last_zoom_time = 0
    zoom_cooldown = 0.6
    window_name = "Gesture-Controlled Presentation"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    feedback_flash = 0  # Frames of screen flash remaining

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame, landmarks_list = tracker.process_frame(frame)
        h, w = annotated_frame.shape[:2]

        # Command Mode banner
        if command_mode:
            cv2.rectangle(annotated_frame, (0, 0), (w, 45), (0, 220, 0), -1)
            cv2.putText(annotated_frame, "COMMAND MODE: ON", (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 25, 25), 2)
        else:
            cv2.rectangle(annotated_frame, (0, 0), (w, 45), (30, 30, 30), -1)
            cv2.putText(annotated_frame,
                        "COMMAND MODE: OFF (Show Open Palm to activate)",
                        (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.78, (200, 200, 200), 2)

        if landmarks_list:
            for idx, landmarks in enumerate(landmarks_list):
                gesture = detector.detect_gesture(landmarks)
                now = time.time()
                # Command Mode toggling
                if gesture == "Open Palm" and not command_mode and now - last_command_time > mode_cooldown:
                    command_mode = True
                    last_command_time = now
                    cv2.putText(annotated_frame, ">>> COMMAND MODE ON <<<", (40, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 255, 0), 3)
                    gesture_active = None
                    gesture_start_time = 0
                    continue
                if command_mode and gesture == "Fist" and now - last_command_time > mode_cooldown:
                    command_mode = False
                    last_command_time = now
                    cv2.putText(annotated_frame, ">>> COMMAND MODE OFF <<<", (40, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.15, (0, 0, 255), 3)
                    gesture_active = None
                    gesture_start_time = 0
                    continue

                if command_mode:
                    wrist_x = int(landmarks[0][0] * w)
                    wrist_y = int(landmarks[0][1] * h)
                    # Instant Zoom In/Out
                    if gesture in ("Zoom In", "Zoom Out") and now - last_zoom_time > zoom_cooldown:
                        cv2.putText(annotated_frame, f"{gesture} triggered!",
                                    (wrist_x - 30, wrist_y + 60 + 40 * idx),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
                        if gesture == "Zoom In":
                            zoom_in()
                        else:
                            zoom_out()
                        last_zoom_time = now
                        cv2.putText(annotated_frame, gesture,
                                    (wrist_x - 30, wrist_y + 30 + 40 * idx),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        play_feedback_sound()   # Play sound here!
                        feedback_flash = 10
                        continue

                    hold_gestures = (
                        "fingers_swipe_left", "fingers_swipe_right",
                        "fingers_scroll_up", "fingers_scroll_down",
                        "OK Sign", "Three Fingers", "Palm Left", "Palm Right",
                        "Peace", "Thumbs Up", "Four Fingers",
                        "L Gesture", "Single Point", "C Shape", "Rock Sign"
                    )
                    if gesture in hold_gestures:
                        if gesture != gesture_active:
                            gesture_active = gesture
                            gesture_start_time = now
                        else:
                            elapsed = now - gesture_start_time
                            progress = min(int((elapsed / hold_duration_required) * 200), 200)
                            cv2.rectangle(annotated_frame, (w - 220, h - 50),
                                          (w - 220 + progress, h - 25), (80, 255, 80), -1)
                            cv2.rectangle(annotated_frame, (w - 220, h - 50),
                                          (w - 20, h - 25), (60, 100, 60), 2)
                            cv2.putText(annotated_frame, "Hold for Action",
                                        (w - 200, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 2)
                            if elapsed >= hold_duration_required:
                                if gesture == "fingers_swipe_right":
                                    next_slide()
                                elif gesture == "fingers_swipe_left":
                                    previous_slide()
                                elif gesture == "OK Sign":
                                    pointer_toggle()
                                elif gesture == "Three Fingers":
                                    start_slideshow()
                                elif gesture == "Palm Left":
                                    previous_slide()
                                elif gesture == "Palm Right":
                                    next_slide()
                                elif gesture == "Peace":
                                    pointer_toggle()
                                elif gesture == "Thumbs Up":
                                    start_slideshow()
                                elif gesture == "Four Fingers":
                                    stop_slideshow()
                                elif gesture == "fingers_scroll_up":
                                    scroll_up(amount=5)
                                elif gesture == "fingers_scroll_down":
                                    scroll_down(amount=5)
                                elif gesture == "L Gesture":
                                    pointer_toggle()
                                elif gesture == "Single Point":
                                    pointer_toggle()
                                elif gesture == "C Shape":
                                    pointer_toggle()
                                elif gesture == "Rock Sign":
                                    next_slide()
                                cv2.putText(annotated_frame, f"{gesture} triggered!",
                                            (wrist_x - 30, wrist_y + 60 + 40 * idx),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
                                play_feedback_sound()   # Make sure to play sound on each action!
                                feedback_flash = 10
                                time.sleep(0.2)
                                gesture_active = None
                                gesture_start_time = 0
                    else:
                        gesture_active = None
                        gesture_start_time = 0

                    # Display detected gesture
                    if gesture:
                        if "Palm" in gesture:
                            color = (0, 120, 255)
                        elif "OK" in gesture:
                            color = (100, 50, 245)
                        elif "fingers" in gesture or "Finger" in gesture:
                            color = (120, 220, 250)
                        elif gesture in ("L Gesture", "Single Point", "C Shape", "Rock Sign"):
                            color = (255, 140, 0)
                        else:
                            color = (0, 255, 0)
                        cv2.putText(annotated_frame, gesture,
                                    (wrist_x - 30, wrist_y + 30 + 40 * idx),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                else:
                    gesture_active = None
                    gesture_start_time = 0

        # Draw border flash for feedback
        if feedback_flash > 0:
            cv2.rectangle(annotated_frame, (0, 0), (w-1, h-1), (0, 255, 0), thickness=18)
            feedback_flash -= 1

        cv2.imshow(window_name, annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
