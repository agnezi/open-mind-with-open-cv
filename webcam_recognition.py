"""
Webcam Video Recognition with Object Detection
Uses YOLOv3 for real-time object detection through your webcam
"""

import cv2
import numpy as np
import urllib.request
import os

class WebcamRecognition:
    def __init__(self):
        self.net = None
        self.classes = []
        self.output_layers = []
        self.colors = []
        
    def download_yolo_files(self):
        """Download YOLO configuration, weights, and class names"""
        print("Downloading YOLO files (this may take a few minutes)...")
        
        # URLs for YOLOv3-tiny (smaller, faster model)
        cfg_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg"
        weights_url = "https://pjreddie.com/media/files/yolov3-tiny.weights"
        names_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
        
        # Download files
        if not os.path.exists("yolov3-tiny.cfg"):
            print("Downloading config file...")
            urllib.request.urlretrieve(cfg_url, "yolov3-tiny.cfg")
        
        if not os.path.exists("yolov3-tiny.weights"):
            print("Downloading weights file (this is ~33MB)...")
            urllib.request.urlretrieve(weights_url, "yolov3-tiny.weights")
        
        if not os.path.exists("coco.names"):
            print("Downloading class names...")
            urllib.request.urlretrieve(names_url, "coco.names")
        
        print("Files downloaded successfully!")
    
    def load_model(self):
        """Load the YOLO model"""
        print("Loading YOLO model...")
        
        # Load class names
        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Generate random colors for each class
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        
        # Load YOLO
        self.net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        print("Model loaded successfully!")
    
    def detect_objects(self, frame):
        """Detect objects in a frame"""
        height, width, channels = frame.shape
        
        # Prepare image for detection
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        
        # Run detection
        outs = self.net.forward(self.output_layers)
        
        # Process detections
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # Confidence threshold
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression to remove overlapping boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        return boxes, confidences, class_ids, indexes
    
    def draw_labels(self, frame, boxes, confidences, class_ids, indexes):
        """Draw bounding boxes and labels on frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                color = self.colors[class_ids[i]]
                
                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label background
                label_text = f"{label} {confidence:.2f}"
                (text_width, text_height), _ = cv2.getTextSize(label_text, font, 0.5, 2)
                cv2.rectangle(frame, (x, y - 20), (x + text_width, y), color, -1)
                
                # Draw label text
                cv2.putText(frame, label_text, (x, y - 5), font, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def run(self):
        """Main loop for webcam recognition"""
        # Download and load model
        self.download_yolo_files()
        self.load_model()
        
        # Open webcam
        print("\nOpening webcam...")
        print("Press 'q' to quit")
        print("Press 's' to save current frame")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Process every 3rd frame for better performance
            if frame_count % 3 == 0:
                boxes, confidences, class_ids, indexes = self.detect_objects(frame)
                frame = self.draw_labels(frame, boxes, confidences, class_ids, indexes)
            
            # Display FPS
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show frame
            cv2.imshow('Webcam Object Recognition - Press Q to quit', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"capture_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved frame as {filename}")
            
            frame_count += 1
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("\nWebcam closed. Goodbye!")

if __name__ == "__main__":
    recognizer = WebcamRecognition()
    recognizer.run()