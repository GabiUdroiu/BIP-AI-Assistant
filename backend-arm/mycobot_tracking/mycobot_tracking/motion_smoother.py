import time

class PIDController:
    """Standard Derivative-filtered Proportional Controller to guarantee smooth tracking velocities."""
    def __init__(self, kp, kd):
        self.kp = kp
        self.kd = kd
        self.prev_error = 0.0
        self.prev_time = time.time()

    def compute(self, error):
        current_time = time.time()
        dt = current_time - self.prev_time
        
        if dt <= 0.0:
            dt = 1e-3  # Prevent division by zero errors

        # Calculate derivative component
        derivative = (error - self.prev_error) / dt
        
        # Calculate control signal: u(t) = K_p e(t) + K_d \frac{de(t)}{dt}
        output = (self.kp * error) + (self.kd * derivative)
        
        # Update historical state
        self.prev_error = error
        self.prev_time = current_time
        return output

    def reset(self):
        self.prev_error = 0.0
        self.prev_time = time.time()