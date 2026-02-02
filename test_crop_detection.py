#!/usr/bin/env python
"""测试边界检测算法的Python版本"""
import cv2
import numpy as np
from PIL import Image

def detect_paper_boundary(image_path):
    """
    使用暗像素检测纸张边界
    """
    # 加载图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法加载图片: {image_path}")
        return None
    
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    top_edge = 0
    bottom_edge = height
    left_edge = 0
    right_edge = width
    
    def get_brightness(gray_val):
        """返回灰度值（0-255）"""
        return gray_val
    
    # 从上往下找上边界
    for y in range(int(height * 0.7)):
        dark_count = 0
        for x in range(width):
            brightness = get_brightness(gray[y, x])
            if brightness < 100:  # 暗色像素
                dark_count += 1
        # 当暗色像素从多变少时，说明找到边界
        if y > 0 and dark_count < width * 0.3:
            top_edge = max(0, y - 10)
            break
    
    # 从下往上找下边界
    for y in range(height - 1, int(height * 0.3), -1):
        dark_count = 0
        for x in range(width):
            brightness = get_brightness(gray[y, x])
            if brightness < 100:
                dark_count += 1
        if dark_count < width * 0.3:
            bottom_edge = min(height, y + 10)
            break
    
    # 从左往右找左边界
    for x in range(int(width * 0.7)):
        dark_count = 0
        for y in range(top_edge, bottom_edge):
            brightness = get_brightness(gray[y, x])
            if brightness < 100:
                dark_count += 1
        if dark_count < (bottom_edge - top_edge) * 0.3:
            left_edge = max(0, x - 10)
            break
    
    # 从右往左找右边界
    for x in range(width - 1, int(width * 0.3), -1):
        dark_count = 0
        for y in range(top_edge, bottom_edge):
            brightness = get_brightness(gray[y, x])
            if brightness < 100:
                dark_count += 1
        if dark_count < (bottom_edge - top_edge) * 0.3:
            right_edge = min(width, x + 10)
            break
    
    return {
        'top': top_edge,
        'bottom': bottom_edge,
        'left': left_edge,
        'right': right_edge,
        'width': width,
        'height': height
    }

def draw_and_save_result(image_path, result, output_path):
    """
    在图片上绘制检测结果并保存
    """
    img = cv2.imread(image_path)
    if img is None:
        return False
    
    # 绘制矩形
    cv2.rectangle(img, 
                 (result['left'], result['top']),
                 (result['right'], result['bottom']),
                 (0, 165, 255), 3)  # Orange in BGR
    
    # 标记四个角
    corners = [
        (result['left'], result['top']),
        (result['right'], result['top']),
        (result['left'], result['bottom']),
        (result['right'], result['bottom'])
    ]
    
    for cx, cy in corners:
        cv2.circle(img, (cx, cy), 8, (0, 165, 255), -1)
        cv2.circle(img, (cx, cy), 8, (255, 255, 255), 2)
    
    # 保存
    cv2.imwrite(output_path, img)
    print(f"✅ 已保存结果到: {output_path}")
    return True

# 测试
if __name__ == '__main__':
    import os
    from pathlib import Path
    
    uploads_dir = '/Users/hongyuwang/code/HLTraining/uploads'
    
    # 查找JPG图片
    jpg_files = list(Path(uploads_dir).glob('*_camera*.jpg'))[:5]
    
    if not jpg_files:
        print("未找到测试图片")
    else:
        for jpg_file in jpg_files:
            print(f"\n🔍 测试: {jpg_file.name}")
            result = detect_paper_boundary(str(jpg_file))
            
            if result:
                print(f"  边界: 顶={result['top']}, 底={result['bottom']}, 左={result['left']}, 右={result['right']}")
                print(f"  检测框大小: {result['right']-result['left']} x {result['bottom']-result['top']}")
                print(f"  图片大小: {result['width']} x {result['height']}")
                
                # 绘制结果
                output_file = str(jpg_file).replace('.jpg', '_boundary_test.jpg')
                draw_and_save_result(str(jpg_file), result, output_file)
            else:
                print("  ❌ 检测失败")
