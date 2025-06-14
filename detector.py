import cv2
import numpy as np
import yaml
from typing import List, Dict, Optional, Tuple
import warnings
import os
import onnxruntime
from utils import letterbox, scale_coords

# 过滤特定的警告
warnings.filterwarnings("ignore", category=FutureWarning)

class YOLODetector:
    """YOLOv5目标检测类"""
    def __init__(self, model_path: str, yaml_path: str = None, conf_threshold: float = 0.25):
        """
        初始化检测器
        Args:
            model_path: YOLOv5 ONNX模型路径
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
        
        self.conf_threshold = conf_threshold
        self.img_size = 640
        self.init_onnx_model(model_path)

    def init_onnx_model(self, model_path: str):
        """初始化ONNX模型"""
        self.model = onnxruntime.InferenceSession(model_path)
        self.input_name = self.model.get_inputs()[0].name
        self.output_name = self.model.get_outputs()[0].name
        input_shape = self.model.get_inputs()[0].shape
        print(f"ONNX模型输入形状: {input_shape}")

    def preprocess(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """预处理图像"""
        img0 = frame.copy()
        img = letterbox(frame, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img).astype(np.float32)
        img /= 255.0
        img = np.expand_dims(img, axis=0)
        return img0, img

    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        检测图像中的目标
        Args:
            frame: 输入图像
        Returns:
            检测结果列表，每个结果包含类别、置信度、边界框和中心点坐标
        """
        img0, img = self.preprocess(frame)
        pred = self.model.run(None, {self.input_name: img})[0]
        pred = pred.astype(np.float32)
        pred = np.squeeze(pred, axis=0)
        
        detections = []
        for detection in pred:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id] * detection[4]

            if confidence > self.conf_threshold:
                box = detection[0:4]
                (center_x, center_y, width, height) = box.astype("int")
                x1 = int(center_x - (width / 2))
                y1 = int(center_y - (height / 2))
                x2 = x1 + int(width)
                y2 = y1 + int(height)
                
                # 坐标还原
                box = np.array([[x1, y1, x2, y2]], dtype=np.float32)
                box = scale_coords((self.img_size, self.img_size), box, img0.shape[:2])
                x1, y1, x2, y2 = map(int, box[0])
                
                detection = {
                    'class': int(class_id),
                    'class_name': self.names.get(int(class_id), str(int(class_id))),
                    'confidence': float(confidence),
                    'bbox': (x1, y1, x2, y2),
                    'center': (int((x1 + x2) / 2), int((y1 + y2) / 2))
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