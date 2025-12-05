"""
Configuration module for hand detection application.
Loads environment variables and provides application settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Camera Configuration
USE_ESP32 = os.getenv('USE_ESP32', 'True').lower() in ('true', '1', 'yes')
ESP32_URL = os.getenv('ESP32_URL', 'YOUR_URL')

# Hand Detection Configuration
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# Display Configuration
WINDOW_NAME = 'Hand Detection'
MIRROR_CAMERA = True  # Flip camera horizontally for mirror effect

# Person Detection Configuration (Full Body)
PERSON_SCALE_FACTOR = 1.1  # Image pyramid scale (lower = more accurate but slower)
PERSON_MIN_NEIGHBORS = 3   # Detection strictness (lower for full body detection)
PERSON_MIN_SIZE = (60, 120) # Minimum person size in pixels (width, height) - taller for body

# Legacy face detection configs (kept for backward compatibility)
FACE_SCALE_FACTOR = PERSON_SCALE_FACTOR
FACE_MIN_NEIGHBORS = PERSON_MIN_NEIGHBORS
FACE_MIN_SIZE = PERSON_MIN_SIZE

# Gesture Control Configuration (HTTP Commands)
CONTROL_URL = os.getenv('CONTROL_URL', 'http://YOUR_URL')
HTTP_TIMEOUT = 2  # Seconds to wait for HTTP response
GESTURE_DEBOUNCE = 0.25  # Seconds between ANY command (250ms debounce)

# Gesture to Command Mapping (sent as JSON in body)
# Only two commands: "follow" (open hand) and "stop" (fist)
GESTURE_COMMANDS = {
    'Open Hand': 'follow',   # Open hand = follow
    'Fist': 'stop',          # Fist = stop
}
