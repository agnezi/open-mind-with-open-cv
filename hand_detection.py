import cv2
import mediapipe as mp
import time

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

# Open webcam
cap = cv2.VideoCapture(0)

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