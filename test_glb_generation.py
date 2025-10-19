#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试GLB格式3D模型生成
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from api.hunyuan3d import Hunyuan3DGenerator

def test_glb_generation():
    """测试GLB格式的3D模型生成"""
    print("🧪 测试GLB格式3D模型生成...")
    
    # 使用之前生成的图片进行测试
    test_image = "uploads/nano_banana_text_1760883592.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        # 查找其他可用的图片
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            image_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if image_files:
                test_image = os.path.join(uploads_dir, image_files[0])
                print(f"✅ 使用测试图片: {test_image}")
            else:
                print("❌ uploads目录中没有找到图片文件")
                return False
        else:
            print("❌ uploads目录不存在")
            return False
    
    try:
        # 初始化3D生成器
        generator = Hunyuan3DGenerator()
        
        # 生成3D模型
        print(f"🎯 开始生成GLB格式3D模型: {test_image}")
        model_path = generator.generate_3d_model(test_image)
        
        if model_path:
            print(f"✅ GLB模型生成成功: {model_path}")
            
            # 检查文件是否存在和大小
            if os.path.exists(model_path):
                file_size = os.path.getsize(model_path)
                print(f"📏 文件大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")
                
                # 检查文件扩展名
                if model_path.endswith('.glb'):
                    print("✅ 文件格式正确：GLB")
                    return True
                else:
                    print(f"❌ 文件格式错误：期望.glb，实际{os.path.splitext(model_path)[1]}")
                    return False
            else:
                print(f"❌ 生成的文件不存在: {model_path}")
                return False
        else:
            print("❌ 3D模型生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_glb_generation()
    if success:
        print("\n🎉 GLB格式3D生成测试成功！")
    else:
        print("\n❌ GLB格式3D生成测试失败！")