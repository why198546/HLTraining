#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试ZIP解压和3D模型文件提取功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.hunyuan3d import Hunyuan3DGenerator

def test_zip_extraction():
    """测试现有ZIP文件的解压功能"""
    print("🧪 测试ZIP解压功能...")
    
    # 使用已下载的ZIP文件
    zip_path = "models/hunyuan3d_boy_model.zip"
    
    if not os.path.exists(zip_path):
        print(f"❌ 测试文件不存在: {zip_path}")
        return
        
    print(f"📦 测试ZIP文件: {zip_path}")
    
    try:
        # 初始化3D生成器
        generator = Hunyuan3DGenerator()
        
        # 测试解压功能
        extracted_model = generator._extract_model_from_zip(
            zip_path, 
            "test_boy", 
            "12345678"
        )
        
        if extracted_model:
            print(f"✅ 解压测试成功: {extracted_model}")
            
            # 检查文件大小
            if os.path.exists(extracted_model):
                file_size = os.path.getsize(extracted_model)
                print(f"📏 提取文件大小: {file_size} 字节")
            else:
                print("❌ 提取的文件不存在")
        else:
            print("❌ 解压测试失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_zip_extraction()