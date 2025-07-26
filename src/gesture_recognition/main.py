# main.py

import cv2
from hand_tracker import HandTracker
from gesture_detector import GestureDetector


def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(
        max_num_hands=2,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.7,
        model_complexity=1,
        smoothing_window=5
    )
    detector = GestureDetector()

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Get annotated frame & list of smoothed landmarks (each is np.ndarray shape (21,3))
        annotated_frame, smoothed_landmarks_list = tracker.process_frame(frame)

        if smoothed_landmarks_list:
            for landmarks_np in smoothed_landmarks_list:
                # Detect gesture for each hand
                gesture = detector.detect_gesture(landmarks_np)

                if gesture:
                    # Calculate wrist position in pixel coords for placing text
                    h, w, _ = annotated_frame.shape
                    wrist_x = int(landmarks_np[0][0] * w)
                    wrist_y = int(landmarks_np[0][1] * h)

                    # Draw the gesture label on frame
                    cv2.putText(
                        annotated_frame,
                        gesture,
                        (wrist_x - 30, wrist_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA,
                    )

        # Show the video feed with annotations
        cv2.imshow("Gesture-Controlled Presentation System", annotated_frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
