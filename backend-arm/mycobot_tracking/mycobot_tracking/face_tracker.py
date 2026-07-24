import cv2
import time
from config import FRAME_WIDTH, FRAME_HEIGHT, DEADZONE_X, DEADZONE_Y, SEARCH_MAX_PAN
from motion_smoother import PIDController

class FaceTracker:
    """Manages Computer Vision detection structures, target coordinates, and loss recovery loops."""
    def __init__(self):
        # Using built-in Haar Cascade classifier for native lightweight Pi efficiency
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self.pid_x = PIDController(0.12, 0.05)
        self.pid_y = PIDController(0.10, 0.04)
        
        self.tracking_enabled = False
        self.face_lost = True
        self.time_lost = 0.0
        self.search_direction = 1
        self.search_angle = 0.0

    def process_frame(self, frame):
        """Processes images to map bounding spatial center offsets."""
        if frame is None:
            return None, (0, 0), False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(40, 40))
        
        frame_center_x = FRAME_WIDTH // 2
        frame_center_y = FRAME_HEIGHT // 2
        
        # Draw central reference target deadzones visually
        cv2.rectangle(frame, (frame_center_x - DEADZONE_X, frame_center_y - DEADZONE_Y),
                      (frame_center_x + DEADZONE_X, frame_center_y + DEADZONE_Y), (255, 255, 255), 1)

        if len(faces) > 0:
            # Isolate and track only the primary closest/largest detected face structure
            longest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            (x, y, w, h) = longest_face
            
            face_center_x = x + (w // 2)
            face_center_y = y + (h // 2)
            
            # Draw targeting UI elements onto screen display matrices
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (face_center_x, face_center_y), 4, (0, 255, 0), -1)
            
            if self.face_lost:
                print("[TRACKING] Face discovered. Activating lock-on systems.")
                self.face_lost = False
                self.pid_x.reset()
                self.pid_y.reset()

            # Calculate precise geometric pixel target error configurations
            error_x = face_center_x - frame_center_x
            error_y = frame_center_y - face_center_y  # Invert image plane coordinates for Cartesian alignment
            
            # Enforce deadzone dampening
            if abs(error_x) < DEADZONE_X: error_x = 0
            if abs(error_y) < DEADZONE_Y: error_y = 0
            
            return frame, (error_x, error_y), True

        else:
            if not self.face_lost:
                print("[TRACKING] Face lost from sensory matrix frame.")
                self.face_lost = True
                self.time_lost = time.time()
                
            return frame, (0, 0), False

    def get_search_offset(self):
        """Stage 6: Smoothly drives a slow sinusoidal horizontal sweep back and forth to relocate target."""
        # Oscillate search angles across safe regional bounds
        self.search_angle += (self.search_direction * 0.8)
        if abs(self.search_angle) >= SEARCH_MAX_PAN:
            self.search_direction *= -1 # Reverse sweep pathing limits
            
        return self.search_angle