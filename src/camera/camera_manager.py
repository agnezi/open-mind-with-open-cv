"""
Camera Manager Module.
Handles webcam initialization.
"""
import cv2


def initialize_camera():
    """
    Initialize webcam for video capture.

    Returns:
        cv2.VideoCapture: Webcam capture object

    Raises:
        SystemExit: If webcam cannot be initialized
    """
    print("=" * 50)
    print("Camera Initialization")
    print("=" * 50)
    print("Mode: Webcam")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("\nError: Could not open webcam")
        print("Please check:")
        print("  1. Webcam is connected")
        print("  2. No other application is using the webcam")
        print("  3. Camera permissions are granted")
        exit(1)

    print("Webcam connected successfully!")
    print("=" * 50)
    print()

    return cap
