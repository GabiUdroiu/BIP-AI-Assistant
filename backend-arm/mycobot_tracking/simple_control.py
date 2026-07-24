import time
import sys
import termios
import tty

try:
    from pymycobot.mycobot import MyCobot
except ImportError:
    print("[ERROR] pymycobot library not found. Run: pip install pymycobot")
    sys.exit(1)

# Configuration
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200
SPEED = 20           
STEP = 5.0           
UP_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# "Shadow State" to track perfect math angles without encoder noise
current_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

def get_keypress():
    """Reads a single keypress instantly without requiring the Enter key."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch.upper()

def sync_initial_angles(mc):
    """Reads the robot's actual position once at startup to sync our tracker."""
    global current_angles
    print("Syncing initial physical angles...")
    for _ in range(5):
        angles = mc.get_angles()
        if angles and len(angles) == 6:
            current_angles = angles
            print(f"Synced! Starting angles: {current_angles}")
            return
        time.sleep(0.1)
    print("[WARNING] Could not read initial angles. Assuming 0 degrees.")

def main():
    global current_angles
    
    print("Connecting to myCobot 320 PI...")
    try:
        mc = MyCobot(SERIAL_PORT, BAUD_RATE)
        time.sleep(1)
        print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Sync the shadow state with reality before we start
    sync_initial_angles(mc)

    print("\n========================================")
    print("      ISOLATED JOINT CONTROL TESTER     ")
    print("========================================")
    print("  [U] - Move ALL THE WAY UP (0,0,0,0,0,0)")
    print("\n  Joint Controls (- / +):")
    print("  [1/2] - Joint 1 (Base)")
    print("  [3/4] - Joint 2")
    print("  [5/6] - Joint 3")
    print("  [7/8] - Joint 4")
    print("  [9/0] - Joint 5")
    print("  [-/=] - Joint 6 (Wrist)")
    print("\n  [SPACE] - Stop Movement")
    print("  [Q] - Quit Program")
    print("========================================\n")

    while True:
        key = get_keypress()

        if key == 'Q':
            print("\nExiting program...")
            mc.stop()
            break
            
        elif key == 'U':
            print("\nMoving to STRAIGHT UP position...")
            current_angles = list(UP_POSE) # Reset our shadow tracker
            mc.send_angles(current_angles, SPEED)
            
        elif key == ' ':
            print("\nStopping current movement.")
            mc.stop()
            # Re-sync because stopping mid-movement breaks our math tracking
            sync_initial_angles(mc)

        # Joint 1
        elif key == '1': move_single_joint(mc, 1, -1)
        elif key == '2': move_single_joint(mc, 1, 1)
        # Joint 2
        elif key == '3': move_single_joint(mc, 2, -1)
        elif key == '4': move_single_joint(mc, 2, 1)
        # Joint 3
        elif key == '5': move_single_joint(mc, 3, -1)
        elif key == '6': move_single_joint(mc, 3, 1)
        # Joint 4
        elif key == '7': move_single_joint(mc, 4, -1)
        elif key == '8': move_single_joint(mc, 4, 1)
        # Joint 5
        elif key == '9': move_single_joint(mc, 5, -1)
        elif key == '0': move_single_joint(mc, 5, 1)
        # Joint 6
        elif key == '-': move_single_joint(mc, 6, -1)
        elif key == '=': move_single_joint(mc, 6, 1)

def move_single_joint(mc, joint_id, direction):
    """Updates the internal tracker and sends a command ONLY to one specific motor."""
    global current_angles
    
    # Calculate the new angle purely in software
    current_angles[joint_id - 1] += (direction * STEP)
    target_angle = current_angles[joint_id - 1]
    
    print(f"Commanding ONLY Joint {joint_id} to {target_angle:.1f} degrees")
    
    # Send the targeted command directly to that one motor ID
    mc.send_angle(joint_id, target_angle, SPEED)

if __name__ == "__main__":
    main()