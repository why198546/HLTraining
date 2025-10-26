#!/usr/bin/env python3
"""
快速验证16:9转换是否无黑边
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from api.nano_banana import NanoBananaAPI

def quick_no_blackbar_test():
    """快速测试确认无黑边"""
    print("⚡ 快速无黑边验证测试")
    print("="*40)
    
    # 创建一个明亮的测试图片（容易看出黑边）
    img = Image.new('RGB', (1024, 1024), color='white')
    draw = ImageDraw.Draw(img)
    
    # 用彩色格子填满整个画面
    colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
    grid_size = 128
    
    for i in range(0, 1024, grid_size):
        for j in range(0, 1024, grid_size):
            color_idx = ((i // grid_size) + (j // grid_size)) % len(colors)
            draw.rectangle([i, j, i + grid_size, j + grid_size], fill=colors[color_idx])
    
    # 在边缘画白框
    border_width = 5
    draw.rectangle([0, 0, 1024, border_width], fill='white')  # 上
    draw.rectangle([0, 1024-border_width, 1024, 1024], fill='white')  # 下
    draw.rectangle([0, 0, border_width, 1024], fill='white')  # 左
    draw.rectangle([1024-border_width, 0, 1024, 1024], fill='white')  # 右
    
    test_path = 'uploads/colorful_test_1024x1024.png'
    img.save(test_path)
    print(f"✅ 彩色测试图片: {test_path}")
    
    # 转换
    api = NanoBananaAPI()
    result_path = api.convert_image_for_video(test_path, '16:9', 'blur')
    
    if result_path and os.path.exists(result_path):
        result_img = Image.open(result_path)
        width, height = result_img.size
        ratio = width / height
        
        print(f"✅ 转换成功: {width}x{height}")
        print(f"📊 比例: {ratio:.8f}")
        
        # 检查边缘是否有黑色
        pixels = result_img.load()
        has_black_edge = False
        
        # 检查四个角落
        corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        for x, y in corners:
            r, g, b = pixels[x, y][:3]
            if r == 0 and g == 0 and b == 0:
                print(f"⚠️ 角落({x},{y})有黑色像素")
                has_black_edge = True
        
        # 检查边缘中点
        edges = [
            (width//2, 0),      # 上边缘中点
            (width//2, height-1), # 下边缘中点
            (0, height//2),     # 左边缘中点
            (width-1, height//2) # 右边缘中点
        ]
        
        for x, y in edges:
            r, g, b = pixels[x, y][:3]
            if r == 0 and g == 0 and b == 0:
                print(f"⚠️ 边缘({x},{y})有黑色像素")
                has_black_edge = True
        
        if has_black_edge:
            print("❌ 检测到黑边")
            return False
        else:
            print("🎉 确认无黑边！")
            return True
    else:
        print("❌ 转换失败")
        return False

if __name__ == "__main__":
    print("🎬 16:9无黑边快速验证\n")
    
    success = quick_no_blackbar_test()
    
    if success:
        print(f"\n✨ 结论：16:9预处理功能正常，无黑边问题")
        print(f"💡 建议：使用'模糊边缘'模式获得最佳效果")
        print(f"📝 如果视频仍有黑边，请检查：")
        print(f"   1. 是否选择了'黑边填充'模式")
        print(f"   2. 视频播放器的显示设置")
        print(f"   3. Veo API的视频编码设置")
    else:
        print(f"\n⚠️ 检测到问题，需要进一步调试")