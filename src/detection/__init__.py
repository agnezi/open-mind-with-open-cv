"""
Detection package for hand detection and gesture recognition.
Provides gesture recognition and MediaPipe hand detection wrapper.
"""
from .gesture_recognition import count_fingers, recognize_gesture
from .hand_detector import HandDetector

__all__ = ['count_fingers', 'recognize_gesture', 'HandDetector']
