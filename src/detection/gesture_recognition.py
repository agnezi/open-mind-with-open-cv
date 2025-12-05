"""
Gesture Recognition Module.
Contains pure logic for finger counting and gesture recognition.
Independent of MediaPipe or OpenCV - just processes landmark data.
"""


def count_fingers(hand_landmarks, handedness):
    """
    Count how many fingers are extended.

    Args:
        hand_landmarks: MediaPipe hand landmarks object with 21 landmarks
        handedness (str): "Right" or "Left" - which hand is detected

    Returns:
        list: List of booleans [thumb, index, middle, ring, pinky]
              True means finger is extended, False means folded

    Landmark IDs reference:
    - Thumb: tip=4, IP=3
    - Index: tip=8, PIP=6
    - Middle: tip=12, PIP=10
    - Ring: tip=16, PIP=14
    - Pinky: tip=20, PIP=18
    """
    fingers = []

    # Check thumb (different logic - horizontal movement)
    # For right hand: thumb tip should be to the right of thumb IP
    # For left hand: thumb tip should be to the left of thumb IP
    if handedness == "Right":
        fingers.append(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x)
    else:  # Left hand
        fingers.append(hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x)

    # Check other 4 fingers (vertical movement)
    # Finger is up if tip is above PIP joint (smaller y value = higher on screen)
    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky tips
    finger_pips = [6, 10, 14, 18]  # Their PIP joints

    for tip, pip in zip(finger_tips, finger_pips):
        fingers.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y)

    return fingers


def recognize_gesture(fingers):
    """
    Recognize gesture based on which fingers are extended.

    Args:
        fingers (list): [thumb, index, middle, ring, pinky]
                       True if finger is up, False if down

    Returns:
        str: Name of the recognized gesture

    Supported gestures:
    - Fist: No fingers up
    - Thumbs Up: Only thumb up
    - Pointing: Only index finger up
    - Peace Sign: Index and middle fingers up
    - Open Hand: All 5 fingers up
    - Rock On: Index and pinky up
    - Default: Shows number of fingers up
    """
    # Count total fingers up
    total_fingers = sum(fingers)

    # Fist - no fingers up
    if total_fingers == 0:
        return "Fist"

    # Thumbs up - only thumb is up
    if fingers == [True, False, False, False, False]:
        return "Thumbs Up"

    # Pointing - only index finger up
    if fingers == [False, True, False, False, False]:
        return "Pointing"

    # Peace sign - index and middle fingers up
    if fingers == [False, True, True, False, False]:
        return "Peace Sign"

    # Open hand - all fingers up
    if total_fingers == 5:
        return "Open Hand"

    # Rock sign - index and pinky up
    if fingers == [False, True, False, False, True]:
        return "Rock On"

    # Default - show number of fingers
    return f"{total_fingers} Fingers"
