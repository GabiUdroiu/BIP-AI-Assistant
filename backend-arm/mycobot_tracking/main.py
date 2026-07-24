import time
import sys
import cv2
from robot_controller import RobotController
from gripper_controller import GripperController
from keyboard_controller import KeyboardController
from idle_controller import IdleController
from camera_stream import CameraStream
from face_tracker import FaceTracker

class MainApplication:
    def __init__(self):
        print("=====================================================")
        print("myCobot 320 PI Integrated System Core - STAGES 1 TO 6")
        print("=====================================================")
        
        # Load independent system components
        self.rc = RobotController()
        self.gripper = GripperController(self.rc)
        self.idle = IdleController()
        self.camera = CameraStream()
        self.tracker = FaceTracker()
        self.keyboard = KeyboardController(self)
        
        self.display_menu()

    def display_menu(self):
        print("\n--- SYSTEM CONTROL DASHBOARD ---")
        print("  [H]  - GO TO STANDARD POSITION (Safe Home Pose)")
        print("  [T]  - TOGGLE AUTOMATED FACE TRACKING (ON/OFF)")
        print("  [I]  - Toggle Idle Bouncing manually")
        print("  [O/C] - Open / Close Gripper")
        print("\n--- JOINT CONTROLS (Counter-Clockwise / Clockwise) ---")
        print(" [1 / 2] - Joint 1 (Base)")
        print(" [3 / 4] - Joint 2")
        print(" [5 / 6] - Joint 3")
        print(" [7 / 8] - Joint 4")
        print(" [9 / 0] - Joint 5")
        print(" [- / =] - Joint 6 (Wrist)")
        print("\n--- SYSTEM SAFEGUARDS ---")
        print(" [SPACE]- Safe Stop Current Movement")
        print("  [K]  - HARD EMERGENCY KILL SWITCH")
        print("  [Q]  - Quit Program safely")
        print("-----------------------------------------\n")

    def run(self):
        # Start input and video streams
        self.keyboard.start()
        self.camera.start()
        
        print("[MAIN] Execution lifecycle active. Launching CV interface display...")
        
        try:
            while self.rc.is_alive and self.keyboard.running:
                frame = self.camera.read_frame()
                
                vel_y = 0.0
                vel_z = 0.0
                idle_offset_z = 0.0
                
                if frame is not None:
                    # Analyze visual fields for tracking profiles
                    processed_frame, error_vector, target_acquired = self.tracker.process_frame(frame)
                    err_x, err_y = error_vector
                    
                    if self.tracker.tracking_enabled:
                        self.idle.record_activity() # Tracking execution maintains active usage parameters
                        
                        if target_acquired:
                            # Use PID metrics to calculate corrections
                            vel_y = self.tracker.pid_x.compute(err_x)
                            vel_z = self.tracker.pid_y.compute(err_y)
                        else:
                            # Face is missing. Drop velocities, run slow automated search sweeps
                            simulated_search_angle = self.tracker.get_search_offset()
                            self.rc.apply_search_pan(simulated_search_angle)
                    
                    # Process idle bounce criteria if tracking isn't proactively handling a target
                    if not (self.tracker.tracking_enabled and target_acquired):
                        idle_offset_z = self.idle.update()
                    else:
                        # Smooth integration overlay: tiny bounce on top of tracking target if active
                        idle_offset_z = self.idle.update() * 0.3 # Scale down bounce intensity to prevent drops
                    
                    # Apply combined delta translations to robot kinematics
                    if vel_y != 0.0 or vel_z != 0.0 or idle_offset_z != 0.0:
                        self.rc.apply_tracking_updates(vel_y, vel_z, idle_offset_z)

                    # Display real-time UI feed
                    cv2.imshow("myCobot Vision Target Matrix", processed_frame)
                    
                # Clean up display matrix frames
                if cv2.waitKey(1) & 0xFF == ord('Q'):
                    break
                    
                time.sleep(0.03) # Lock calculations to roughly ~30 FPS profile ranges
                
        except KeyboardInterrupt:
            print("\n[MAIN] Manual Interruption intercepted. Triggering full shutdown.")
            self.rc.emergency_stop()
        finally:
            self.shutdown()

    def shutdown(self):
        self.keyboard.stop()
        self.camera.stop()
        self.rc.release_resources()
        cv2.destroyAllWindows()
        print("[MAIN] Fully cleaned up process loops. Script terminated.")
        sys.exit(0)

if __name__ == "__main__":
    app = MainApplication()
    app.run()