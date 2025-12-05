"""
Person Detection Application

A lightweight person detection application using OpenCV's Haar Cascade classifier.
Detects full human bodies in real-time from webcam feed.

Controls:
- Press 'q' to quit
- Press 's' to save screenshot
- Press 'r' to toggle video recording
"""
import cv2
import datetime
from src.detection import FaceDetector


def main():
    """Main loop for person detection."""
    print("Opening webcam for person detection (full body)...")
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save screenshot")
    print("  - Press 'r' to toggle recording")
    print()

    # Initialize person detector (detects full body)
    detector = FaceDetector()

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Recording state
    recording = False
    video_writer = None
    frame_count = 0
    fps = 0
    start_time = datetime.datetime.now()

    print("Person detection started!\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame")
            break

        # Detect people (full body)
        people = detector.process(frame)

        # Draw detections (simple blue rectangles)
        detector.draw_detections(frame, people)

        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()
            fps = frame_count / elapsed if elapsed > 0 else 0

        # Display info
        info_text = f"People: {len(people)} | FPS: {fps:.1f}"
        cv2.putText(frame, info_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show recording indicator
        if recording:
            cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (frame.shape[1] - 70, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Show frame
        cv2.imshow('Person Detection - Press Q to quit', frame)

        # Write frame if recording
        if recording and video_writer is not None:
            video_writer.write(frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"person_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved as {filename}")
        elif key == ord('r'):
            if not recording:
                # Start recording
                filename = f"person_video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                video_writer = cv2.VideoWriter(filename, fourcc, 20.0,
                                               (frame.shape[1], frame.shape[0]))
                recording = True
                print(f"Started recording to {filename}")
            else:
                # Stop recording
                recording = False
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                print("Stopped recording")

    # Cleanup
    if video_writer is not None:
        video_writer.release()
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("\nWebcam closed. Goodbye!")


if __name__ == "__main__":
    main()
