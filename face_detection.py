"""
Webcam Face Detection
A lightweight alternative using OpenCV's built-in Haar Cascade classifier
"""

import cv2
import datetime

class FaceDetection:
    def __init__(self):
        # Load the pre-trained Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    def detect_faces(self, frame):
        """Detect faces in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return faces, gray
    
    def detect_features(self, gray, face_rect):
        """Detect eyes and smile within a face region"""
        x, y, w, h = face_rect
        roi_gray = gray[y:y+h, x:x+w]
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
        
        # Detect smile
        smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
        
        return eyes, smiles
    
    def draw_detections(self, frame, faces, gray):
        """Draw rectangles around detected faces and features"""
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Add label
            cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            # Detect and draw eyes
            eyes, smiles = self.detect_features(gray, (x, y, w, h))
            
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
            
            # Draw smile indicator
            if len(smiles) > 0:
                cv2.putText(frame, 'Smiling :)', (x, y+h+25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return frame
    
    def run(self):
        """Main loop for face detection"""
        print("Opening webcam for face detection...")
        print("Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save screenshot")
        print("  - Press 'r' to toggle recording")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        recording = False
        video_writer = None
        frame_count = 0
        fps = 0
        start_time = datetime.datetime.now()
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Detect faces
            faces, gray = self.detect_faces(frame)
            
            # Draw detections
            frame = self.draw_detections(frame, faces, gray)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = (datetime.datetime.now() - start_time).total_seconds()
                fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Display info
            info_text = f"Faces: {len(faces)} | FPS: {fps:.1f}"
            cv2.putText(frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if recording:
                cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (frame.shape[1] - 70, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Show frame
            cv2.imshow('Face Detection - Press Q to quit', frame)
            
            # Write frame if recording
            if recording and video_writer is not None:
                video_writer.write(frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"face_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved as {filename}")
            elif key == ord('r'):
                if not recording:
                    # Start recording
                    filename = f"face_video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    video_writer = cv2.VideoWriter(filename, fourcc, 20.0, 
                                                   (frame.shape[1], frame.shape[0]))
                    recording = True
                    print(f"Started recording to {filename}")
                else:
                    # Stop recording
                    recording = False
                    if video_writer is not None:
                        video_writer.release()
                        video_writer = None
                    print("Stopped recording")
        
        # Cleanup
        if video_writer is not None:
            video_writer.release()
        cap.release()
        cv2.destroyAllWindows()
        print("\nWebcam closed. Goodbye!")

if __name__ == "__main__":
    detector = FaceDetection()
    detector.run()