"""
Gesture Control Module

Sends HTTP POST commands with JSON body to a target device based on recognized hand gestures.
Maps gestures to command strings sent in JSON format.
Uses threading for non-blocking requests.
"""
import requests
import time
import threading
from typing import Optional
from src import config


class GestureController:
    """
    Controls external devices via HTTP POST based on hand gestures.

    This class maps hand gestures to commands and sends them as JSON
    with debounce to prevent rapid repeated commands.
    """

    def __init__(self, url: Optional[str] = None, async_mode: bool = True):
        """
        Initialize the gesture controller.

        Args:
            url: Full URL of the target device (e.g., "http://YOUR_URL")
                 If None, uses config.CONTROL_URL
            async_mode: If True, sends requests in background thread (non-blocking)
        """
        self.url = url or config.CONTROL_URL
        self.last_command_time = 0.0  # Global debounce timer
        self.debounce = config.GESTURE_DEBOUNCE  # Seconds between ANY commands
        self.async_mode = async_mode

        print(f"GestureController initialized")
        print(f"  URL: {self.url}")
        print(f"  Debounce: {self.debounce * 1000}ms")
        print(f"  Mode: {'Async (non-blocking)' if async_mode else 'Sync (blocking)'}")

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

        # Update debounce timer immediately
        self.last_command_time = current_time

        if self.async_mode:
            # Send request in background thread (non-blocking)
            thread = threading.Thread(
                target=self._send_request_async,
                args=(payload, command),
                daemon=True
            )
            thread.start()
            return True
        else:
            # Send request synchronously (blocking)
            return self._send_request_sync(payload, command)

    def _send_request_sync(self, payload: dict, command: str) -> bool:
        """Send HTTP request synchronously (blocks until response)."""
        try:
            start_time = time.time()
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=config.HTTP_TIMEOUT
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                print(f"✓ Sent: {command} ({elapsed_ms:.0f}ms)")
                return True
            else:
                print(f"✗ Failed. Status: {response.status_code} ({elapsed_ms:.0f}ms)")
                return False

        except requests.exceptions.Timeout:
            print(f"✗ Request timeout (>{config.HTTP_TIMEOUT}s)")
            return False
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def _send_request_async(self, payload: dict, command: str):
        """Send HTTP request asynchronously in background thread."""
        try:
            start_time = time.time()
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=config.HTTP_TIMEOUT
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                print(f"✓ Sent: {command} ({elapsed_ms:.0f}ms)")
            else:
                print(f"✗ Failed. Status: {response.status_code} ({elapsed_ms:.0f}ms)")

        except requests.exceptions.Timeout:
            print(f"✗ Timeout: {command} (>{config.HTTP_TIMEOUT}s)")
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection error: {command}")
        except Exception as e:
            print(f"✗ Error: {command} - {e}")

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
