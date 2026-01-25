"""图片裁剪API"""
from flask import Blueprint, request, jsonify
from PIL import Image
import numpy as np
import cv2
import os
from pathlib import Path

crop_api_bp = Blueprint('crop_api', __name__)

@crop_api_bp.route('/api/crop_image', methods=['POST'])
def crop_image():
    """使用透视变换裁剪图片"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        image_src = data.get('image_src', '')
        crop_data = data.get('crop_data', {})
        
        if not image_src or not crop_data:
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 从image_src中提取文件路径
        if image_src.startswith('data:image'):
            # Base64图片
            return jsonify({'success': False, 'error': '暂不支持Base64图片裁剪'})
        
        # 从URL中提取文件路径
        # /uploads/xxxx.jpg
        if '/uploads/' in image_src:
            filename = image_src.split('/uploads/')[-1].split('?')[0]
            image_path = os.path.join('uploads', filename)
        else:
            return jsonify({'success': False, 'error': '无效的图片路径'})
        
        if not os.path.exists(image_path):
            return jsonify({'success': False, 'error': f'图片文件不存在: {image_path}'})
        
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return jsonify({'success': False, 'error': '无法读取图片'})
        
        # 获取四个角点
        corners = crop_data.get('corners', [])
        if len(corners) != 4:
            return jsonify({'success': False, 'error': '需要4个角点'})
        
        # 按id排序：tl, tr, br, bl
        corner_dict = {c['id']: (c['x'], c['y']) for c in corners}
        src_points = np.float32([
            corner_dict['tl'],  # 左上
            corner_dict['tr'],  # 右上
            corner_dict['br'],  # 右下
            corner_dict['bl']   # 左下
        ])
        
        # 计算目标矩形的宽度和高度
        # 使用上边和下边的平均宽度，左边和右边的平均高度
        width_top = np.linalg.norm(src_points[1] - src_points[0])
        width_bottom = np.linalg.norm(src_points[2] - src_points[3])
        width = int((width_top + width_bottom) / 2)
        
        height_left = np.linalg.norm(src_points[3] - src_points[0])
        height_right = np.linalg.norm(src_points[2] - src_points[1])
        height = int((height_left + height_right) / 2)
        
        # 定义目标矩形的四个角点
        dst_points = np.float32([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ])
        
        # 计算透视变换矩阵
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # 应用透视变换
        result = cv2.warpPerspective(img, matrix, (width, height))
        
        # 保存裁剪后的图片
        base_name = Path(image_path).stem
        ext = Path(image_path).suffix
        cropped_filename = f"{base_name}_cropped{ext}"
        cropped_path = os.path.join('uploads', cropped_filename)
        
        cv2.imwrite(cropped_path, result)
        
        # 返回裁剪后的图片URL
        cropped_url = f'/uploads/{cropped_filename}'
        
        return jsonify({
            'success': True,
            'cropped_image_url': cropped_url,
            'width': width,
            'height': height
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})
