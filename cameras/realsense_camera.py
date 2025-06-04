import cv2
import pyrealsense2 as rs
import numpy as np
from .base import Camera

class RealSenseCamera(Camera):
    """RealSense摄像头类"""
    def __init__(self):
        super().__init__()
        self.pipeline = None
        self.config = None
        self.align = None
        self.depth_frame = None
        self.color_frame = None

    def start(self):
        """启动RealSense摄像头"""
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.align = rs.align(rs.stream.color)
        self.pipeline.start(self.config)
        self.is_running = True

    def stop(self):
        """停止RealSense摄像头"""
        if self.pipeline is not None:
            self.pipeline.stop()
        self.is_running = False

    def get_frame(self):
        """获取当前帧"""
        if not self.is_running:
            return None
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        
        # 获取对齐后的深度帧和彩色帧
        self.depth_frame = aligned_frames.get_depth_frame()
        self.color_frame = aligned_frames.get_color_frame()
        
        if not self.color_frame:
            return None
        return np.asanyarray(self.color_frame.get_data())

    def get_depth_at_point(self, x: int, y: int) -> float:
        """
        获取指定像素点的深度值
        Args:
            x: 像素x坐标
            y: 像素y坐标
        Returns:
            深度值（毫米）
        """
        if self.depth_frame is None:
            return None
        
        # 确保坐标在有效范围内
        if 0 <= x < self.depth_frame.get_width() and 0 <= y < self.depth_frame.get_height():
            depth = self.depth_frame.get_distance(x, y)
            return depth
        return None

    def get_depth_frame(self):
        """获取深度帧"""
        if not self.is_running or self.depth_frame is None:
            return None
        return np.asanyarray(self.depth_frame.get_data()) 