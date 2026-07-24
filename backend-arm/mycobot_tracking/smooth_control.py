import time
import sys
import cv2
import threading
import math
import mediapipe as mp

try:
    from pymycobot.mycobot import MyCobot
except ImportError:
    print("[ERROR] pymycobot library not found. Run: pip install pymycobot")
    sys.exit(1)

# ==========================================
# CONFIGURATION 
# ==========================================
CAMERA_SOURCE = "http://192.168.42.129:8080/video"

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

# Robot Configuration
TRACKING_SPEED = 30  
DEADZONE_X = 40      
DEADZONE_Y = 30      

# --- THE FIX: AXIS INVERSION ---
INVERT_X = True 
INVERT_Y = True  

# SAFETY LIMITS 
MAX_STEP = 1.5           
J1_LIMITS = (-180, 180)  
J4_LIMITS = (-40, 40)    

# --- GRAPPLE LOCK SETTINGS ---
# These set the permanent, standard position for the grapple joints so they never move.
GRAPPLE_PAN = 0.0    # Joint 5
GRAPPLE_ROLL = 70.0  # Joint 6 (Your 70-degree fix)

current_angles = [0.0, 0.0, 0.0, 0.0, GRAPPLE_PAN, GRAPPLE_ROLL]

robot_lock = threading.Lock()
mc = None
running = True

class CameraStream:
    def __init__(self, src):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
        self.frame = None
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = cv2.flip(frame, 1) 
            time.sleep(0.01)

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()

def main():
    global mc, running, current_angles

    print("Connecting to myCobot 320 PI...")
    try:
        mc = MyCobot(SERIAL_PORT, BAUD_RATE)
        time.sleep(1)
        mc.set_color(0, 255, 0) 
        print("Robot Connected! Lights are GREEN.")
    except Exception as e:
        print(f"Failed to connect to robot: {e}")
        return

    print("Moving to starting position...")
    with robot_lock:
        mc.send_angles(current_angles, 40)
    time.sleep(2)

    print("Connecting to Camera...")
    cam = CameraStream(CAMERA_SOURCE)
    time.sleep(2) 

    if cam.read() is None:
        print("[ERROR] Could not connect to the camera!")
        mc.set_color(255, 0, 0) 
        cam.stop()
        return

    print("\n========================================")
    print("      AI FACE TRACKING ACTIVATED        ")
    print("========================================")
    print(" Ensure your face is in the camera view.")
    print(" Click the video window and press 'Q' to quit. Press 'T' to turn 180 degrees.")
    print("========================================\n")

    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

    last_face_time = time.time()
    last_idle_update = 0

    while running:
        frame = cam.read()
        if frame is None:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        h, w, _ = frame.shape
        frame_center_x = w // 2 
        frame_center_y = h // 2 

        cv2.rectangle(frame, (frame_center_x - DEADZONE_X, frame_center_y - DEADZONE_Y),
                             (frame_center_x + DEADZONE_X, frame_center_y + DEADZONE_Y), (255, 255, 255), 1)

        # Forcefully lock the grapple angles every frame so they cannot drift
        current_angles[4] = GRAPPLE_PAN
        current_angles[5] = GRAPPLE_ROLL

        if results.detections:
            last_face_time = time.time()
            
            detection = results.detections[0]
            bboxC = detection.location_data.relative_bounding_box
            
            xmin = int(bboxC.xmin * w)
            ymin = int(bboxC.ymin * h)
            width = int(bboxC.width * w)
            height = int(bboxC.height * h)

            face_center_x = xmin + (width // 2)
            face_center_y = ymin + (height // 2)

            cv2.rectangle(frame, (xmin, ymin), (xmin + width, ymin + height), (0, 255, 0), 2)
            cv2.circle(frame, (face_center_x, face_center_y), 4, (0, 255, 0), -1)

            error_x = face_center_x - frame_center_x
            error_y = face_center_y - frame_center_y

            move_required = False

            # --- X-AXIS (Left/Right) TRACKING ---
            if abs(error_x) > DEADZONE_X:
                raw_step_x = (error_x / float(w // 2)) * 1.5 
                step_x = max(-MAX_STEP, min(MAX_STEP, raw_step_x))
                
                if INVERT_X:
                    current_angles[0] += step_x 
                else:
                    current_angles[0] -= step_x 
                
                current_angles[0] = max(J1_LIMITS[0], min(J1_LIMITS[1], current_angles[0]))
                move_required = True

            # --- Y-A