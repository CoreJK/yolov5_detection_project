# YOLOv5 目标检测项目

这是一个基于 YOLOv5 的目标检测项目，支持普通摄像头和 RealSense 深度摄像头。

## 项目结构

```
yolov5_detection_project/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖包列表
├── main.py                   # 主程序
├── detector.py               # 检测器模块
├── cameras/                  # 相机模块目录
│   ├── __init__.py          # 相机模块初始化文件
│   ├── base.py              # 相机基类
│   ├── web_camera.py        # 普通摄像头类
│   └── realsense_camera.py  # RealSense摄像头类
├── datasets/                 # 数据集目录
│   └── custom.yaml          # 数据集配置文件
└── models/                   # 模型目录
    └── best.pt              # 训练好的模型文件
```

## 环境要求

- Python 3.8 或更高版本
- CUDA 11.0 或更高版本（用于 GPU 加速）
- OpenCV 4.5.0 或更高版本
- PyTorch 1.7.0 或更高版本
- Intel RealSense SDK 2.0（仅在使用 RealSense 摄像头时需要）

## 安装依赖

1. 克隆项目：
```bash
git clone https://github.com/yourusername/yolov5_detection_project.git
cd yolov5_detection_project
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

4. 如果使用 RealSense 摄像头，安装 RealSense SDK：
```bash
pip install pyrealsense2
```

## 使用方法

1. 确保已安装所有依赖
2. 将训练好的模型文件 `best.pt` 放在 `models` 目录下
3. 运行主程序：
   ```bash
   python main.py
   ```
4. 根据提示选择摄像头类型：
   - 1: 普通摄像头
   - 2: RealSense 深度摄像头

## 功能特点

- 支持多种摄像头类型：
  - 普通网络摄像头
  - RealSense 深度摄像头
- 实时目标检测
- 显示检测框、类别名称和置信度
- 使用 RealSense 摄像头时可获取目标深度信息
- 按 'q' 键退出程序

## 相机模块说明

### 基类 (Camera)
- 定义了所有相机类型必须实现的接口
- 包含基本的摄像头状态管理
- 提供统一的启动、停止和获取帧的方法

### 普通摄像头 (WebCamera)
- 支持标准网络摄像头
- 可配置摄像头ID
- 提供基本的图像捕获功能

### RealSense摄像头 (RealSenseCamera)
- 支持 Intel RealSense 深度摄像头
- 提供彩色图像和深度信息
- 支持深度帧和彩色帧对齐
- 可获取指定像素点的深度值

## 常见问题解答

1. **Q: 程序无法启动摄像头**
   - A: 检查摄像头是否正确连接
   - A: 确认摄像头ID是否正确（默认为0）
   - A: 检查是否有其他程序占用摄像头

2. **Q: RealSense 摄像头无法获取深度信息**
   - A: 确保已正确安装 RealSense SDK
   - A: 检查摄像头固件是否为最新版本
   - A: 确认摄像头与电脑的连接是否稳定

3. **Q: 检测效果不理想**
   - A: 检查模型文件是否正确放置
   - A: 确认 custom.yaml 中的类别配置是否正确
   - A: 考虑重新训练模型或调整检测参数

## 注意事项

1. 使用 RealSense 摄像头时需要安装 pyrealsense2 库
2. 确保 `custom.yaml` 文件中的类别名称配置正确
3. 模型文件 `best.pt` 需要放在正确的位置
4. 如果使用普通摄像头，确保摄像头ID正确（默认为0）

## 扩展新相机类型

如果需要添加新的相机类型，请按照以下步骤操作：

1. 在 `cameras` 目录下创建新的相机类文件
2. 继承 `Camera` 基类
3. 实现必要的方法：
   - `start()`: 启动摄像头
   - `stop()`: 停止摄像头
   - `get_frame()`: 获取当前帧
4. 在 `cameras/__init__.py` 中导出新的相机类

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：your.email@example.com 