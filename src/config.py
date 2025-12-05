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
