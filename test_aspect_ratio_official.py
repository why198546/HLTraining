#!/usr/bin/env python3
"""
测试Gemini 2.5 Flash Image官方API的高宽比功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.nano_banana import NanoBananaAPI

def test_aspect_ratio():
    """测试不同高宽比的图片生成"""
    print("🧪 测试Gemini 2.5 Flash Image官方API高宽比功能")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 测试提示词
    prompt = "奥特曼"
    
    # 测试不同的高宽比
    aspect_ratios = ["1:1", "16:9", "9:16"]
    
    for aspect_ratio in aspect_ratios:
        print(f"\n🎯 测试高宽比: {aspect_ratio}")
        print("-" * 40)
        
        try:
            result = api.generate_image_from_text(
                text_prompt=prompt,
                style="cute",
                color_preference="colorful",
                expert_mode=False,
                aspect_ratio=aspect_ratio
            )
            
            if result:
                print(f"✅ 成功生成图片: {result}")
                
                # 检查生成图片的实际尺寸
                from PIL import Image
                with Image.open(result) as img:
                    width, height = img.size
                    actual_ratio = width / height
                    print(f"📐 图片尺寸: {width}x{height}")
                    print(f"📊 实际比例: {actual_ratio:.4f}")
                    
                    # 计算期望比例
                    if aspect_ratio == "1:1":
                        expected_ratio = 1.0
                    elif aspect_ratio == "16:9":
                        expected_ratio = 16.0 / 9.0
                    elif aspect_ratio == "9:16":
                        expected_ratio = 9.0 / 16.0
                    
                    print(f"🎯 期望比例: {expected_ratio:.4f}")
                    ratio_error = abs(actual_ratio - expected_ratio)
                    print(f"📏 比例误差: {ratio_error:.4f}")
                    
                    if ratio_error < 0.1:
                        print("✅ 高宽比控制成功!")
                    else:
                        print("⚠️ 高宽比可能有偏差")
            else:
                print(f"❌ 生成失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print(f"\n🏁 测试完成!")

if __name__ == "__main__":
    test_aspect_ratio()