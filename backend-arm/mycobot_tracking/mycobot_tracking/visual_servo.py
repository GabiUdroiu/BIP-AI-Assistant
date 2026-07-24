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

            # --- Y-AXIS (Up/Down) TRACKING ---
            if abs(error_y) > DEADZONE_Y:
                raw_step_y = (error_y / float(h // 2)) * 1.5 
                step_y = max(-MAX_STEP, min(MAX_STEP, raw_step_y))
                
                if INVERT_Y:
                    current_angles[3] -= step_y 
                else:
                    current_angles[3] += step_y 
                
                current_angles[3] = max(J4_LIMITS[0], min(J4_LIMITS[1], current_angles[3]))
                move_required = True

            if move_required:
                with robot_lock:
                    mc.send_angles(current_angles, TRACKING_SPEED)
            else:
                cv2.putText(frame, "CENTERED - LOCKED ON", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            time_since_last_face = time.time() - last_face_time
            
            if time_since_last_face > 2.0:
                cv2.putText(frame, "IDLE MODE: ORGANIC BREATHING", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                
                if time.time() - last_idle_update > 0.06:
                    t = time.time()
                    idle_angles = list(current_angles)
                    
                    primary_wave = math.sin(t * 1.4)
                    micro_wave = math.sin(t * 3.8) * 0.8
                    fluid_j3_wave = math.sin(t * 1.4 + 0.7)
                    
                    j2_offset = (primary_wave * 4.5) + micro_wave
                    j3_offset = (fluid_j3_wave * -3.5)
                    j4_offset = (primary_wave * 2.0)  
                    
                    idle_angles[1] += j2_offset
                    idle_angles[2] += j3_offset
                    idle_angles[3] += j4_offset
                    
                    with robot_lock:
                        mc.send_angles(idle_angles, 25)
                        
                    last_idle_update = t
            else:
                cv2.putText(frame, "SEARCHING FOR FACE...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Robot Vision (AI Powered)", frame)

        # --- KEYBOARD CONTROLS ---
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            running = False
            break
        elif key == ord('t'):
            print("\n[COMMAND] Executing 180-Degree Turn!")
            
            if current_angles[0] <= 0:
                current_angles[0] += 180.0
            else:
                current_angles[0] -= 180.0
                
            current_angles[0] = max(J1_LIMITS[0], min(J1_LIMITS[1], current_angles[0]))
            
            with robot_lock:
                mc.send_angles(current_angles, 60)
            
            time.sleep(1.5) 
            last_face_time = time.time()

        time.sleep(0.05) 

    print("\nShutting down safely...")
    cam.stop()
    cv2.destroyAllWindows()
    with robot_lock:
        mc.stop()
        time.sleep(0.1)
        mc.set_color(0, 0, 255) 

if __name__ == "__main__":
    main()