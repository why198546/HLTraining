#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 Gemini API 连接和图片生成功能"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import io

from dotenv import load_dotenv
from PIL import Image

from api.nano_banana import NanoBananaAPI

# 加载环境变量
load_dotenv()

def test_gemini_api():
    """测试 Gemini API 是否可用"""
    print("=" * 60)
    print("🔍 测试 Gemini API 连接")
    print("=" * 60)
    
    # 检查 API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    print(f"✅ GEMINI_API_KEY 已设置 (长度: {len(api_key)})")
    
    # 初始化 API
    try:
        nb_api = NanoBananaAPI()
        print("✅ NanoBananaAPI 初始化成功")
        
        if not nb_api.client:
            print("❌ Google Gen AI 客户端未初始化")
            return False
        
        print("✅ Google Gen AI 客户端已初始化")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    # 创建一个简单的测试图片
    print("\n📝 创建测试图片...")
    test_image = Image.new('RGB', (100, 100), color='white')
    test_path = '/tmp/test_sketch.png'
    test_image.save(test_path)
    print(f"✅ 测试图片已保存: {test_path}")
    
    # 尝试生成图片
    print("\n🎨 尝试调用 AI 生成图片...")
    try:
        result_path = nb_api.generate_image_from_reference(
            sketch_path=test_path,
            description="A simple colorful test image",
            style="cute",
            aspect_ratio="256x256"
        )
        
        if result_path:
            print(f"✅ AI 生成成功: {result_path}")
            # 检查文件是否存在
            if os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"✅ 生成的文件大小: {file_size} 字节")
                return True
            else:
                print(f"⚠️ 文件路径不存在: {result_path}")
                return False
        else:
            print("❌ AI 生成失败 (返回 None)")
            return False
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_path):
            os.remove(test_path)
            print(f"\n🧹 已清理测试文件")

if __name__ == '__main__':
    success = test_gemini_api()
    print("\n" + "=" * 60)
    if success:
        print("✅ API 测试通过！")
        sys.exit(0)
    else:
        print("❌ API 测试失败")
        sys.exit(1)
