import cv2
import threading
import time
from config import CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT

class CameraStream:
    """Threaded camera ingestion module to prevent OpenCV frame capture from blocking system execution loops."""
    def __init__(self):
        self.stream_source = CAMERA_SOURCE
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None

    def start(self):
        print(f"[CAMERA] Initializing video capture source: {self.stream_source}")
        self.cap = cv2.VideoCapture(self.stream_source)
        
        # Configure frame bounding box optimizations
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print("[CAMERA] Asynchronous frame capture thread successfully deployed.")

    def _update_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[CAMERA] Error: Failed to extract frame from stream matrix source.")
                time.sleep(0.5)
                continue
            # Store the latest valid video frame frame buffer
            self.frame = frame
            time.sleep(0.01)

    def read_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        print("[CAMERA] Video stream pipeline terminated cleanly.")