"""
Gesture Control Module

Sends HTTP POST commands with JSON body to a target device based on recognized hand gestures.
Maps gestures to command strings sent in JSON format.
"""
import requests
import time
from typing import Optional
from src import config


class GestureController:
    """
    Controls external devices via HTTP POST based on hand gestures.

    This class maps hand gestures to commands and sends them as JSON
    with debounce to prevent rapid repeated commands.
    """

    def __init__(self, url: Optional[str] = None):
        """
        Initialize the gesture controller.

        Args:
            url: Full URL of the target device (e.g., "http://YOUR_URL")
                 If None, uses config.CONTROL_URL
        """
        self.url = url or config.CONTROL_URL
        self.last_command_time = 0.0  # Global debounce timer
        self.debounce = config.GESTURE_DEBOUNCE  # Seconds between ANY commands

        print(f"GestureController initialized")
        print(f"  URL: {self.url}")
        print(f"  Debounce: {self.debounce * 1000}ms")

    def send_gesture_command(self, gesture: str) -> bool:
        """
        Send HTTP POST command with JSON body for a recognized gesture.

        Args:
            gesture: Name of the recognized gesture

        Returns:
            True if command was sent successfully, False otherwise
        """
        # Check if gesture is mapped to a command
        if gesture not in config.GESTURE_COMMANDS:
            return False

        # Check global debounce to prevent rapid commands
        current_time = time.time()
        time_since_last = current_time - self.last_command_time
        if time_since_last < self.debounce:
            return False  # Still in debounce period

        # Get command string for this gesture
        command = config.GESTURE_COMMANDS[gesture]

        # Create simple JSON payload (only command field)
        payload = {
            'command': command
        }

        try:
            # Send HTTP POST request with JSON body
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=config.HTTP_TIMEOUT
            )

            if response.status_code == 200:
                self.last_command_time = current_time
                print(f"✓ Sent: {command} (gesture: {gesture})")
                return True
            else:
                print(f"✗ Failed. Status: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print(f"✗ Request timeout")
            return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def send_custom_command(self, command: str) -> bool:
        """
        Send a custom HTTP POST command with JSON body.

        Args:
            command: The command string to send

        Returns:
            True if command was sent successfully, False otherwise
        """
        payload = {
            'command': command
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=config.HTTP_TIMEOUT
            )

            if response.status_code == 200:
                print(f"✓ Sent custom command: {command}")
                return True
            else:
                print(f"✗ Failed. Status: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test if the target device is reachable by sending a test POST.

        Returns:
            True if device responds, False otherwise
        """
        try:
            payload = {'command': 'test'}
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=2
            )
            print(f"✓ Connection successful to {self.url}")
            return True
        except Exception as e:
            print(f"✗ Connection failed to {self.url}: {e}")
            return False
