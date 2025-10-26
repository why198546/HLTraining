#!/usr/bin/env python3
"""
16:9图片预处理专项测试

专门测试视频生成前的图片16:9转换功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from api.nano_banana import NanoBananaAPI

def create_sample_artwork():
    """创建一个示例艺术作品图片 (1024x1024)"""
    print("🎨 创建示例艺术作品...")
    
    img = Image.new('RGB', (1024, 1024), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # 绘制一个可爱的小房子
    # 房子主体
    draw.rectangle([312, 400, 712, 700], fill='#FFB6C1', outline='black', width=3)
    
    # 屋顶
    draw.polygon([(312, 400), (512, 250), (712, 400)], fill='#FF69B4')
    
    # 门
    draw.rectangle([460, 580, 540, 700], fill='#8B4513', outline='black', width=2)
    draw.circle((520, 640), 5, fill='gold')  # 门把手
    
    # 窗户
    draw.rectangle([350, 480, 420, 550], fill='#87CEEB', outline='black', width=2)
    draw.rectangle([580, 480, 650, 550], fill='#87CEEB', outline='black', width=2)
    
    # 窗框
    draw.line([(385, 480), (385, 550)], fill='black', width=1)
    draw.line([(350, 515), (420, 515)], fill='black', width=1)
    draw.line([(615, 480), (615, 550)], fill='black', width=1)
    draw.line([(580, 515), (650, 515)], fill='black', width=1)
    
    # 地面
    draw.rectangle([0, 700, 1024, 1024], fill='#90EE90')
    
    # 太阳
    draw.circle((150, 150), 60, fill='#FFD700', outline='#FFA500', width=3)
    
    # 云朵
    for x, y in [(300, 100), (700, 120), (850, 80)]:
        draw.ellipse([x, y, x+80, y+40], fill='white')
        draw.ellipse([x+20, y-10, x+60, y+30], fill='white')
    
    # 草地装饰
    for i in range(20):
        x = i * 50 + 25
        for j in range(3):
            y = 720 + j * 20
            draw.line([(x, y), (x, y+15)], fill='#006400', width=2)
    
    os.makedirs('uploads', exist_ok=True)
    artwork_path = 'uploads/sample_artwork_1024x1024.png'
    img.save(artwork_path)
    print(f"✅ 示例作品已创建: {artwork_path}")
    return artwork_path

def test_16_9_preprocessing():
    """测试16:9预处理功能"""
    print("\n" + "="*60)
    print("🎬 16:9视频预处理测试")
    print("="*60)
    
    # 创建示例图片
    original_image = create_sample_artwork()
    
    # 初始化API
    print("\n🔧 初始化API...")
    api = NanoBananaAPI()
    
    # 测试不同填充模式的16:9转换
    padding_modes = ['blur', 'black', 'ai']
    
    for mode in padding_modes:
        print(f"\n📐 测试模式: {mode}")
        print("-" * 40)
        
        try:
            # 执行16:9转换
            converted_path = api.convert_image_for_video(
                original_image,
                aspect_ratio='16:9',
                padding_mode=mode
            )
            
            if converted_path and os.path.exists(converted_path):
                # 验证结果
                img = Image.open(converted_path)
                width, height = img.size
                ratio = width / height
                target_ratio = 16/9
                
                print(f"✅ 转换成功")
                print(f"   📏 尺寸: {width}x{height}")
                print(f"   📊 比例: {ratio:.6f} (目标: {target_ratio:.6f})")
                print(f"   📂 文件: {os.path.basename(converted_path)}")
                
                # 检查比例精度
                error = abs(ratio - target_ratio)
                if error < 0.001:
                    print(f"   🎯 精度: 完美 (误差: {error:.8f})")
                elif error < 0.01:
                    print(f"   ✅ 精度: 良好 (误差: {error:.8f})")
                else:
                    print(f"   ⚠️ 精度: 需要改进 (误差: {error:.8f})")
                    
            else:
                print("❌ 转换失败")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print(f"\n{'='*60}")
    print("📊 总结")
    print(f"{'='*60}")
    
    # 显示生成的文件
    print("\n📁 生成的16:9图片:")
    files_found = 0
    for file in os.listdir('uploads'):
        if 'sample_artwork' in file and '16_9' in file:
            file_path = os.path.join('uploads', file)
            try:
                img = Image.open(file_path)
                w, h = img.size
                ratio = w/h
                size_kb = os.path.getsize(file_path) / 1024
                
                print(f"   📄 {file}")
                print(f"       • 尺寸: {w}x{h}")
                print(f"       • 比例: {ratio:.6f}")
                print(f"       • 大小: {size_kb:.1f} KB")
                files_found += 1
            except:
                pass
    
    if files_found > 0:
        print(f"\n🎉 成功生成 {files_found} 个16:9图片！")
        print("💡 这些图片可以直接用于视频生成，无黑边无变形")
    else:
        print("\n⚠️ 未找到生成的16:9图片")

def quick_test():
    """快速测试 - 只测试一种模式"""
    print("⚡ 快速16:9转换测试")
    print("-" * 30)
    
    # 创建简单测试图片
    img = Image.new('RGB', (512, 512), color='red')
    draw = ImageDraw.Draw(img)
    draw.rectangle([156, 156, 356, 356], fill='yellow')
    draw.text((230, 240), "TEST", fill='black')
    
    test_path = 'uploads/quick_test_512x512.png'
    img.save(test_path)
    
    # 转换
    api = NanoBananaAPI()
    result = api.convert_image_for_video(test_path, '16:9', 'blur')
    
    if result:
        result_img = Image.open(result)
        w, h = result_img.size
        ratio = w/h
        print(f"✅ 转换完成: {w}x{h}, 比例: {ratio:.4f}")
        return True
    else:
        print("❌ 转换失败")
        return False

if __name__ == "__main__":
    print("AI创意工坊 - 16:9预处理测试工具\n")
    
    try:
        # 选择测试模式
        print("请选择测试模式:")
        print("1. 完整测试 (测试所有填充模式)")
        print("2. 快速测试 (仅测试模糊填充)")
        
        choice = input("请输入选择 (1/2) [默认: 2]: ").strip() or "2"
        
        if choice == "1":
            test_16_9_preprocessing()
        else:
            if quick_test():
                print("\n🎯 16:9预处理功能正常!")
                print("📝 可以继续使用视频生成功能")
            else:
                print("\n❌ 预处理功能存在问题，请检查代码")
                
    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()