import os
import shutil
import random
from pathlib import Path
import yaml

def create_directories():
    """创建必要的目录结构"""
    dirs = [
        'images/train',
        'images/val',
        'labels/train',
        'labels/val'
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def split_dataset(source_dir, train_ratio=0.8):
    """划分数据集为训练集和验证集"""
    # 获取所有图片文件
    image_files = [f for f in os.listdir(source_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    # 随机打乱文件列表
    random.shuffle(image_files)
    
    # 计算训练集大小
    train_size = int(len(image_files) * train_ratio)
    
    # 划分数据集
    train_files = image_files[:train_size]
    val_files = image_files[train_size:]
    
    return train_files, val_files

def copy_and_rename_files(source_dir, files, target_dir, prefix):
    """复制并重命名文件"""
    for i, file in enumerate(files, 1):
        # 构建新的文件名
        new_name = f"{prefix}_{i:04d}{Path(file).suffix}"
        
        # 复制文件
        shutil.copy2(
            os.path.join(source_dir, file),
            os.path.join(target_dir, new_name)
        )

def create_dataset_yaml():
    """创建数据集配置文件"""
    yaml_content = {
        'path': '../datasets',  # 数据集根目录
        'train': 'images/train',  # 训练集图片路径
        'val': 'images/val',      # 验证集图片路径
        'names': {
            0: 'object'  # 类别名称，根据实际情况修改
        }
    }
    
    with open('custom.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, allow_unicode=True)

def main():
    # 设置随机种子
    random.seed(42)
    
    # 创建目录结构
    create_directories()
    
    # 划分数据集
    train_files, val_files = split_dataset('pre_datas')
    
    # 复制并重命名文件
    copy_and_rename_files('pre_datas', train_files, 'images/train', 'train')
    copy_and_rename_files('pre_datas', val_files, 'images/val', 'val')
    
    # 创建数据集配置文件
    create_dataset_yaml()
    
    print(f"数据集准备完成！")
    print(f"训练集图片数量: {len(train_files)}")
    print(f"验证集图片数量: {len(val_files)}")

if __name__ == '__main__':
    main() 