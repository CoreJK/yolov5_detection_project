from abc import ABC, abstractmethod

class Camera(ABC):
    """摄像头基类"""
    def __init__(self):
        self.frame = None
        self.is_running = False

    @abstractmethod
    def start(self):
        """启动摄像头"""
        pass

    @abstractmethod
    def stop(self):
        """停止摄像头"""
        pass

    @abstractmethod
    def get_frame(self):
        """获取当前帧"""
        pass 