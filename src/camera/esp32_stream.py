"""
ESP32-CAM Stream Handler Module.
Provides a class to capture MJPEG stream from ESP32-CAM.
Works better than cv2.VideoCapture() for ESP32-CAM.
"""
import cv2
import requests
import numpy as np


class ESP32CamStream:
    """
    Class to capture MJPEG stream from ESP32-CAM.
    Provides a similar interface to cv2.VideoCapture for compatibility.
    """

    def __init__(self, url):
        """
        Initialize ESP32-CAM stream.

        Args:
            url (str): ESP32-CAM stream URL
        """
        self.url = url
        self.stream = None
        self.bytes_buffer = b''
        self.stream_iterator = None

    def connect(self):
        """
        Connect to ESP32-CAM MJPEG stream.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"Tentando conectar a {self.url}...")
            self.stream = requests.get(self.url, stream=True, timeout=10)
            # Create the iterator once
            self.stream_iterator = self.stream.iter_content(chunk_size=1024)
            print(f"✅ Conectado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    def read(self):
        """
        Read a frame from the MJPEG stream.

        Returns:
            tuple: (success, frame) - same format as cv2.VideoCapture

        Works with ESP32-CAM format:
        Content-Type: image/jpeg
        Content-Length: XXXX

        <JPEG data>
        --frame
        """
        if self.stream_iterator is None:
            return False, None

        try:
            # Read chunks until we have a complete frame
            while True:
                # Get next chunk from iterator
                try:
                    chunk = next(self.stream_iterator)
                except StopIteration:
                    return False, None

                if not chunk:
                    continue

                self.bytes_buffer += chunk

                # Look for ESP32-CAM boundary
                # ESP32 uses "\r\n--frame\r\n" as separator
                boundary = b'\r\n--frame\r\n'
                boundary_pos = self.bytes_buffer.find(boundary)

                if boundary_pos != -1:
                    # Get everything before boundary (complete frame)
                    frame_data = self.bytes_buffer[:boundary_pos]

                    # Look for header "Content-Type: image/jpeg"
                    header_end = frame_data.find(b'\r\n\r\n')
                    if header_end != -1:
                        # Skip header and get only JPEG data
                        jpg_data = frame_data[header_end + 4:]

                        # Remove processed frame from buffer
                        self.bytes_buffer = self.bytes_buffer[boundary_pos + len(boundary):]

                        # Decode JPEG to OpenCV image
                        if len(jpg_data) > 0:
                            frame = cv2.imdecode(
                                np.frombuffer(jpg_data, dtype=np.uint8),
                                cv2.IMREAD_COLOR
                            )

                            if frame is not None:
                                return True, frame

        except Exception as e:
            print(f"❌ Erro ao ler frame: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def release(self):
        """Close the connection to the stream."""
        if self.stream:
            self.stream.close()
            self.stream = None
            print("Conexão fechada")

    def isOpened(self):
        """
        Check if stream is opened (for compatibility with cv2.VideoCapture).

        Returns:
            bool: True if stream is connected, False otherwise
        """
        return self.stream is not None and self.stream_iterator is not None
