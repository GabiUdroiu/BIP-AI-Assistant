import threading
import sys
import select

class KeyboardController:
    def __init__(self, main_app):
        self.main_app = main_app
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)

    def start(self):
        self.listener_thread.start()

    def stop(self):
        self.running = False

    def _listen_loop(self):
        print("[KEYBOARD] Non-blocking input engine ready.")
        while self.running and self.main_app.rc.is_alive:
            if sys.platform == "win32":
                import msvcrt
                if msvcrt.kbhit():
                    ch = msvcrt.getch().decode('utf-8', errors='ignore').upper()
                    self._handle_key(ch)
            else:
                ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                if ready:
                    ch = sys.stdin.read(1).upper()
                    self._handle_key(ch)

    def _handle_key(self, key):
        rc = self.main_app.rc
        self.main_app.idle.record_activity() # Any manual input breaks standard idle triggers
        
        # System & Gripper Actions
        if key == 'O': self.main_app.gripper.open_gripper()
        elif key == 'C': self.main_app.gripper.close_gripper_step()
        elif key == 'Y': self.main_app.gripper.confirm_grip()
        elif key == 'K': rc.emergency_stop()
        elif key == ' ': rc.stop_current_movement()
        elif key == 'H': rc.go_home()
        elif key == 'Q':
            print("[MAIN] Shutdown requested via keyboard input.")
            self.running = False
            self.main_app.shutdown()
            
        # Automated Mode Toggles
        elif key == 'T':
            self.main_app.tracker.tracking_enabled = not self.main_app.tracker.tracking_enabled
            print(f"[MODE] Automated Tracking state updated to: {self.main_app.tracker.tracking_enabled}")
        elif key == 'I':
            self.main_app.idle.is_idle = not self.main_app.idle.is_idle
            self.main_app.idle.start_idle_time = sys.time() if hasattr(sys, 'time') else 0.0
            print(f"[MODE] Manual Overridden Idle State configured to: {self.main_app.idle.is_idle}")

        # Cartesian Manual Controls
        elif key == 'W': rc.move_cartesian('z', 1)
        elif key == 'S': rc.move_cartesian('z', -1)
        elif key == 'A': rc.move_cartesian('y', 1)
        elif key == 'D': rc.move_cartesian('y', -1)
        elif key == 'F': rc.move_cartesian('x', 1)
        elif key == 'R': rc.move_cartesian('x', -1)
        
        # Independent Joint Controls (J1 through J6)
        elif key == '1': rc.move_joint(1, -1)
        elif key == '2': rc.move_joint(1, 1)
        elif key == '3': rc.move_joint(2, -1)
        elif key == '4': rc.move_joint(2, 1)
        elif key == '5': rc.move_joint(3, -1)
        elif key == '6': rc.move_joint(3, 1)
        elif key == '7': rc.move_joint(4, -1)
        elif key == '8': rc.move_joint(4, 1)
        elif key == '9': rc.move_joint(5, -1)
        elif key == '0': rc.move_joint(5, 1)
        elif key == '-': rc.move_joint(6, -1)
        elif key == '=': rc.move_joint(6, 1)