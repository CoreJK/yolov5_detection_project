import cv2
import time
import os
from cameras import WebCamera, RealSenseCamera
from detector import YOLODetector

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 初始化检测器
    model_path = os.path.join(current_dir, "models", "best.pt")  # 使用训练好的模型
    yaml_path = os.path.join(current_dir, "datasets", "custom.yaml")
    detector = YOLODetector(model_path, yaml_path=yaml_path, conf_threshold=0.75)

    # 选择摄像头类型
    print("请选择摄像头类型：")
    print("1. 普通摄像头")
    print("2. RealSense摄像头")
    choice = input("请输入选择（1或2）：")

    # 初始化摄像头
    if choice == "1":
        camera = WebCamera(camera_id=0)
    else:
        camera = RealSenseCamera()

    try:
        # 启动摄像头
        camera.start()
        print("摄像头已启动")

        while True:
            # 获取图像帧
            frame = camera.get_frame()
            if frame is None:
                continue

            # 执行检测
            detections = detector.detect(frame)
            
            # 获取深度信息（如果是RealSense摄像头）
            depth_info = {}
            if isinstance(camera, RealSenseCamera):
                for i, det in enumerate(detections):
                    center_x, center_y = det['center']
                    depth = camera.get_depth_at_point(center_x, center_y)
                    if depth is not None:
                        depth_info[i] = depth / 1000.0  # 转换为米

            # 绘制检测结果
            frame = detector.draw_detections(frame, detections, depth_info)

            # 显示结果
            cv2.imshow("Object Detection", frame)

            # 打印检测结果
            for i, det in enumerate(detections):
                depth_str = f", 深度: {depth_info[i]:.2f}m" if i in depth_info else ""
                print(f"检测到物体: 类别={det['class_name']}, 置信度={det['confidence']:.2f}, "
                      f"中心点=({det['center'][0]}, {det['center'][1]}){depth_str}")

            # 按'q'退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        # 清理资源
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 