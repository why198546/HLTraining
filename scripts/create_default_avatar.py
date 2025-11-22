"""
生成默认头像
创建一个简单的彩色圆形默认头像
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    """创建默认头像"""
    # 创建一个圆形头像，尺寸200x200
    size = 200
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变背景圆形
    for i in range(size // 2):
        # 从中心向外渐变
        progress = i / (size // 2)
        # 紫色到蓝色渐变
        r = int(102 + (118 - 102) * progress)
        g = int(126 + (75 - 126) * progress)
        b = int(234 + (162 - 234) * progress)
        
        draw.ellipse(
            [i, i, size - i, size - i],
            fill=(r, g, b)
        )
    
    # 绘制白色的人形图标
    # 头部圆形
    head_radius = size // 6
    head_center = (size // 2, size // 2 - size // 10)
    draw.ellipse(
        [head_center[0] - head_radius, head_center[1] - head_radius,
         head_center[0] + head_radius, head_center[1] + head_radius],
        fill='white'
    )
    
    # 身体部分（半圆）
    body_width = size // 3
    body_height = size // 4
    body_top = head_center[1] + head_radius - 5
    draw.ellipse(
        [size // 2 - body_width, body_top,
         size // 2 + body_width, body_top + body_height * 2],
        fill='white'
    )
    
    # 保存图片
    output_path = 'static/image/default_avatar.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f'✅ 默认头像已创建: {output_path}')

if __name__ == '__main__':
    create_default_avatar()
