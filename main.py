import cv2
import time
import os
from cameras import WebCamera, RealSenseCamera
from detector import YOLODetector

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 选择模型类型
    print("请选择模型类型：")
    print("1. PyTorch模型 (.pt)")
    print("2. ONNX模型 (.onnx)")
    model_choice = input("请输入选择（1或2）：")
    use_onnx = model_choice == "2"
    
    # 设置模型路径
    if use_onnx:
        model_path = os.path.join(current_dir, "models", "best.onnx")
    else:
        model_path = os.path.join(current_dir, "models", "best.pt")
    
    # 初始化检测器
    yaml_path = os.path.join(current_dir, "datasets", "custom.yaml")
    detector = YOLODetector(model_path, yaml_path=yaml_path, conf_threshold=0.75, use_onnx=use_onnx)

    # 选择摄像头类型
    print("\n请选择摄像头类型：")
    print("1. 普通摄像头")
    print("2. RealSense摄像头")
    choice = input("请输入选择（1或2）：")

    # 初始化摄像头
    if choice == "1":
        camera = WebCamera(camera_id=0)
    else:
        # 询问是否启用深度检测
        print("\n是否启用深度检测？")
        print("1. 是")
        print("2. 否")
        depth_choice = input("请输入选择（1或2）：")
        enable_depth = depth_choice == "1"
        camera = RealSenseCamera(enable_depth=enable_depth)

    try:
        # 启动摄像头
        camera.start()
        print("摄像头已启动")
        if isinstance(camera, RealSenseCamera):
            print(f"深度检测状态: {'已启用' if camera.enable_depth else '已禁用'}")

        while True:
            # 获取图像帧
            frame = camera.get_frame()
            if frame is None:
                continue

            # 执行检测
            detections = detector.detect(frame)
            
            # 先获取深度信息（在翻转前，使用原始坐标）
            depth_info = {}
            if isinstance(camera, RealSenseCamera) and camera.enable_depth:
                for i, det in enumerate(detections):
                    center_x, center_y = det['center']
                    depth = camera.get_depth_at_point(center_x, center_y)
                    if depth is not None:
                        depth_info[i] = depth  # RealSense返回的就是米

            # 左右翻转图像
            frame = cv2.flip(frame, 1)
            
            # 调整检测框坐标以匹配翻转后的图像
            for det in detections:
                # 获取图像宽度
                img_width = frame.shape[1]
                # 翻转边界框坐标
                x1, y1, x2, y2 = det['bbox']
                det['bbox'] = (img_width - x2, y1, img_width - x1, y2)
                # 翻转中心点坐标
                center_x, center_y = det['center']
                det['center'] = (img_width - center_x, center_y)

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