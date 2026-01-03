"""
Configuration module for hand detection application.
Loads environment variables and provides application settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Hand Detection Configuration
MAX_NUM_HANDS = int(os.getenv('MAX_NUM_HANDS', '2'))
MIN_DETECTION_CONFIDENCE = float(os.getenv('MIN_DETECTION_CONFIDENCE', '0.8'))  # Increased from 0.5 to 0.8 to prevent face detection
MIN_TRACKING_CONFIDENCE = float(os.getenv('MIN_TRACKING_CONFIDENCE', '0.5'))

# Display Configuration
WINDOW_NAME = 'Hand Detection'
MIRROR_CAMERA = True  # Flip camera horizontally for mirror effect

# Gesture Control Configuration (HTTP Commands)
CONTROL_URL = os.getenv('CONTROL_URL', 'http://YOUR_URL')
HTTP_TIMEOUT = 2  # Seconds to wait for HTTP response
GESTURE_DEBOUNCE = 0.25  # Seconds between ANY command (250ms debounce)

# Gesture to Command Mapping (sent as JSON in body)
# Only two commands: "follow" (open hand) and "stop" (fist)
GESTURE_COMMANDS = {
    'Open Hand': 'follow',   # Open hand = follow
    'Fist': 'stop',          # Fist = stop
    'Pointing': 'turn-right',
    'Peace Sign': 'turn-left',
    'Thumbs Up': 'backward'
}

# Telemetry Configuration
TELEMETRY_ENABLED = os.getenv('TELEMETRY_ENABLED', 'True').lower() in ('true', '1', 'yes')
TELEMETRY_SMOOTHING = float(os.getenv('TELEMETRY_SMOOTHING', '0.1'))  # FPS smoothing factor (0.0-1.0, lower = smoother)
