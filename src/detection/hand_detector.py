"""
Hand Detector Module.
Wraps MediaPipe Hands for easier use and cleaner interface.
"""
import mediapipe as mp
from .. import config


class HandDetector:
    """
    Wrapper class for MediaPipe Hands detection.
    Provides a clean interface for hand detection and drawing.
    """

    def __init__(self,
                 max_num_hands=None,
                 min_detection_confidence=None,
                 min_tracking_confidence=None):
        """
        Initialize hand detector.

        Args:
            max_num_hands (int): Maximum number of hands to detect
            min_detection_confidence (float): Minimum confidence for detection (0.0-1.0)
            min_tracking_confidence (float): Minimum confidence for tracking (0.0-1.0)
        """
        # Use config values if not provided
        if max_num_hands is None:
            max_num_hands = config.MAX_NUM_HANDS
        if min_detection_confidence is None:
            min_detection_confidence = config.MIN_DETECTION_CONFIDENCE
        if min_tracking_confidence is None:
            min_tracking_confidence = config.MIN_TRACKING_CONFIDENCE

        # Initialize MediaPipe components
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Configure hand detection
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # False = video mode (continuous detection)
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame_rgb):
        """
        Process a frame to detect hands.

        Args:
            frame_rgb (numpy.ndarray): Frame in RGB format

        Returns:
            results: MediaPipe results object with hand landmarks
        """
        return self.hands.process(frame_rgb)

    def draw_landmarks(self, frame, hand_landmarks):
        """
        Draw hand landmarks and connections on frame.

        Args:
            frame (numpy.ndarray): Frame to draw on (BGR format)
            hand_landmarks: MediaPipe hand landmarks to draw
        """
        self.mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS
        )

    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()
