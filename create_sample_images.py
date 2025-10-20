#!/usr/bin/env python3
# 创建示例图片占位符

from PIL import Image, ImageDraw, ImageFont
import os

# 确保目录存在
os.makedirs('static/images/sample', exist_ok=True)

def create_placeholder(filename, text, color, size=(300, 300)):
    # 创建图像
    image = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # 获取文本边界框
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 计算文本位置（居中）
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # 绘制文本
    draw.text((x, y), text, fill='white', font=font)
    
    # 保存图像
    image.save(f'static/images/sample/{filename}')
    print(f'Created: static/images/sample/{filename}')

# 创建各种示例图片
samples = [
    # 小猫系列
    ('cat_sketch.png', '小猫简笔画', (200, 200, 200)),
    ('cat_colored.png', '可爱小猫', (255, 182, 193)),
    ('cat_figurine.png', '小猫手办', (255, 218, 185)),
    
    # 超级英雄系列
    ('superhero_sketch.png', '英雄简笔画', (200, 200, 200)),
    ('superhero_colored.png', '超级英雄', (70, 130, 180)),
    ('superhero_figurine.png', '英雄手办', (255, 140, 0)),
    
    # 花朵系列
    ('flower_sketch.png', '花朵简笔画', (200, 200, 200)),
    ('flower_colored.png', '美丽花朵', (255, 192, 203)),
    ('flower_figurine.png', '花朵手办', (144, 238, 144)),
    
    # 机器人系列
    ('robot_sketch.png', '机器人简笔画', (200, 200, 200)),
    ('robot_colored.png', '未来机器人', (123, 104, 238)),
    ('robot_figurine.png', '机器人手办', (169, 169, 169)),
]

for filename, text, color in samples:
    create_placeholder(filename, text, color)

print("所有示例图片已创建完成！")