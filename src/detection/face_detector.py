"""
Person Detection Module

Provides a simple person detection wrapper using OpenCV's Haar Cascade classifier.
Detects full human bodies in video frames with minimal visual output.
"""
import cv2
from src import config


class FaceDetector:
    """
    Person detector using Haar Cascade classifier for full body detection.

    This class provides a simple interface for detecting human bodies in video frames.
    It uses OpenCV's pre-trained Haar Cascade model for full body detection.

    Note: Class name kept as FaceDetector for backward compatibility.
    """

    def __init__(self):
        """
        Initialize the person detector by loading the Haar Cascade classifier.
        """
        # Load the pre-trained Haar Cascade for full body detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise RuntimeError(f"Failed to load Haar Cascade from {cascade_path}")

    def process(self, frame):
        """
        Detect people (full bodies) in the given frame.

        Args:
            frame: BGR image frame from OpenCV (numpy array)

        Returns:
            List of tuples (x, y, w, h) representing detected person rectangles
        """
        # Convert to grayscale for Haar Cascade processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect people using configured parameters
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=config.PERSON_SCALE_FACTOR,
            minNeighbors=config.PERSON_MIN_NEIGHBORS,
            minSize=config.PERSON_MIN_SIZE
        )

        return faces

    def draw_detections(self, frame, faces):
        """
        Draw simple rectangles around detected people.

        Args:
            frame: BGR image frame to draw on (numpy array)
            faces: List of tuples (x, y, w, h) from process()

        Returns:
            Frame with person rectangles drawn (modifies in-place and returns)
        """
        for (x, y, w, h) in faces:
            # Draw blue rectangle around each detected person
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return frame

    def close(self):
        """
        Clean up resources.

        Note: Haar Cascade doesn't require explicit cleanup, but this method
        is provided for interface consistency with HandDetector.
        """
        pass
