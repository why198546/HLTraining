#!/usr/bin/env python3
"""
视频生成图片预处理测试脚本

测试图片从1:1到16:9的转换流程，确保视频生成使用正确的预处理图片
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from api.nano_banana import NanoBananaAPI

def create_test_square_image():
    """创建一个测试用的1024x1024正方形图片"""
    print("🎨 创建测试用的正方形图片...")
    
    # 创建一个具有明显中心主体的测试图片
    img = Image.new('RGB', (1024, 1024), color='skyblue')
    
    # 在中心绘制一个明显的主体
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # 绘制一个城堡
    # 主体建筑
    draw.rectangle([412, 400, 612, 624], fill='gray', outline='black', width=3)
    
    # 塔楼
    draw.rectangle([350, 300, 400, 500], fill='darkgray', outline='black', width=2)
    draw.rectangle([624, 300, 674, 500], fill='darkgray', outline='black', width=2)
    
    # 屋顶
    draw.polygon([(350, 300), (375, 250), (400, 300)], fill='red')
    draw.polygon([(624, 300), (649, 250), (674, 300)], fill='red')
    draw.polygon([(412, 400), (512, 350), (612, 400)], fill='red')
    
    # 门
    draw.rectangle([485, 550, 535, 624], fill='brown', outline='black', width=2)
    
    # 窗户
    draw.rectangle([430, 450, 460, 480], fill='yellow', outline='black', width=1)
    draw.rectangle([564, 450, 594, 480], fill='yellow', outline='black', width=1)
    
    # 地面
    draw.rectangle([0, 624, 1024, 1024], fill='green')
    
    # 添加一些云朵作为背景元素
    draw.ellipse([100, 100, 200, 150], fill='white')
    draw.ellipse([180, 80, 280, 130], fill='white')
    draw.ellipse([800, 120, 900, 170], fill='white')
    
    # 太阳
    draw.ellipse([50, 50, 120, 120], fill='yellow', outline='orange', width=3)
    
    test_path = 'uploads/test_castle_1024x1024.png'
    os.makedirs('uploads', exist_ok=True)
    img.save(test_path)
    print(f"✅ 测试图片已创建: {test_path}")
    return test_path

def test_video_preprocessing():
    """测试视频生成的图片预处理流程"""
    print("\n" + "="*70)
    print("🧪 开始测试视频生成的图片预处理流程")
    print("="*70)
    
    # 创建测试图片
    test_image = create_test_square_image()
    
    # 初始化API
    print("\n🔧 初始化Nano Banana API...")
    api = NanoBananaAPI()
    
    # 测试不同的填充模式
    padding_modes = ['ai', 'blur', 'black']
    
    for padding_mode in padding_modes:
        print(f"\n{'='*50}")
        print(f"🎬 测试填充模式: {padding_mode}")
        print(f"{'='*50}")
        
        try:
            # 测试16:9转换
            print(f"\n📐 测试 16:9 转换 (填充模式: {padding_mode})")
            result_path = api.convert_image_for_video(
                test_image, 
                aspect_ratio='16:9', 
                padding_mode=padding_mode
            )
            
            if result_path and os.path.exists(result_path):
                # 验证结果
                result_img = Image.open(result_path)
                width, height = result_img.size
                ratio = width / height
                expected_ratio = 16 / 9
                
                print(f"✅ 转换成功!")
                print(f"   输出文件: {os.path.basename(result_path)}")
                print(f"   输出尺寸: {width}x{height}")
                print(f"   宽高比: {ratio:.6f}")
                print(f"   预期比例: {expected_ratio:.6f}")
                print(f"   误差: {abs(ratio - expected_ratio):.8f}")
                
                # 检查比例精度
                if abs(ratio - expected_ratio) < 0.001:
                    print(f"   🎯 比例完美匹配!")
                elif abs(ratio - expected_ratio) < 0.01:
                    print(f"   ✅ 比例良好 (误差在可接受范围)")
                else:
                    print(f"   ⚠️ 比例误差较大!")
                    
                # 计算文件大小
                file_size = os.path.getsize(result_path) / (1024 * 1024)
                print(f"   文件大小: {file_size:.2f} MB")
                
            else:
                print(f"❌ 转换失败: 无法生成输出文件")
                
        except Exception as e:
            print(f"❌ 测试出错: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("📊 测试结果总结")
    print(f"{'='*70}")
    
    # 列出生成的所有文件
    print("\n📁 生成的文件列表:")
    for file in os.listdir('uploads'):
        if file.startswith('test_castle') and '16_9' in file:
            file_path = os.path.join('uploads', file)
            if os.path.exists(file_path):
                try:
                    img = Image.open(file_path)
                    w, h = img.size
                    ratio = w / h
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    print(f"   📄 {file}")
                    print(f"       尺寸: {w}x{h}, 比例: {ratio:.6f}, 大小: {size_mb:.2f}MB")
                except:
                    print(f"   ❌ {file} (无法读取)")
    
    print(f"\n🎉 测试完成!")
    print(f"💡 建议: 使用 'ai' 模式获得最佳视频生成效果")

def test_aspect_ratio_precision():
    """测试宽高比精度"""
    print(f"\n{'='*50}")
    print("🎯 宽高比精度测试")
    print(f"{'='*50}")
    
    # 测试不同尺寸下的比例精度
    test_cases = [
        (1024, 1024),    # 标准正方形
        (800, 600),      # 4:3
        (1920, 1080),    # 16:9 (已经符合)
        (1080, 1920),    # 9:16
        (512, 768),      # 2:3
    ]
    
    api = NanoBananaAPI()
    
    for width, height in test_cases:
        print(f"\n📐 测试尺寸: {width}x{height} (比例: {width/height:.4f})")
        
        # 创建测试图片
        img = Image.new('RGB', (width, height), color='lightblue')
        test_path = f'uploads/test_{width}x{height}.png'
        img.save(test_path)
        
        try:
            # 转换为16:9
            result_path = api.convert_image_for_video(test_path, '16:9', 'ai')
            
            if result_path and os.path.exists(result_path):
                result_img = Image.open(result_path)
                rw, rh = result_img.size
                ratio = rw / rh
                expected = 16/9
                error = abs(ratio - expected)
                
                status = "🎯" if error < 0.001 else "✅" if error < 0.01 else "⚠️"
                print(f"   {status} 结果: {rw}x{rh}, 比例: {ratio:.6f}, 误差: {error:.8f}")
            else:
                print(f"   ❌ 转换失败")
                
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")

if __name__ == "__main__":
    try:
        test_video_preprocessing()
        test_aspect_ratio_precision()
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()