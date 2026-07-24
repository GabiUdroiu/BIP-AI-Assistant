import time
import math
from config import IDLE_TIMEOUT, IDLE_AMPLITUDE_Z, IDLE_FREQUENCY

class IdleController:
    """Handles the 4-second interaction timeouts and builds a 2D-sinusoidal motion profile."""
    def __init__(self):
        self.last_activity_time = time.time()
        self.is_idle = False
        self.start_idle_time = 0.0

    def record_activity(self):
        """Resets the timeout countdown whenever a user or tracking command triggers action."""
        self.last_activity_time = time.time()
        if self.is_idle:
            print("[IDLE] System interaction detected. Suspending idle animation patterns.")
            self.is_idle = False

    def update(self):
        """Evaluates timestamps and returns programmatic offset adjustment maps."""
        current_time = time.time()
        
        if not self.is_idle and (current_time - self.last_activity_time >= IDLE_TIMEOUT):
            print("[IDLE] System silent for 4 seconds. Initiating smooth passive bounce sequences.")
            self.is_idle = True
            self.start_idle_time = current_time

        if self.is_idle:
            elapsed = current_time - self.start_idle_time
            # Generate continuous sinusoidal wave patterns: \Delta z = A \cdot \sin(2\pi f \cdot t)
            z_offset = IDLE_AMPLITUDE_Z * math.sin(2 * math.pi * IDLE_FREQUENCY * elapsed)
            return z_offset
        
        return 0.0