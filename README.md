# Webcam Video Recognition Project

Two Python-based video recognition applications using your webcam.

## Prerequisites

- Python 3.7+
- Webcam connected to your computer
- OpenCV installed

## Virtual Environment Setup (Recommended)

Using a virtual environment keeps this project's dependencies isolated from your system Python. This is a best practice in Python development.

### What is a Virtual Environment?

Think of it like `node_modules` in web development - each project has its own isolated dependencies instead of installing everything globally.

### Setup Steps

1. **Create the virtual environment:**
   ```bash
   python3 -m venv venv
   ```
   This creates a `venv/` folder with an isolated Python installation.

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```
   You'll see `(venv)` appear in your terminal prompt.

3. **Install packages (now they install only in this project):**
   ```bash
   pip install opencv-python numpy
   ```
   Note: No `pip3` or `--break-system-packages` needed when in virtual environment!

4. **Save dependencies (optional but recommended):**
   ```bash
   pip freeze > requirements.txt
   ```
   This creates a file listing all dependencies (like `package.json` in Node.js).

### Daily Workflow

**Starting work:**
```bash
source venv/bin/activate  # Activate environment
python face_detection.py  # Run your scripts
```

**When done:**
```bash
deactivate  # Exit virtual environment
```

### If Installing from requirements.txt

If you cloned this project and see a `requirements.txt` file:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Installation

### Option 1: With Virtual Environment (Recommended)

If you followed the Virtual Environment Setup above:

```bash
pip install opencv-python numpy mediapipe
```

**What gets installed:**
- `opencv-python` - Computer vision library
- `numpy` - Math operations (required by OpenCV)
- `mediapipe` - Google's ML solutions (for hand detection)

### Option 2: Global Install (Not Recommended)

Install required packages globally:

```bash
pip3 install opencv-python numpy --break-system-packages
```

**Note:** The `--break-system-packages` flag is needed on macOS to bypass system Python protection.

## Applications

### 1. Face Detection (Recommended to Start)
**File:** `face_detection.py`

A lightweight face detection application that:
- Detects faces in real-time
- Identifies eyes and smiles
- Supports screenshot capture
- Can record video

**Run it:**
```bash
python3 face_detection.py
```

**Controls:**
- `q` - Quit application
- `s` - Save screenshot
- `r` - Toggle video recording

**Pros:**
- No downloads needed (uses built-in models)
- Fast and lightweight
- Great for beginners

---

### 2. Hand Detection & Gesture Recognition
**File:** `hand_detection.py`

Real-time hand tracking and gesture recognition using MediaPipe:
- Detects up to 2 hands simultaneously
- Tracks 21 landmarks per hand (finger joints, tips, palm)
- Recognizes gestures: Thumbs Up, Peace Sign, Pointing, Fist, Open Hand, Rock On
- Labels each finger (Thumb, Index, Middle, Ring, Pinky)
- Shows which hand (Left or Right)

**Run it:**
```bash
python hand_detection.py
```

**Requires:**
```bash
pip install mediapipe
```

**Controls:**
- `q` - Quit application

**Recognized Gestures:**
- 👍 Thumbs Up - Only thumb extended
- ☝️ Pointing - Only index finger up
- ✌️ Peace Sign - Index and middle fingers up
- ✊ Fist - No fingers extended
- ✋ Open Hand - All 5 fingers extended
- 🤘 Rock On - Index and pinky up

**Use Cases:**
- Touchless controls for devices
- Gesture-based game controls
- Sign language recognition foundation
- Control robots/cars with hand gestures

---

### 3. Object Detection (Advanced)
**File:** `webcam_recognition.py`

Advanced object detection using YOLO (You Only Look Once):
- Detects 80 different object types (people, cars, animals, furniture, etc.)
- Shows confidence scores
- Real-time bounding boxes

**Run it:**
```bash
python3 webcam_recognition.py
```

**First run:** Downloads ~33MB model files automatically

**Controls:**
- `q` - Quit application
- `s` - Save current frame

**Pros:**
- Detects many object types
- Industry-standard model
- Extensible for custom training

---

## Customization Ideas

### Modify Detection Parameters

**Face Detection - Adjust sensitivity:**
```python
faces = self.face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,    # Lower = more detections (but more false positives)
    minNeighbors=5,     # Higher = stricter detection
    minSize=(30, 30)    # Minimum face size in pixels
)
```

**Object Detection - Change confidence threshold:**
```python
if confidence > 0.5:  # Change to 0.3 for more detections, 0.7 for fewer
```

### Add New Features

1. **Motion Detection:**
```python
# Compare frames to detect movement
prev_frame = None
if prev_frame is not None:
    diff = cv2.absdiff(frame, prev_frame)
    # Threshold and find contours for motion
```

2. **Person Counting:**
```python
# Count detected people
person_count = sum(1 for class_id in class_ids if self.classes[class_id] == 'person')
```

3. **Alert System:**
```python
# Trigger alert when specific object detected
if 'cell phone' in detected_objects:
    print("⚠️ Phone detected!")
```

## Advanced Usage

### Using Different YOLO Models

Replace `yolov3-tiny` with full YOLOv3 for better accuracy:
```python
cfg_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg"
weights_url = "https://pjreddie.com/media/files/yolov3.weights"
```

### Process Video Files

Modify to process video files instead of webcam:
```python
cap = cv2.VideoCapture('path/to/video.mp4')  # Instead of VideoCapture(0)
```

### Save Detections to File

Log detected objects:
```python
with open('detections.log', 'a') as f:
    f.write(f"{datetime.now()}: {label} detected with {confidence:.2f} confidence\n")
```

## Troubleshooting

**Webcam not opening:**
- Check if another application is using the webcam
- Try different camera indices: `VideoCapture(1)` or `VideoCapture(2)`
- On Linux, ensure you have camera permissions

**Low FPS:**
- Use face_detection.py (lighter weight)
- Process every nth frame: `if frame_count % 3 == 0:`
- Reduce video resolution: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`

**Import errors:**
- Reinstall OpenCV: `pip install --upgrade opencv-python`
- Check Python version: `python3 --version`

## Next Steps

1. **Start simple:** Run `face_detection.py` first
2. **Experiment:** Try different detection parameters
3. **Customize:** Add features for your specific use case
4. **Learn more:** Explore OpenCV documentation

## Resources

- [OpenCV Documentation](https://docs.opencv.org/)
- [YOLO Official Site](https://pjreddie.com/darknet/yolo/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

## License

These scripts are provided as educational examples. Feel free to modify and use them for your projects!