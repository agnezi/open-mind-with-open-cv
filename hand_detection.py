"""
Hand Detection Application - Main Entry Point

This application detects hands in real-time from a camera feed and recognizes gestures.
Supports both ESP32-CAM and regular webcams.

Controls:
- Press 'q' to quit
- Press 's' to save current frame
"""
import cv2
import time
from src import config
from src.camera import initialize_camera
from src.detection import HandDetector, count_fingers, recognize_gesture


def main():
    """Main application loop."""
    # Initialize camera
    cap = initialize_camera()

    # Initialize hand detector
    detector = HandDetector()

    # Main processing loop
    while True:
        # Read frame from camera
        success, frame = cap.read()

        if not success:
            print("Failed to read from camera")
            break

        # Apply mirror effect if configured
        if config.MIRROR_CAMERA:
            frame = cv2.flip(frame, 1)

        # Convert BGR (OpenCV format) to RGB (MediaPipe format)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame to detect hands
        results = detector.process(frame_rgb)

        # If hands detected, process them
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness (Left or Right)
                handedness = results.multi_handedness[idx].classification[0].label

                # Draw all 21 landmarks and connections
                detector.draw_landmarks(frame, hand_landmarks)

                # Count fingers and recognize gesture
                fingers = count_fingers(hand_landmarks, handedness)
                gesture = recognize_gesture(fingers)

                # Display gesture information
                draw_gesture_info(frame, hand_landmarks, gesture, handedness)

        # Display the frame
        cv2.imshow(config.WINDOW_NAME, frame)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            save_frame(frame)

    # Clean up
    cleanup(cap, detector)


def draw_gesture_info(frame, hand_landmarks, gesture, handedness):
    """
    Draw gesture and hand information on the frame.

    Args:
        frame: OpenCV frame to draw on
        hand_landmarks: MediaPipe hand landmarks
        gesture: Recognized gesture name
        handedness: "Left" or "Right"
    """
    h, w, _ = frame.shape

    # Position text near the wrist (landmark 0)
    wrist = hand_landmarks.landmark[0]
    wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)

    # Draw gesture name
    cv2.putText(frame, f"Gesture: {gesture}", (wrist_x - 80, wrist_y - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Draw handedness
    cv2.putText(frame, f"Hand: {handedness} Hand", (wrist_x - 50, wrist_y - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Label specific finger tips
    # Landmark IDs: 4=Thumb, 8=Index, 12=Middle, 16=Ring, 20=Pinky
    finger_tips = {
        4: "Thumb",
        8: "Index",
        12: "Middle",
        16: "Ring",
        20: "Pinky"
    }

    # Draw labels for each finger tip
    for tip_id, finger_name in finger_tips.items():
        landmark = hand_landmarks.landmark[tip_id]
        # Convert normalized coordinates to pixel coordinates
        cx, cy = int(landmark.x * w), int(landmark.y * h)
        # Draw finger name
        cv2.putText(frame, finger_name, (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def save_frame(frame):
    """
    Save current frame to disk.

    Args:
        frame: OpenCV frame to save
    """
    filename = f"capture_{time.time()}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Saved frame as {filename}")


def cleanup(cap, detector):
    """
    Clean up resources before exit.

    Args:
        cap: Camera capture object
        detector: HandDetector object
    """
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("\nApplication closed successfully")


if __name__ == "__main__":
    main()
