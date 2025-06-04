import cv2
from .base import Camera

class WebCamera(Camera):
    """普通网络摄像头类"""
    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.cap = None

    def start(self):
        """启动网络摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise Exception(f"无法打开摄像头 {self.camera_id}")
        self.is_running = True

    def stop(self):
        """停止网络摄像头"""
        if self.cap is not None:
            self.cap.release()
        self.is_running = False

    def get_frame(self):
        """获取当前帧"""
        if not self.is_running:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame 