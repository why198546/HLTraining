#!/usr/bin/env python3
"""
16:9图片转换功能测试脚本

测试 NanoBananaAPI 的图片16:9转换功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

def create_test_image():
    """创建一个测试用的1024x1024图片"""
    # 创建一个渐变色的正方形图片
    img = Image.new('RGB', (1024, 1024))
    pixels = img.load()
    
    for y in range(1024):
        for x in range(1024):
            # 创建从左上到右下的渐变
            r = int((x / 1024) * 255)
            g = int((y / 1024) * 255)
            b = int(((x + y) / 2048) * 255)
            pixels[x, y] = (r, g, b)
    
    test_path = 'uploads/test_square_1024.png'
    img.save(test_path)
    print(f"✅ 创建测试图片: {test_path}")
    return test_path

def test_conversion():
    """测试16:9转换功能"""
    from api.nano_banana import NanoBananaAPI
    
    print("\n" + "="*60)
    print("🧪 开始测试16:9图片转换功能")
    print("="*60 + "\n")
    
    # 初始化API
    api = NanoBananaAPI()
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 执行转换
    print("\n📐 执行16:9转换...")
    result_path = api._convert_to_16_9(test_image)
    
    # 验证结果
    if result_path and os.path.exists(result_path):
        result_img = Image.open(result_path)
        width, height = result_img.size
        ratio = width / height
        expected_ratio = 16 / 9
        
        print(f"\n✅ 转换成功!")
        print(f"   原始图片: {test_image}")
        print(f"   输出图片: {result_path}")
        print(f"   输出尺寸: {width}x{height}")
        print(f"   宽高比: {ratio:.4f}")
        print(f"   预期比例: {expected_ratio:.4f}")
        print(f"   误差: {abs(ratio - expected_ratio):.6f}")
        
        if abs(ratio - expected_ratio) < 0.01:
            print(f"\n🎉 测试通过! 宽高比正确!")
        else:
            print(f"\n⚠️  警告: 宽高比偏差较大!")
    else:
        print(f"\n❌ 转换失败!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # 确保uploads目录存在
    os.makedirs('uploads', exist_ok=True)
    
    try:
        test_conversion()
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
