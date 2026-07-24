import time
from config import GRIPPER_OPEN_VALUE, GRIPPER_MIN_SAFE_LIMIT, GRIPPER_STEP_SIZE, GRIPPER_CLOSE_SPEED

class GripperController:
    def __init__(self, robot_controller):
        self.rc = robot_controller
        self.current_value = GRIPPER_OPEN_VALUE
        self.is_confirmed = False

    def open_gripper(self):
        if not self.rc.is_alive: return
        print("[GRIPPER] Opening gripper fully...")
        self.current_value = GRIPPER_OPEN_VALUE
        self.is_confirmed = False
        
        if self.rc.connected and self.rc.mc:
            self.rc.mc.set_gripper_value(GRIPPER_OPEN_VALUE, GRIPPER_CLOSE_SPEED)
        print(f"[GRIPPER] Gripper value set to: {self.current_value}")

    def close_gripper_step(self):
        if not self.rc.is_alive: return
        if self.current_value <= GRIPPER_MIN_SAFE_LIMIT:
            print(f"[WARNING] Gripper hit the safe limit boundary ({GRIPPER_MIN_SAFE_LIMIT})!")
            return

        self.current_value -= GRIPPER_STEP_SIZE
        if self.current_value < GRIPPER_MIN_SAFE_LIMIT:
            self.current_value = GRIPPER_MIN_SAFE_LIMIT

        print(f"[GRIPPER] Closing slowly. Current target: {self.current_value}")
        
        if self.rc.connected and self.rc.mc:
            self.rc.mc.set_gripper_value(self.current_value, GRIPPER_CLOSE_SPEED)

    def confirm_grip(self):
        if self.current_value == GRIPPER_OPEN_VALUE:
            print("[GRIPPER] Cannot confirm grip while gripper is wide open!")
            return False
        self.is_confirmed = True
        print("[GRIPPER] Phone grip confirmed by user. Safe to proceed.")
        return True