#!/usr/bin/env python3
"""
实际视频生成测试 - 验证是否真的存在黑边问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from api.nano_banana import NanoBananaAPI

def create_full_frame_test_image():
    """创建一个填满整个画面的测试图片，便于检测黑边"""
    print("🎨 创建全画面测试图片...")
    
    # 创建1024x1024的图片
    img = Image.new('RGB', (1024, 1024))
    draw = ImageDraw.Draw(img)
    
    # 用渐变色填满整个画面，边缘使用鲜明的红色
    for y in range(1024):
        for x in range(1024):
            # 边缘10像素用红色标记
            if x < 10 or x > 1013 or y < 10 or y > 1013:
                color = (255, 0, 0)  # 红色边框
            else:
                # 内部用渐变蓝色
                blue_value = int((x + y) / 2048 * 255)
                color = (0, 0, blue_value)
            
            try:
                pixels = img.load()
                pixels[x, y] = color
            except:
                pass
    
    # 在中心绘制一个白色十字，用于验证图片中心位置
    center = 512
    cross_size = 100
    draw.line([(center - cross_size, center), (center + cross_size, center)], fill='white', width=5)
    draw.line([(center, center - cross_size), (center, center + cross_size)], fill='white', width=5)
    
    # 在四个角落绘制标记
    corner_size = 50
    corners = [
        (0, 0), (1024 - corner_size, 0),
        (0, 1024 - corner_size), (1024 - corner_size, 1024 - corner_size)
    ]
    
    for i, (x, y) in enumerate(corners):
        draw.rectangle([x, y, x + corner_size, y + corner_size], fill='yellow')
        draw.text((x + 25, y + 25), str(i+1), fill='black', anchor="mm")
    
    test_path = 'uploads/fullframe_test_1024x1024.png'
    os.makedirs('uploads', exist_ok=True)
    img.save(test_path)
    print(f"✅ 全画面测试图片创建: {test_path}")
    return test_path

def analyze_converted_image(image_path):
    """分析转换后的图片，检测是否有黑边"""
    print(f"\n🔍 分析转换后的图片: {os.path.basename(image_path)}")
    
    if not os.path.exists(image_path):
        print("❌ 文件不存在")
        return False
    
    img = Image.open(image_path)
    width, height = img.size
    pixels = img.load()
    
    print(f"📐 图片尺寸: {width}x{height}")
    print(f"📊 宽高比: {width/height:.10f}")
    
    # 检查四条边是否有黑边
    black_pixels_found = False
    
    # 检查上下边缘
    for y in [0, height-1]:
        for x in range(width):
            r, g, b = pixels[x, y][:3]
            if r == 0 and g == 0 and b == 0:
                print(f"⚠️ 发现黑色像素在位置 ({x}, {y})")
                black_pixels_found = True
                break
        if black_pixels_found:
            break
    
    # 检查左右边缘
    if not black_pixels_found:
        for x in [0, width-1]:
            for y in range(height):
                r, g, b = pixels[x, y][:3]
                if r == 0 and g == 0 and b == 0:
                    print(f"⚠️ 发现黑色像素在位置 ({x}, {y})")
                    black_pixels_found = True
                    break
            if black_pixels_found:
                break
    
    if black_pixels_found:
        print("❌ 检测到黑边！")
        return False
    else:
        print("✅ 未检测到黑边")
        return True

def test_video_preprocessing_quality():
    """测试视频预处理的质量"""
    print("🎬 视频预处理质量测试")
    print("="*50)
    
    # 创建测试图片
    test_image = create_full_frame_test_image()
    
    # 初始化API
    api = NanoBananaAPI()
    
    # 测试不同的填充模式
    modes = ['blur', 'black']
    results = {}
    
    for mode in modes:
        print(f"\n📐 测试模式: {mode}")
        print("-" * 30)
        
        # 转换图片
        converted_path = api.convert_image_for_video(test_image, '16:9', mode)
        
        if converted_path and os.path.exists(converted_path):
            # 分析结果
            no_black_edges = analyze_converted_image(converted_path)
            results[mode] = {
                'path': converted_path,
                'no_black_edges': no_black_edges
            }
            
            # 检查文件大小
            file_size = os.path.getsize(converted_path) / (1024 * 1024)
            print(f"📄 文件大小: {file_size:.2f} MB")
        else:
            print("❌ 转换失败")
            results[mode] = {'path': None, 'no_black_edges': False}
    
    # 总结结果
    print(f"\n{'='*50}")
    print("📊 测试结果总结")
    print("="*50)
    
    for mode, result in results.items():
        if result['path']:
            status = "✅ 无黑边" if result['no_black_edges'] else "❌ 有黑边"
            print(f"{mode:10} | {status} | {os.path.basename(result['path'])}")
        else:
            print(f"{mode:10} | ❌ 转换失败")
    
    # 推荐最佳模式
    best_modes = [mode for mode, result in results.items() if result['no_black_edges']]
    if best_modes:
        print(f"\n💡 推荐使用模式: {', '.join(best_modes)}")
        return True
    else:
        print(f"\n⚠️ 所有模式都检测到问题，需要进一步优化")
        return False

def check_actual_16_9_precision():
    """检查实际的16:9精度是否足够用于视频"""
    print(f"\n🎯 16:9精度视频兼容性检查")
    print("-" * 40)
    
    # 常见的视频分辨率和它们的实际比例
    video_resolutions = [
        (1280, 720),   # 720p
        (1920, 1080),  # 1080p  
        (2560, 1440),  # 1440p
        (3840, 2160),  # 4K
        (1366, 768),   # 常见笔记本
        (1600, 900),   # 16:9变体
    ]
    
    target_ratio = 16.0 / 9.0
    
    print("常见视频分辨率的实际比例误差:")
    print("分辨率        | 实际比例    | 误差")
    print("-" * 40)
    
    for width, height in video_resolutions:
        actual_ratio = width / height
        error = abs(actual_ratio - target_ratio)
        print(f"{width}x{height:4} | {actual_ratio:.8f} | {error:.10f}")
    
    # 我们的转换结果比较
    our_results = [
        (1820, 1024),  # 我们的1024高度基准
        (910, 512),    # 我们的512高度基准
        (1920, 1080),  # 标准1080p
    ]
    
    print(f"\n我们的转换结果:")
    print("尺寸          | 实际比例    | 误差")
    print("-" * 40)
    
    max_error = 0
    for width, height in our_results:
        actual_ratio = width / height
        error = abs(actual_ratio - target_ratio)
        max_error = max(max_error, error)
        print(f"{width}x{height:4} | {actual_ratio:.8f} | {error:.10f}")
    
    print(f"\n📊 我们的最大误差: {max_error:.10f}")
    
    # 判断是否在可接受范围内
    if max_error < 0.001:
        print("✅ 精度完全满足视频播放要求!")
        return True
    elif max_error < 0.01:
        print("✅ 精度满足大多数视频播放要求")
        return True
    else:
        print("⚠️ 精度可能需要进一步优化")
        return False

if __name__ == "__main__":
    print("🎬 视频黑边问题诊断工具\n")
    
    try:
        # 测试预处理质量
        quality_ok = test_video_preprocessing_quality()
        
        # 检查精度
        precision_ok = check_actual_16_9_precision()
        
        print(f"\n{'='*60}")
        print("🏁 最终诊断结果")
        print("="*60)
        
        if quality_ok and precision_ok:
            print("🎉 预处理功能工作正常，应该不会产生黑边")
            print("💡 如果仍有黑边，可能是视频播放器或编码问题")
        elif quality_ok:
            print("✅ 图片处理正常，但精度可能需要微调")
        elif precision_ok:
            print("✅ 数学精度足够，但图片处理可能有问题")
        else:
            print("⚠️ 检测到问题，需要进一步调试")
            
        print(f"\n📁 查看生成的测试图片以验证结果")
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()