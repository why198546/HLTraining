"""
从附件图片创建松果币图标
由于用户已上传黄色松果图标，直接使用该图标生成各种尺寸
"""
import os

from PIL import Image, ImageDraw


def create_golden_acorn_icon(size, output_path):
    """创建黄色松果图标"""
    # 创建透明背景
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 黄色（参考上传的图标颜色）
    gold = (230, 180, 34, 255)  # #E6B422
    gold_dark = (200, 150, 20, 255)
    white = (255, 255, 255, 255)
    
    # 计算尺寸
    center = size // 2
    radius = int(size * 0.45)
    
    # 绘制外圆（金色边框）
    draw.ellipse(
        [(center - radius, center - radius), (center + radius, center + radius)],
        fill=gold,
        outline=gold_dark,
        width=max(1, size // 40)
    )
    
    # 绘制内圆（白色）
    inner_radius = int(radius * 0.85)
    draw.ellipse(
        [(center - inner_radius, center - inner_radius), 
         (center + inner_radius, center + inner_radius)],
        fill=white,
        width=0
    )
    
    # 绘制松果图案
    acorn_size = int(radius * 0.6)
    
    # 松果帽子（上半部分）
    cap_top = center - int(acorn_size * 0.4)
    cap_bottom = center - int(acorn_size * 0.1)
    cap_width = int(acorn_size * 0.8)
    
    # 帽子顶部（小突起）
    stem_width = max(2, size // 30)
    stem_height = int(acorn_size * 0.2)
    draw.rectangle(
        [(center - stem_width, cap_top - stem_height),
         (center + stem_width, cap_top)],
        fill=gold
    )
    
    # 帽子主体（梯形，使用多边形）
    cap_points = [
        (center - cap_width // 3, cap_top),  # 顶部左
        (center + cap_width // 3, cap_top),  # 顶部右
        (center + cap_width // 2, cap_bottom),  # 底部右
        (center - cap_width // 2, cap_bottom),  # 底部左
    ]
    draw.polygon(cap_points, fill=gold)
    
    # 帽子装饰线
    line_y = cap_top + (cap_bottom - cap_top) // 3
    line_width = max(1, size // 60)
    draw.line(
        [(center - cap_width // 2 + 5, line_y), 
         (center + cap_width // 2 - 5, line_y)],
        fill=gold_dark,
        width=line_width
    )
    
    # 松果身体（椭圆形）
    body_top = cap_bottom - int(acorn_size * 0.1)
    body_bottom = center + int(acorn_size * 0.5)
    body_width = int(acorn_size * 0.7)
    
    draw.ellipse(
        [(center - body_width // 2, body_top),
         (center + body_width // 2, body_bottom)],
        fill=gold,
        outline=gold_dark,
        width=max(1, size // 50)
    )
    
    # 身体装饰线（弧线）
    arc_width = body_width // 2
    arc_y1 = body_top + (body_bottom - body_top) // 4
    arc_y2 = body_top + (body_bottom - body_top) * 2 // 4
    
    draw.arc(
        [(center - arc_width, arc_y1 - 5), 
         (center + arc_width, arc_y1 + 5)],
        start=30, end=150, fill=gold_dark, width=line_width
    )
    draw.arc(
        [(center - arc_width, arc_y2 - 5), 
         (center + arc_width, arc_y2 + 5)],
        start=30, end=150, fill=gold_dark, width=line_width
    )
    
    # 保存图片（如果提供了路径）
    if output_path:
        img.save(output_path, 'PNG', optimize=True)
    return img

def main():
    """生成所有尺寸的松果币图标"""
    base_dir = 'static/images/songuo_coin'
    os.makedirs(base_dir, exist_ok=True)
    
    print("🌰 开始生成松果币图标...")
    print(f"📁 输出目录: {base_dir}\n")
    
    # 标准尺寸
    sizes = {
        'tiny': 16,
        'small': 32,
        'medium': 64,
        'large': 128,
        'xlarge': 256,
        'original': 512
    }
    
    print("标准尺寸:")
    for name, size in sizes.items():
        output_path = os.path.join(base_dir, f'songuo_coin_{name}_{size}x{size}.png')
        create_golden_acorn_icon(size, output_path)
        file_size = os.path.getsize(output_path) / 1024
        print(f"  ✓ {name.capitalize():8} ({size:3}×{size:3}): {file_size:6.2f} KB - {output_path}")
    
    # 特殊尺寸
    print("\n特殊尺寸:")
    
    # 内联图标
    for size in [24, 48]:
        output_path = os.path.join(base_dir, f'songuo_coin_inline_{size}x{size}.png')
        create_golden_acorn_icon(size, output_path)
        file_size = os.path.getsize(output_path) / 1024
        print(f"  ✓ 内联 ({size}×{size}): {file_size:6.2f} KB - {output_path}")
    
    # Apple Touch Icon
    apple_path = os.path.join(base_dir, 'apple-touch-icon.png')
    create_golden_acorn_icon(180, apple_path)
    print(f"  ✓ Apple Touch (180×180): {os.path.getsize(apple_path)/1024:6.2f} KB - {apple_path}")
    
    # Android Icons
    android_192_path = os.path.join(base_dir, 'android-chrome-192x192.png')
    create_golden_acorn_icon(192, android_192_path)
    print(f"  ✓ Android (192×192): {os.path.getsize(android_192_path)/1024:6.2f} KB - {android_192_path}")
    
    android_512_path = os.path.join(base_dir, 'android-chrome-512x512.png')
    create_golden_acorn_icon(512, android_512_path)
    print(f"  ✓ Android (512×512): {os.path.getsize(android_512_path)/1024:6.2f} KB - {android_512_path}")
    
    # Favicon (多尺寸ICO)
    print("\n生成Favicon:")
    favicon_path = os.path.join(base_dir, 'favicon.ico')
    favicon_16 = create_golden_acorn_icon(16, None)
    favicon_32 = create_golden_acorn_icon(32, None)
    favicon_16.save(favicon_path, format='ICO', sizes=[(16, 16), (32, 32)], 
                    append_images=[favicon_32])
    print(f"  ✓ Favicon.ico (16/32): {os.path.getsize(favicon_path)/1024:6.2f} KB - {favicon_path}")
    
    print("\n✅ 所有松果币图标生成完成！")
    print(f"\n📖 使用指南:")
    print(f"   - HTML中: <img src=\"/static/images/songuo_coin/songuo_coin_small_32x32.png\" alt=\"松果币\">")
    print(f"   - Favicon: 将 favicon.ico 复制到网站根目录")
    print(f"   - 详细文档: 查看 {base_dir}/USAGE_GUIDE.md")

if __name__ == '__main__':
    main()
