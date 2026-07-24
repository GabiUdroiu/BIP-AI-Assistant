# Centralized configuration settings for the myCobot 320 PI setup

# Connection settings (Raspberry Pi Local Serial)
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

# Safety & Speed metrics
DEFAULT_SPEED = 20              # Safe, low velocity percentage (1-100)
TRACKING_SPEED = 15             # Even smoother, slower speed specifically for auto-tracking
EMERGENCY_SPEED = 0             # Immediate stop velocity

# Gripper safety settings (0 to 100 range)
GRIPPER_OPEN_VALUE = 100        
GRIPPER_MIN_SAFE_LIMIT = 20     
GRIPPER_STEP_SIZE = 5           
GRIPPER_CLOSE_SPEED = 15        

# Manual Movement Settings
STEP_CARTESIAN = 10.0           # mm to move per keypress for X, Y, Z
STEP_ANGLE = 5.0                # degrees to move per keypress for joints

# Safe Neutral Pose (Joint angles in degrees: J1, J2, J3, J4, J5, J6)
HOME_ANGLES = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  

# Stage 3: Idle Mode Settings
IDLE_TIMEOUT = 4.0              # Seconds of inactivity before idle kicks in
IDLE_AMPLITUDE_Z = 8.0          # Vertical bounce amplitude in mm
IDLE_FREQUENCY = 1.5            # Speed of the sinusoidal bounce cycle

# Stage 4: Camera Stream Settings
# Examples: 0 (local webcam), "http://10.89.35.81:8080/video" (DroidCam / IP Webcam)
CAMERA_SOURCE = 0               # Default to local laptop webcam for testing right now

# Stage 5 & 6: Tracking & Search Settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEADZONE_X = 25                 # Pixels of tolerance before moving left/right
DEADZONE_Y = 20                 # Pixels of tolerance before moving up/down

# PID Controller Coefficients
PID_KP_X = 0.12                 # Proportional gain for horizontal adjustments
PID_KD_X = 0.05                 # Derivative gain to counter oscillations
PID_KP_Y = 0.10                 # Proportional gain for vertical adjustments
PID_KD_Y = 0.04                 # Derivative gain

SEARCH_MAX_PAN = 45.0           # Maximum degree sweep left/right during face loss search
SEARCH_SPEED = 8                # Very slow, controlled search sweep speed