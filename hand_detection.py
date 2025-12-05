import cv2
import mediapipe as mp
import time
import requests
import numpy as np
import os
from dotenv import load_dotenv

# ============================================
# CONFIGURATION
# ============================================
# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables with defaults
USE_ESP32 = os.getenv('USE_ESP32', 'True').lower() in ('true', '1', 'yes')
ESP32_URL = os.getenv('ESP32_URL', 'YOUR_URL')

# ============================================
# ESP32-CAM STREAM CLASS
# ============================================
class ESP32CamStream:
    """
    Classe para capturar stream MJPEG do ESP32-CAM
    Funciona melhor que cv2.VideoCapture() para ESP32-CAM
    """
    def __init__(self, url):
        self.url = url
        self.stream = None
        self.bytes_buffer = b''
        self.stream_iterator = None

    def connect(self):
        """Conecta ao stream MJPEG do ESP32-CAM"""
        try:
            print(f"Tentando conectar a {self.url}...")
            self.stream = requests.get(self.url, stream=True, timeout=10)
            # Cria o iterador uma única vez
            self.stream_iterator = self.stream.iter_content(chunk_size=1024)
            print(f"✅ Conectado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    def read(self):
        """
        Lê um frame do stream MJPEG
        Retorna: (success, frame) - mesmo formato do cv2.VideoCapture

        Funciona com o formato do ESP32-CAM:
        Content-Type: image/jpeg
        Content-Length: XXXX

        <dados JPEG>
        --frame
        """
        if self.stream_iterator is None:
            return False, None

        try:
            # Lê chunks até ter um frame completo
            while True:
                # Pega o próximo chunk do iterator
                try:
                    chunk = next(self.stream_iterator)
                except StopIteration:
                    return False, None

                if not chunk:
                    continue

                self.bytes_buffer += chunk

                # Procura pelo boundary do ESP32-CAM
                # O ESP32 usa "\r\n--frame\r\n" como separador
                boundary = b'\r\n--frame\r\n'
                boundary_pos = self.bytes_buffer.find(boundary)

                if boundary_pos != -1:
                    # Pega tudo antes do boundary (é um frame completo)
                    frame_data = self.bytes_buffer[:boundary_pos]

                    # Procura pelo header "Content-Type: image/jpeg"
                    header_end = frame_data.find(b'\r\n\r\n')
                    if header_end != -1:
                        # Pula o header e pega só os dados do JPEG
                        jpg_data = frame_data[header_end + 4:]

                        # Remove o frame processado do buffer
                        self.bytes_buffer = self.bytes_buffer[boundary_pos + len(boundary):]

                        # Decodifica JPEG para imagem OpenCV
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
        """Fecha a conexão com o stream"""
        if self.stream:
            self.stream.close()
            self.stream = None
            print("Conexão fechada")

# ============================================
# HAND DETECTION FUNCTIONS
# ============================================
def count_fingers(hand_landmarks, handedness):
  """
  Count how manyy fingers are extended.
  Returns: list of booleans [thumb, index, middle, ring, pinkyy]
  """
  fingers = []

  # Landmark IDs for each finger tip and middle joint
  # Thumb: tip=4, IP=3
  # Index: tip=8, PIP=6
  # Middle: tip=12, PIP=10
  # Ring: tip=16, PIP=14
  # Pinky: tip=20, PIP=18

  # Check thumb (different logic - horizontal movement)
  # For right hand: thumb tip should be to the right of thumb IP
  # For left hand: thumb tip should be to the left of thumb IP
  if handedness == "Right":
    fingers.append(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x)
  else: # Left hand
    fingers.append(hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x)

  # Check other 4 fingers (vertical movement)
  # Finger is up if tip is above PIP joint (smaller y value = higher on screen)
  finger_tips = [8, 12, 16, 20] # Index, Middle, Ring, Pinky tips
  finger_pips = [6, 10, 14, 18] # Their PIP joints

  for tip, pip in zip(finger_tips, finger_pips):
    fingers.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y)

  return fingers

def recognize_gesture(fingers):
  """
  Recognize gesture based on which fingers are up.
  fingers: [thumb, index, middle, ring, pink] - True if up, False if down
  """

  # Count total fingers up
  total_fingers = sum(fingers)

  # First - no fingers up
  if total_fingers == 0:
    return "Fist"
  
  # Thumbs up - only thumb is up
  if fingers == [True, False, False, False, False]:
    return "Trhumbs Up"
  
  # Pointing - onlyy index finger up
  if fingers == [False, True, False, False, False]:
    return "Pointing"
  
  # Peace sign - index and middle fingers up
  if fingers == [False, True, True, False, False]:
    return "Peace Sign"
  
  # Open hand - all fingers up
  if total_fingers == 5:
    return "Open Hand"
  
  # Rock sign - index and pink yup
  if fingers == [False, True, False, False, True]:
    return "Rock On"
  
  # Default - show number of fingers
  return f"{total_fingers} Fingers"


# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Configure hand detection
hands = mp_hands.Hands(
  static_image_mode=False,      # False = video mode (continuous detection)
  max_num_hands=2,              # Detect up to 2 hands
  min_detection_confidence=0.5, # How confident to be (0.5 = 50%)
  min_tracking_confidence=0.5   # How well to track bertween frames
)


# ============================================
# CAMERA INITIALIZATION
# ============================================
print("=" * 50)
print("HAND DETECTION - Camera Setup")
print("=" * 50)

if USE_ESP32:
    print(f"📷 Modo: ESP32-CAM")
    print(f"🌐 URL: {ESP32_URL}")
    cap = ESP32CamStream(ESP32_URL)

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

print("Hand Detection Started!")
print("Controls:")
print(" - Press 'q' to quit")

while True:
  # Read frame from webcam
  success, frame = cap.read()

  if not success:
    print("Failed to read from webcam")
    break

  # Convert BGR (OpenCV format) to RGB (MediaPipe format)
  frame = cv2.flip(frame, 1) # Flip hohrizontally (mirror effect)
  frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

  # Process frame to detect hands
  results = hands.process(frame_rgb)

  # If hands detected, draw landmarks
  if results.multi_hand_landmarks:
    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):

      # Get handedness (Left or Right)
      handedness = results.multi_handedness[idx].classification[0].label

      # Draw all 21 landmarks and connections
      mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS
      )

      # Count fingers and recognize gesture
      fingers = count_fingers(hand_landmarks, handedness)
      gesture = recognize_gesture(fingers)

      # Display gesture name
      h, w, c = frame.shape
      
      # Position text near the wrist (landmark 0)
      wrist = hand_landmarks.landmark[0]
      wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)

      cv2.putText(frame, f"Gesture: {gesture}", (wrist_x - 80, wrist_y - 60),
                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
      cv2.putText(frame, f"Hand: {handedness} Hand", (wrist_x - 50, wrist_y - 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

      # Label specifcit finger tips
      # Landmark IDs: 4=Thumb, 8=Index, 12=Middle, 16=Ring, 20=Pinky
      finger_tips = {
        4: "Thumb",
        8: "Index",
        12: "Middle",
        16: "Ring",
        20: "Pinky"
      }

      # Draw labels for each finger tip
      for tip_id, finger_name in finger_tips.items():
        landmark = hand_landmarks.landmark[tip_id]

        # Convert normalized coordinates to pixel coordinates
        cx, cy = int(landmark.x * w), int(landmark.y * h)
        
        # Draw finger name
        cv2.putText(frame, finger_name, (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
  # Display the frame
  cv2.imshow('Hand Detection', frame)

  key = cv2.waitKey(1) & 0xFF

  # Quit on 'q' key
  if key == ord('q'):
    break
  elif key == ord('s'):
        filename = f"capture_{time.time()}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved frame as {filename}")
    

# Clean up
cap.release()
cv2.destroyAllWindows()
hands.close()