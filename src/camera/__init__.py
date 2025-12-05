"""
Camera package for handling different camera sources.
Supports both ESP32-CAM and regular webcams.
"""
from .esp32_stream import ESP32CamStream
from .camera_manager import initialize_camera

__all__ = ['ESP32CamStream', 'initialize_camera']
