"""
Camera Manager Module.
Handles camera initialization with automatic fallback from ESP32-CAM to webcam.
"""
import cv2
from .esp32_stream import ESP32CamStream
from .. import config


def initialize_camera():
    """
    Initialize camera based on configuration.
    Tries ESP32-CAM first (if configured), then falls back to webcam.

    Returns:
        camera object: Either ESP32CamStream or cv2.VideoCapture object
        None: If no camera could be initialized

    Raises:
        SystemExit: If no camera source is available
    """
    print("=" * 50)
    print("HAND DETECTION - Camera Setup")
    print("=" * 50)

    if config.USE_ESP32:
        print(f"📷 Modo: ESP32-CAM")
        print(f"🌐 URL: {config.ESP32_URL}")
        cap = ESP32CamStream(config.ESP32_URL)

        if not cap.connect():
            print("\n⚠️  Falha ao conectar ao ESP32-CAM")
            print("🔄 Tentando usar webcam como fallback...")
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("\n❌ Erro: Não conseguiu conectar nem ao ESP32-CAM nem à webcam")
                print("\nVerifique:")
                print("1. ESP32-CAM está ligado?")
                print("2. Conectado ao WiFi?")
                print("3. URL está correta?")
                print("4. Webcam está disponível?")
                exit(1)
            else:
                print("✅ Webcam conectada com sucesso!")
        else:
            print("✅ ESP32-CAM conectado!")
    else:
        print("📷 Modo: Webcam")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("\n❌ Erro: Não conseguiu conectar à webcam")
            print("Verifique se a webcam está disponível")
            exit(1)
        else:
            print("✅ Webcam conectada com sucesso!")

    print("\nHand Detection Started!")
    print("Controls:")
    print(" - Press 'q' to quit")
    print(" - Press 's' to save current frame")
    print()

    return cap
