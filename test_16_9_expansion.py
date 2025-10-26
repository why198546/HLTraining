#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的16:9扩展逻辑
验证：原图作为16:9画面中间的9:16部分，向左右扩展
"""

import os
import sys
from PIL import Image, ImageDraw
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.nano_banana import NanoBananaAPI

def create_test_image():
    """创建一个测试图片（模拟1024分辨率）"""
    # 创建一个800x800的测试图片
    img = Image.new('RGB', (800, 800), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)
    
    # 绘制一些内容
    draw.rectangle([100, 100, 700, 700], fill=(255, 255, 255))
    draw.text((200, 200), "TEST IMAGE", fill=(0, 0, 0))
    draw.text((200, 300), "800x800", fill=(0, 0, 0))
    draw.text((200, 400), "Should be center", fill=(0, 0, 0))
    draw.text((200, 500), "of 16:9 frame", fill=(0, 0, 0))
    
    # 添加边缘标记
    draw.rectangle([0, 0, 800, 50], fill=(255, 0, 0))  # 顶部红色
    draw.rectangle([0, 750, 800, 800], fill=(0, 255, 0))  # 底部绿色
    draw.rectangle([0, 0, 50, 800], fill=(0, 0, 255))  # 左侧蓝色
    draw.rectangle([750, 0, 800, 800], fill=(255, 255, 0))  # 右侧黄色
    
    # 保存测试图片
    test_path = "static/uploads/test_800x800.png"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    img.save(test_path)
    print(f"✅ 创建测试图片: {test_path}")
    return test_path

def test_16_9_expansion():
    """测试16:9扩展功能"""
    print("🧪 开始测试16:9扩展功能")
    print("=" * 50)
    
    # 创建测试图片
    test_image_path = create_test_image()
    
    # 初始化API
    api = NanoBananaAPI()
    
    # 执行16:9扩展 - 功能已删除
    print("\n⚠️ 扩展取景功能已删除，跳过此测试...")
    print("❌ expand_image_for_framing 函数已被删除")
    return False
    
    # result = api.expand_image_for_framing(test_image_path)
    
    if result['success']:
        print(f"\n✅ 扩展成功!")
        print(f"📁 扩展图片路径: {result['expanded_path']}")
        print(f"📐 扩展图片尺寸: {result['expanded_width']}x{result['expanded_height']}")
        
        # 计算并验证比例
        ratio = result['expanded_width'] / result['expanded_height']
        target_ratio = 16.0 / 9.0
        ratio_error = abs(ratio - target_ratio)
        
        print(f"📊 实际比例: {ratio:.6f}")
        print(f"🎯 目标比例: {target_ratio:.6f}")
        print(f"📏 比例误差: {ratio_error:.8f}")
        
        if ratio_error < 0.001:
            print("✅ 比例精度: 优秀")
        elif ratio_error < 0.01:
            print("⚠️ 比例精度: 良好")
        else:
            print("❌ 比例精度: 需要改进")
        
        # 原图在扩展图中的位置
        original_region = result['original_region']
        print(f"\n📍 原图在扩展图中的位置:")
        print(f"   坐标: ({original_region['x']}, {original_region['y']})")
        print(f"   尺寸: {original_region['width']}x{original_region['height']}")
        
        # 验证原图是否在中央
        center_x = result['expanded_width'] // 2
        original_center_x = original_region['x'] + original_region['width'] // 2
        x_offset = abs(center_x - original_center_x)
        
        print(f"🎯 水平居中验证:")
        print(f"   扩展图中心X: {center_x}")
        print(f"   原图中心X: {original_center_x}")
        print(f"   偏移量: {x_offset}px")
        
        if x_offset <= 1:
            print("✅ 原图完美居中")
        else:
            print(f"⚠️ 原图偏移 {x_offset}px")
        
        # 推荐的裁剪区域
        suggested_crops = result.get('suggested_crops', {})
        if suggested_crops:
            print(f"\n📐 推荐裁剪区域:")
            for ratio_name, crop_info in suggested_crops.items():
                print(f"   {ratio_name}: ({crop_info['x']}, {crop_info['y']}) {crop_info['width']}x{crop_info['height']}")
        
        return True
        
    else:
        print(f"❌ 扩展失败: {result.get('error', '未知错误')}")
        return False

def verify_expansion_concept():
    """验证扩展概念的正确性"""
    print("\n🔍 验证扩展概念...")
    print("-" * 30)
    
    # 假设原图是800x800
    original_width, original_height = 800, 800
    print(f"原图尺寸: {original_width}x{original_height}")
    
    # 16:9的完整尺寸，以原图高度为基准
    final_height = original_height  # 800
    final_width = int(final_height * 16.0 / 9.0)  # 约1422
    
    print(f"16:9完整尺寸: {final_width}x{final_height}")
    
    # 9:16区域的宽度
    center_region_width = int(final_height * 9.0 / 16.0)  # 450
    print(f"中心9:16区域宽度: {center_region_width}")
    
    # 左右扩展宽度
    left_right_expansion = (final_width - center_region_width) // 2  # 486
    print(f"左右各扩展: {left_right_expansion}px")
    
    # 验证原图是否需要调整
    if original_width > center_region_width:
        print(f"⚠️ 原图过宽，需要缩放: {original_width} → {center_region_width}")
        scale_factor = center_region_width / original_width
        new_height = int(original_height * scale_factor)
        print(f"   缩放后高度: {original_height} → {new_height}")
        
        # 重新计算16:9尺寸
        final_height = new_height
        final_width = int(final_height * 16.0 / 9.0)
        print(f"   调整后16:9尺寸: {final_width}x{final_height}")
    else:
        print(f"✅ 原图宽度合适，无需缩放")
    
    # 计算最终比例
    final_ratio = final_width / final_height
    target_ratio = 16.0 / 9.0
    print(f"最终比例: {final_ratio:.6f} (目标: {target_ratio:.6f})")
    
    return True

if __name__ == "__main__":
    print("🎬 16:9扩展功能测试")
    print("=" * 50)
    
    # 验证概念
    verify_expansion_concept()
    
    # 执行实际测试
    success = test_16_9_expansion()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成: 16:9扩展功能正常!")
    else:
        print("❌ 测试失败: 需要检查代码")