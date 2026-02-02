#!/usr/bin/env python
"""测试改进的边界检测算法（Sobel边缘检测）"""
import cv2
import numpy as np

def detect_paper_boundary_improved(image_path):
    """
    使用Sobel边缘检测来找纸张边界
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Sobel边缘检测
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.sqrt(sobelx**2 + sobely**2).astype(np.uint8)
    
    edge_threshold = 50
    top_edge = 0
    bottom_edge = height
    left_edge = 0
    right_edge = width
    
    # 从上往下找上边界
    for y in range(int(height * 0.7)):
        edge_count = np.sum(edges[y] > edge_threshold)
        if edge_count > width * 0.2:
            top_edge = max(0, y - 10)
            break
    
    # 从下往上找下边界
    for y in range(height - 1, int(height * 0.3), -1):
        edge_count = np.sum(edges[y] > edge_threshold)
        if edge_count > width * 0.2:
            bottom_edge = min(height, y + 10)
            break
    
    # 从左往右找左边界
    for x in range(int(width * 0.7)):
        edge_count = np.sum(edges[top_edge:bottom_edge, x] > edge_threshold)
        if edge_count > (bottom_edge - top_edge) * 0.2:
            left_edge = max(0, x - 10)
            break
    
    # 从右往左找右边界
    for x in range(width - 1, int(width * 0.3), -1):
        edge_count = np.sum(edges[top_edge:bottom_edge, x] > edge_threshold)
        if edge_count > (bottom_edge - top_edge) * 0.2:
            right_edge = min(width, x + 10)
            break
    
    # 检测失败时返回完整图片
    if right_edge - left_edge < width * 0.2 or bottom_edge - top_edge < height * 0.2:
        return {'top': 0, 'bottom': height, 'left': 0, 'right': width}
    
    return {
        'top': top_edge,
        'bottom': bottom_edge,
        'left': left_edge,
        'right': right_edge,
        'width': width,
        'height': height
    }

# 测试
if __name__ == '__main__':
    from pathlib import Path
    import os
    
    img_path = '/Users/hongyuwang/code/HLTraining/uploads/569b5a4e-d6b4-4a99-963d-7fb1334b1d78_camera-photo.jpg'
    
    result = detect_paper_boundary_improved(img_path)
    if result:
        print(f'🔍 检测结果:')
        print(f'  边界: 顶={result["top"]}, 底={result["bottom"]}, 左={result["left"]}, 右={result["right"]}')
        print(f'  检测框大小: {result["right"]-result["left"]} x {result["bottom"]-result["top"]}')
        print(f'  图片大小: {result["width"]} x {result["height"]}')
        print(f'  覆盖率: {100*(result["right"]-result["left"])/(result["width"]):.1f}% x {100*(result["bottom"]-result["top"])/(result["height"]):.1f}%')
        
        # 可视化
        img = cv2.imread(img_path)
        cv2.rectangle(img, (result['left'], result['top']), (result['right'], result['bottom']), (0, 165, 255), 3)
        cv2.imwrite('/tmp/boundary_test.jpg', img)
        print(f'  已保存结果到: /tmp/boundary_test.jpg')
