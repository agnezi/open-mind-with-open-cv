"""
Detection package for hand detection, face detection, and gesture recognition.
Provides gesture recognition, MediaPipe hand detection, and Haar Cascade face detection.
"""
from .gesture_recognition import count_fingers, recognize_gesture
from .hand_detector import HandDetector
from .face_detector import FaceDetector

__all__ = ['count_fingers', 'recognize_gesture', 'HandDetector', 'FaceDetector']
