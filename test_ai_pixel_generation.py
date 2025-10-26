#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试AI像素生成功能
验证：使用大模型真正生成外部像素，而不是拉伸
"""

import os
import sys
from PIL import Image, ImageDraw
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.nano_banana import NanoBananaAPI

def create_test_image_with_clear_boundaries():
    """创建一个边界清晰的测试图片，便于验证AI是否真正生成了新像素"""
    # 创建一个600x600的测试图片，有明显的边界特征
    img = Image.new('RGB', (600, 600), color=(50, 50, 50))
    draw = ImageDraw.Draw(img)
    
    # 绘制明显的边界标记
    # 左边界 - 蓝色条纹
    for i in range(0, 600, 40):
        draw.rectangle([0, i, 30, i+20], fill=(0, 100, 255))
    
    # 右边界 - 红色条纹  
    for i in range(0, 600, 40):
        draw.rectangle([570, i, 600, i+20], fill=(255, 50, 50))
    
    # 中心内容
    draw.rectangle([100, 100, 500, 500], fill=(255, 255, 255))
    draw.text((150, 200), "ORIGINAL IMAGE", fill=(0, 0, 0))
    draw.text((150, 250), "600x600", fill=(0, 0, 0))
    draw.text((150, 300), "Clear Boundaries", fill=(0, 0, 0))
    draw.text((150, 350), "Test AI Generation", fill=(0, 0, 0))
    
    # 添加明显的边缘识别元素
    # 顶部边界
    draw.rectangle([0, 0, 600, 20], fill=(255, 255, 0))
    draw.text((250, 5), "TOP EDGE", fill=(0, 0, 0))
    
    # 底部边界
    draw.rectangle([0, 580, 600, 600], fill=(0, 255, 0))
    draw.text((250, 585), "BOTTOM EDGE", fill=(0, 0, 0))
    
    # 保存测试图片
    test_path = "static/uploads/ai_test_clear_boundaries.png"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    img.save(test_path)
    print(f"✅ 创建边界清晰测试图片: {test_path}")
    return test_path

def analyze_pixel_generation(original_path, expanded_path):
    """分析AI是否真正生成了新像素"""
    try:
        original_img = Image.open(original_path)
        expanded_img = Image.open(expanded_path)
        
        print(f"\n🔍 像素生成分析:")
        print(f"原图尺寸: {original_img.size}")
        print(f"扩展图尺寸: {expanded_img.size}")
        
        # 计算原图在扩展图中的位置
        expanded_width, expanded_height = expanded_img.size
        original_width, original_height = original_img.size
        
        center_x = (expanded_width - original_width) // 2
        center_y = (expanded_height - original_height) // 2
        
        print(f"原图在扩展图中的位置: ({center_x}, {center_y})")
        
        # 提取扩展图中央的原图区域
        extracted_center = expanded_img.crop((
            center_x, center_y, 
            center_x + original_width, 
            center_y + original_height
        ))
        
        # 保存提取的中央区域，用于对比
        extracted_path = "static/uploads/extracted_center.png"
        extracted_center.save(extracted_path)
        print(f"📁 提取的中央区域保存为: {extracted_path}")
        
        # 分析左右两侧的生成区域
        if center_x > 0:
            # 左侧生成区域
            left_region = expanded_img.crop((0, 0, center_x, expanded_height))
            left_path = "static/uploads/generated_left.png"
            left_region.save(left_path)
            print(f"📁 左侧生成区域: {left_path} (宽度: {center_x}px)")
            
            # 右侧生成区域
            right_region = expanded_img.crop((center_x + original_width, 0, expanded_width, expanded_height))
            right_path = "static/uploads/generated_right.png"
            right_region.save(right_path)
            print(f"📁 右侧生成区域: {right_path} (宽度: {expanded_width - center_x - original_width}px)")
            
            # 分析左右区域的像素特征
            analyze_generated_region(left_region, "左侧")
            analyze_generated_region(right_region, "右侧")
        
        return True
        
    except Exception as e:
        print(f"❌ 像素分析失败: {str(e)}")
        return False

def analyze_generated_region(region_img, region_name):
    """分析生成区域的像素特征"""
    try:
        import numpy as np
        
        # 转换为numpy数组进行分析
        region_array = np.array(region_img)
        
        # 计算颜色统计
        mean_color = np.mean(region_array, axis=(0, 1))
        std_color = np.std(region_array, axis=(0, 1))
        
        print(f"🎨 {region_name}生成区域分析:")
        print(f"   平均颜色: RGB({mean_color[0]:.1f}, {mean_color[1]:.1f}, {mean_color[2]:.1f})")
        print(f"   颜色变化: RGB({std_color[0]:.1f}, {std_color[1]:.1f}, {std_color[2]:.1f})")
        
        # 检查是否有足够的变化（说明不是简单填充）
        total_variation = np.sum(std_color)
        if total_variation > 50:
            print(f"   ✅ 像素变化丰富 (变化值: {total_variation:.1f}) - 疑似AI生成")
        elif total_variation > 10:
            print(f"   ⚠️ 像素变化中等 (变化值: {total_variation:.1f}) - 可能是处理后的结果")
        else:
            print(f"   ❌ 像素变化很少 (变化值: {total_variation:.1f}) - 疑似简单填充")
            
    except Exception as e:
        print(f"❌ {region_name}区域分析失败: {str(e)}")

def test_ai_pixel_generation():
    """测试AI像素生成功能"""
    print("🎨 AI像素生成功能测试")
    print("=" * 60)
    
    # 创建边界清晰的测试图片
    test_image_path = create_test_image_with_clear_boundaries()
    
    # 初始化API
    print("\n🤖 初始化AI API...")
    api = NanoBananaAPI()
    
    # 检查AI客户端状态
    if api.client:
        print("✅ Gemini AI客户端初始化成功 - 将使用真正的AI生成")
    else:
        print("⚠️ Gemini AI客户端未初始化 - 将使用智能备用方案")
    
    # 执行16:9扩展 - 功能已删除
    print(f"\n⚠️ 扩展取景功能已删除，跳过此测试...")
    print("❌ expand_image_for_framing 函数已被删除")
    return False
    
    # result = api.expand_image_for_framing(test_image_path)
    
    if result['success']:
        print(f"\n✅ 扩展成功!")
        print(f"📁 扩展图片路径: {result['expanded_path']}")
        print(f"📐 扩展图片尺寸: {result['expanded_width']}x{result['expanded_height']}")
        
        # 分析像素生成质量
        print(f"\n🔬 分析AI像素生成质量...")
        analyze_pixel_generation(test_image_path, result['expanded_path'])
        
        # 验证比例精度
        ratio = result['expanded_width'] / result['expanded_height']
        target_ratio = 16.0 / 9.0
        ratio_error = abs(ratio - target_ratio)
        
        print(f"\n📊 比例验证:")
        print(f"   实际比例: {ratio:.6f}")
        print(f"   目标比例: {target_ratio:.6f}")
        print(f"   误差: {ratio_error:.8f}")
        
        if ratio_error < 0.001:
            print("   ✅ 比例精度: 优秀")
        else:
            print("   ⚠️ 比例精度: 需要改进")
        
        return result['expanded_path']
        
    else:
        print(f"❌ 扩展失败: {result.get('error', '未知错误')}")
        return None

def generate_comparison_report(expanded_path):
    """生成对比报告"""
    if not expanded_path:
        return
        
    print(f"\n📋 生成对比报告...")
    
    report = f"""
# AI像素生成测试报告

## 测试时间
{time.strftime('%Y-%m-%d %H:%M:%S')}

## 测试文件
- 原始测试图片: ai_test_clear_boundaries.png (600x600)
- AI扩展结果: {os.path.basename(expanded_path)}
- 提取的中央区域: extracted_center.png
- 左侧生成区域: generated_left.png  
- 右侧生成区域: generated_right.png

## 测试目的
验证AI是否真正生成了外部像素，而不是简单的拉伸或复制

## 验证方法
1. 创建边界清晰的测试图片，包含明显的边缘标记
2. 使用AI扩展为16:9格式
3. 分析左右两侧生成区域的像素特征
4. 检查是否为AI创造的新内容

## 判断标准
- ✅ AI生成：左右区域有丰富的像素变化，内容与原图边缘自然融合
- ⚠️ 处理后：有一定变化但可能是算法处理的结果
- ❌ 简单填充：左右区域像素变化很少，明显是拉伸或复制

请查看生成的图片文件进行人工验证。
"""
    
    report_path = "AI_PIXEL_GENERATION_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 测试报告已保存: {report_path}")

if __name__ == "__main__":
    print("🎨 AI像素生成功能专项测试")
    print("=" * 60)
    print("🎯 测试目标: 验证AI是否真正生成外部像素")
    print("💡 测试方法: 使用边界清晰的图片，分析生成区域特征")
    print("")
    
    # 执行测试
    expanded_path = test_ai_pixel_generation()
    
    # 生成报告
    generate_comparison_report(expanded_path)
    
    print("\n" + "=" * 60)
    if expanded_path:
        print("🎉 测试完成!")
        print("👀 请查看生成的图片文件，人工验证AI像素生成质量")
        print("📄 详细报告请查看: AI_PIXEL_GENERATION_REPORT.md")
    else:
        print("❌ 测试失败，请检查配置和代码")