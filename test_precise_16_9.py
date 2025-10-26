#!/usr/bin/env python3
"""
精确16:9比例测试 - 专门解决黑边问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from api.nano_banana import NanoBananaAPI

def test_exact_16_9_ratio():
    """测试精确的16:9比例，确保无黑边"""
    print("🎯 精确16:9比例测试 - 消除黑边")
    print("="*50)
    
    # 创建一个有明确中心主体的测试图片
    img = Image.new('RGB', (1024, 1024), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # 画一个马里奥风格的角色
    # 身体
    draw.ellipse([412, 500, 612, 650], fill='red')
    # 头部
    draw.ellipse([462, 350, 562, 450], fill='pink')
    # 帽子
    draw.ellipse([462, 330, 562, 380], fill='red')
    draw.text((490, 345), "M", fill='white', anchor="mm")
    
    # 眼睛
    draw.ellipse([485, 375, 495, 385], fill='black')
    draw.ellipse([525, 375, 535, 385], fill='black')
    
    # 鼻子
    draw.ellipse([507, 390, 517, 400], fill='black')
    
    # 胡子
    draw.ellipse([495, 405, 505, 415], fill='black')
    draw.ellipse([515, 405, 525, 415], fill='black')
    
    # 手臂
    draw.ellipse([375, 525, 425, 575], fill='pink')
    draw.ellipse([599, 525, 649, 575], fill='pink')
    
    # 腿
    draw.ellipse([450, 630, 500, 700], fill='blue')
    draw.ellipse([524, 630, 574, 700], fill='blue')
    
    # 鞋子
    draw.ellipse([440, 690, 510, 720], fill='brown')
    draw.ellipse([514, 690, 584, 720], fill='brown')
    
    # 地面
    draw.rectangle([0, 720, 1024, 1024], fill='green')
    
    # 背景云朵
    for x, y in [(150, 150), (800, 120), (300, 100)]:
        draw.ellipse([x, y, x+100, y+50], fill='white')
    
    test_path = 'uploads/mario_test_1024x1024.png'
    os.makedirs('uploads', exist_ok=True)
    img.save(test_path)
    print(f"✅ 测试图片创建: {test_path}")
    
    # 初始化API
    api = NanoBananaAPI()
    
    # 测试精确的16:9转换
    print(f"\n🔧 执行精确16:9转换...")
    result_path = api.convert_image_for_video(test_path, '16:9', 'blur')
    
    if result_path and os.path.exists(result_path):
        # 验证结果
        result_img = Image.open(result_path)
        width, height = result_img.size
        ratio = width / height
        target_ratio = 16.0 / 9.0
        error = abs(ratio - target_ratio)
        
        print(f"\n📊 转换结果分析:")
        print(f"   尺寸: {width}x{height}")
        print(f"   实际比例: {ratio:.10f}")
        print(f"   目标比例: {target_ratio:.10f}")
        print(f"   误差: {error:.12f}")
        
        # 判断精度
        if error < 0.000001:
            print(f"   🎯 精度: 完美! (误差 < 0.000001)")
        elif error < 0.00001:
            print(f"   ✅ 精度: 优秀! (误差 < 0.00001)")
        elif error < 0.0001:
            print(f"   ✅ 精度: 良好! (误差 < 0.0001)")
        elif error < 0.001:
            print(f"   ⚠️ 精度: 一般 (误差 < 0.001)")
        else:
            print(f"   ❌ 精度: 较差 (误差 >= 0.001)")
        
        # 检查是否为偶数尺寸（视频编码友好）
        if width % 2 == 0 and height % 2 == 0:
            print(f"   📹 视频兼容: ✅ 偶数尺寸")
        else:
            print(f"   📹 视频兼容: ⚠️ 非偶数尺寸")
        
        # 理论计算验证
        theoretical_width = int(height * target_ratio)
        if theoretical_width % 2 != 0:
            theoretical_width += 1
        theoretical_ratio = theoretical_width / height
        
        print(f"\n🧮 理论验证:")
        print(f"   理论最佳宽度: {theoretical_width}")
        print(f"   理论比例: {theoretical_ratio:.10f}")
        print(f"   与理论差异: {abs(ratio - theoretical_ratio):.12f}")
        
        return error < 0.00001  # 返回是否达到高精度
    else:
        print("❌ 转换失败")
        return False

def test_multiple_sizes():
    """测试多种尺寸的精确转换"""
    print(f"\n{'='*60}")
    print("🔄 多尺寸精确转换测试")
    print("="*60)
    
    test_sizes = [
        (512, 512),    # 小正方形
        (1024, 1024),  # 标准正方形
        (800, 600),    # 4:3
        (1920, 1080),  # 已经是16:9
        (1080, 1920),  # 竖直9:16
        (2048, 1024),  # 2:1超宽
    ]
    
    api = NanoBananaAPI()
    success_count = 0
    
    for width, height in test_sizes:
        print(f"\n📐 测试尺寸: {width}x{height}")
        
        # 创建测试图片
        img = Image.new('RGB', (width, height), color='lightcoral')
        draw = ImageDraw.Draw(img)
        
        # 在中心画一个十字标记
        center_x, center_y = width // 2, height // 2
        cross_size = min(width, height) // 8
        draw.line([(center_x - cross_size, center_y), (center_x + cross_size, center_y)], fill='black', width=5)
        draw.line([(center_x, center_y - cross_size), (center_x, center_y + cross_size)], fill='black', width=5)
        
        test_path = f'uploads/test_{width}x{height}.png'
        img.save(test_path)
        
        # 转换
        result_path = api.convert_image_for_video(test_path, '16:9', 'blur')
        
        if result_path and os.path.exists(result_path):
            result_img = Image.open(result_path)
            rw, rh = result_img.size
            ratio = rw / rh
            target_ratio = 16.0 / 9.0
            error = abs(ratio - target_ratio)
            
            status = "🎯" if error < 0.00001 else "✅" if error < 0.0001 else "⚠️"
            print(f"   {status} 结果: {rw}x{rh}, 比例: {ratio:.8f}, 误差: {error:.10f}")
            
            if error < 0.0001:
                success_count += 1
        else:
            print(f"   ❌ 转换失败")
    
    print(f"\n📊 总结: {success_count}/{len(test_sizes)} 个测试达到高精度")
    return success_count == len(test_sizes)

if __name__ == "__main__":
    print("🎬 无黑边16:9精确转换测试\n")
    
    try:
        # 精确比例测试
        precise_test_passed = test_exact_16_9_ratio()
        
        # 多尺寸测试
        multi_size_passed = test_multiple_sizes()
        
        print(f"\n{'='*60}")
        print("🏁 最终测试结果")
        print("="*60)
        
        if precise_test_passed and multi_size_passed:
            print("🎉 所有测试通过! 16:9转换精度达到视频级别要求")
            print("✨ 现在可以生成无黑边的完美视频了!")
        elif precise_test_passed:
            print("✅ 基础精度测试通过，但部分尺寸可能需要优化")
        else:
            print("⚠️ 精度测试未完全通过，建议检查算法")
            
        print(f"\n💡 提示: 查看 uploads/ 目录中的转换结果图片")
        
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()