import torch
import cv2
import numpy as np
import yaml
from typing import List, Tuple, Dict, Optional
import warnings
import os

# 过滤特定的警告
warnings.filterwarnings("ignore", category=FutureWarning)

class YOLODetector:
    """YOLOv5目标检测类"""
    def __init__(self, model_path: str, yaml_path: str = None, conf_threshold: float = 0.25):
        """
        初始化检测器
        Args:
            model_path: YOLOv5模型路径
            yaml_path: 数据集配置文件路径，如果为None则使用默认路径
            conf_threshold: 置信度阈值
        """
        # 加载类别名称
        if yaml_path is None:
            # 使用默认路径：与模型同目录下的custom.yaml
            yaml_path = os.path.join(os.path.dirname(model_path), "custom.yaml")
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
                self.names = yaml_data.get('names', {})
        except Exception as e:
            print(f"警告：无法加载YAML文件 {yaml_path}，将使用类别索引作为名称")
            self.names = {}
        
        with torch.amp.autocast('cuda'):
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            self.model.conf = conf_threshold
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        检测图像中的目标
        Args:
            frame: 输入图像
        Returns:
            检测结果列表，每个结果包含类别、置信度、边界框和中心点坐标
        """
        with torch.amp.autocast('cuda'):
            results = self.model(frame)
            detections = []
            
            for *xyxy, conf, cls in results.xyxy[0].cpu().numpy():
                x1, y1, x2, y2 = map(int, xyxy)
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                detection = {
                    'class': int(cls),
                    'class_name': self.names.get(int(cls), str(int(cls))),
                    'confidence': float(conf),
                    'bbox': (x1, y1, x2, y2),
                    'center': (center_x, center_y)
                }
                detections.append(detection)
            
            return detections

    def draw_detections(self, frame: np.ndarray, detections: List[Dict], depth_info: Optional[Dict] = None) -> np.ndarray:
        """
        在图像上绘制检测结果
        Args:
            frame: 输入图像
            detections: 检测结果列表
            depth_info: 深度信息字典，键为检测索引，值为深度值
        Returns:
            绘制了检测结果的图像
        """
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            center_x, center_y = det['center']
            
            # 绘制边界框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 准备标签文本
            label = f"{det['class_name']}: {det['confidence']:.2f}"
            if depth_info and i in depth_info:
                label += f" | Depth: {depth_info[i]:.2f}m"
            
            # 绘制标签背景
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), (0, 255, 0), -1)
            
            # 绘制标签文本
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            # 绘制中心点
            cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)
        
        return frame 