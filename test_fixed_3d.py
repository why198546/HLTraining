#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的Hunyuan3D功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.hunyuan3d import Hunyuan3DGenerator

def test_3d_generation():
    """测试3D模型生成功能"""
    print("🧪 测试修复后的Hunyuan3D功能...")
    
    # 查找一个现有的图片文件进行测试
    test_image = None
    uploads_dir = "uploads"
    
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                test_image = os.path.join(uploads_dir, filename)
                break
    
    if not test_image:
        print("❌ 未找到测试图片文件")
        return
        
    print(f"🖼️ 使用测试图片: {test_image}")
    
    try:
        # 初始化3D生成器
        generator = Hunyuan3DGenerator()
        
        # 生成3D模型
        print("🚀 开始生成3D模型...")
        model_path = generator.generate_3d_model(test_image)
        
        if model_path:
            print(f"✅ 3D模型生成成功: {model_path}")
        else:
            print("❌ 3D模型生成失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_3d_generation()