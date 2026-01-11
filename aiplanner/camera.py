import cv2
import threading
import time

class VideoCamera(object):
    def __init__(self):
        # Open the camera (0 is usually the built-in webcam)
        self.video = cv2.VideoCapture(0)
        
        # Load Haar Cascade (ensure the path is correct relative to where app.py runs)
        # We assume app.py runs from the parent directory, so we look in current dir or specific path
        cascade_path = "haarcascade_frontalface_default.xml" 
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.is_slouching = False
        self.last_y = 0
        self.baseline_y = 0
        self.calibration_frames = 0
        
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None, False
            
        # Resize for performance
        image = cv2.resize(image, (640, 480))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        status = "Good"
        color = (0, 255, 0)
        
        if len(faces) > 0:
            # Get the largest face
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            
            # Calibration (first 20 frames)
            if self.calibration_frames < 20:
                self.baseline_y = (self.baseline_y * self.calibration_frames + y) / (self.calibration_frames + 1)
                self.calibration_frames += 1
                status = "Calibrating..."
                color = (255, 255, 0)
            else:
                # Check for slouching (if face moves DOWN, y increases)
                # Threshold: 50 pixels lower than baseline
                if y > self.baseline_y + 50:
                    status = "SLOUCHING!"
                    color = (0, 0, 255)
                    self.is_slouching = True
                else:
                    self.is_slouching = False
                    
            # Draw rectangle
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
            
        else:
            status = "No Face"
            self.is_slouching = False
            
        # Draw Status
        cv2.putText(image, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes(), self.is_slouching
