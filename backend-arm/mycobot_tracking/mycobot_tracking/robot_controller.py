import time
from config import SERIAL_PORT, BAUD_RATE, DEFAULT_SPEED, TRACKING_SPEED, HOME_ANGLES, STEP_CARTESIAN, STEP_ANGLE

try:
    from pymycobot.mycobot import MyCobot
except ImportError:
    MyCobot = None

class RobotController:
    def __init__(self):
        self.is_alive = True
        self.connected = False
        self.mc = None
        self.current_sim_coords = [150.0, 0.0, 200.0, -180.0, 0.0, 0.0] # Simulated base Cartesian coordinates
        self.initialize_connection()

    def initialize_connection(self):
        print(f"[ROBOT] Connecting to robot at {SERIAL_PORT} @ {BAUD_RATE} baud...")
        if MyCobot:
            try:
                self.mc = MyCobot(SERIAL_PORT, BAUD_RATE)
                time.sleep(1)
                self.connected = True
                print("[ROBOT] Physical hardware interface connected.")
            except Exception as e:
                print(f"[ERROR] Failed connecting to real hardware serial interface: {e}")
        else:
            self.connected = False
            print("[ROBOT] Hardware library missing or detached. Running completely in Simulation Mode.")

    def emergency_stop(self):
        self.is_alive = False
        print("\n[!!! EMERGENCY STOP ACTIVATED !!!]")
        if self.connected and self.mc:
            try:
                self.mc.stop()
            except: pass
        
    def release_resources(self):
        print("[ROBOT] Releasing connection resources.")
        if self.mc:
            try: self.mc.stop()
            except: pass

    def go_home(self):
        if not self.is_alive: return
        print(f"[ROBOT] Returning to safe neutral home pose: {HOME_ANGLES}")
        if self.connected and self.mc:
            self.mc.send_angles(HOME_ANGLES, DEFAULT_SPEED)

    def stop_current_movement(self):
        if not self.is_alive: return
        print("[ROBOT] Pausing current trajectory updates.")
        if self.connected and self.mc:
            self.mc.stop()

    def move_cartesian(self, axis, direction):
        if not self.is_alive: return
        axis_map = {'x': 0, 'y': 1, 'z': 2}
        idx = axis_map.get(axis.lower())
        if idx is None: return

        if self.connected and self.mc:
            coords = self.mc.get_coords()
            if coords and len(coords) >= 3:
                coords[idx] += (direction * STEP_CARTESIAN)
                self.mc.send_coords(coords, DEFAULT_SPEED, 1)
        else:
            self.current_sim_coords[idx] += (direction * STEP_CARTESIAN)
            print(f"[SIMULATION] Cartesian move: {axis.upper()} to {self.current_sim_coords[idx]}mm")

    def apply_tracking_updates(self, vel_y, vel_z, idle_offset_z):
        """Applies both automated velocity adjustments from the face tracker and subtle vertical idle bounces."""
        if not self.is_alive: return

        if self.connected and self.mc:
            coords = self.mc.get_coords()
            if coords and len(coords) >= 3:
                # Map tracking adjustments dynamically onto Y and Z cartesian positions
                coords[1] += vel_y  # Left/Right adjustment
                coords[2] += (vel_z + idle_offset_z)  # Up/Down adjustment + Overlay bounce profile
                self.mc.send_coords(coords, TRACKING_SPEED, 1)
        else:
            self.current_sim_coords[1] += vel_y
            self.current_sim_coords[2] += (vel_z + idle_offset_z)
            # Suppress excessive simulation prints by filtering updates slightly
            if abs(vel_y) > 0.1 or abs(vel_z) > 0.1 or abs(idle_offset_z) > 0.1:
                print(f"[SIMULATION TRACKING] Target Y: {self.current_sim_coords[1]:.2f}mm | Target Z: {self.current_sim_coords[2]:.2f}mm (Bounce: {idle_offset_z:.2f}mm)")

    def apply_search_pan(self, simulated_angle):
        """Stage 6: Smoothly updates joint 1 angles to execute structural area searches."""
        if not self.is_alive: return
        if self.connected and self.mc:
            angles = self.mc.get_angles()
            if angles:
                angles[0] = simulated_angle  # Pan base joint 1
                self.mc.send_angles(angles, SEARCH_SPEED)
        else:
            print(f"[SIMULATION SEARCH] Sweeping base Joint 1 angle to: {simulated_angle:.2f}°")

    def move_joint(self, joint_id, direction):
        if not self.is_alive: return
        if self.connected and self.mc:
            angles = self.mc.get_angles()
            if angles and len(angles) >= joint_id:
                angles[joint_id - 1] += (direction * STEP_ANGLE)
                self.mc.send_angles(angles, DEFAULT_SPEED)
        else:
            print(f"[SIMULATION] Rotated Joint {joint_id} by {direction * STEP_ANGLE}°")