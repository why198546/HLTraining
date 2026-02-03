"""
图片打包下载功能
支持将当天课程生成的所有图片打包下载，区分普通图片和已打印图片
"""
import io
import os
import zipfile
from datetime import date, datetime
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_login import current_user, login_required
from auth.models import db
from auth.printed_image import PrintedImage
import requests
from urllib.parse import urlparse

download_bp = Blueprint('download', __name__)


@download_bp.route('/api/download/lesson-images', methods=['POST'])
@login_required
def download_lesson_images():
    """
    打包下载当天课程的所有图片
    请求参数：
    - lesson_key: 课程标识
    - images: 图片URL列表
    """
    try:
        data = request.json
        lesson_key = data.get('lesson_key')
        images = data.get('images', [])
        
        if not lesson_key:
            return jsonify({'success': False, 'error': '缺少课程标识'}), 400
        
        if not images or len(images) == 0:
            return jsonify({'success': False, 'error': '没有可下载的图片'}), 400
        
        current_app.logger.info(f'用户 {current_user.username} 请求下载 {lesson_key} 的 {len(images)} 张图片')
        
        # 获取当天打印过的图片列表
        today = date.today()
        printed_images = PrintedImage.get_printed_images(
            current_user.id, 
            lesson_key, 
            today
        )
        printed_urls = {img.image_url for img in printed_images}
        
        current_app.logger.info(f'当天打印过的图片数量: {len(printed_urls)}')
        
        # 创建内存中的ZIP文件
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 统计信息
            normal_count = 0
            selected_count = 0
            failed_count = 0
            
            for idx, image_url in enumerate(images, 1):
                try:
                    # 判断是否为已打印图片
                    is_printed = image_url in printed_urls
                    folder = 'selected' if is_printed else 'images'
                    
                    # 下载图片
                    image_data = download_image(image_url)
                    if not image_data:
                        current_app.logger.warning(f'图片下载失败: {image_url}')
                        failed_count += 1
                        continue
                    
                    # 生成文件名
                    ext = get_file_extension(image_url)
                    if is_printed:
                        filename = f'{folder}/{lesson_key}_selected_{idx:03d}{ext}'
                        selected_count += 1
                    else:
                        filename = f'{folder}/{lesson_key}_{idx:03d}{ext}'
                        normal_count += 1
                    
                    # 添加到ZIP
                    zf.writestr(filename, image_data)
                    
                except Exception as e:
                    current_app.logger.error(f'处理图片时出错 {image_url}: {str(e)}')
                    failed_count += 1
            
            # 添加README说明文件
            readme_content = f"""课程图片打包说明
============================

课程：{lesson_key}
下载日期：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
用户：{current_user.nickname} (@{current_user.username})

图片统计：
- 普通图片：{normal_count} 张 (位于 images/ 文件夹)
- 已打印图片：{selected_count} 张 (位于 selected/ 文件夹)
- 下载失败：{failed_count} 张

说明：
- selected文件夹中的图片是您今天标记为已打印的图片
- images文件夹中是其他普通生成的图片
- 所有图片均按生成顺序编号

祝学习愉快！
松果AI培训系统
"""
            zf.writestr('README.txt', readme_content.encode('utf-8'))
        
        # 重置文件指针
        memory_file.seek(0)
        
        # 生成文件名
        filename = f'{lesson_key}_{today.strftime("%Y%m%d")}_{current_user.username}.zip'
        
        current_app.logger.info(f'ZIP文件生成成功: {filename}, 普通:{normal_count}, 已打印:{selected_count}, 失败:{failed_count}')
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f'打包下载失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': f'打包失败: {str(e)}'}), 500


@download_bp.route('/api/download/mark-printed', methods=['POST'])
@login_required
def mark_image_as_printed():
    """
    标记图片为已打印
    请求参数：
    - lesson_key: 课程标识
    - image_url: 图片URL
    """
    try:
        data = request.json
        lesson_key = data.get('lesson_key')
        image_url = data.get('image_url')
        
        if not lesson_key or not image_url:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 标记为已打印
        is_new = PrintedImage.mark_as_printed(
            current_user.id,
            lesson_key,
            image_url
        )
        
        if is_new:
            current_app.logger.info(f'用户 {current_user.username} 打印图片: {image_url[:100]}')
        
        return jsonify({
            'success': True,
            'is_new': is_new,
            'message': '已标记为打印' if is_new else '该图片已标记过'
        })
        
    except Exception as e:
        current_app.logger.error(f'标记打印失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@download_bp.route('/api/download/get-printed-status', methods=['POST'])
@login_required
def get_printed_status():
    """
    批量获取图片的打印状态
    请求参数：
    - lesson_key: 课程标识
    - image_urls: 图片URL列表
    """
    try:
        data = request.json
        lesson_key = data.get('lesson_key')
        image_urls = data.get('image_urls', [])
        
        if not lesson_key:
            return jsonify({'success': False, 'error': '缺少课程标识'}), 400
        
        # 获取所有打印记录
        today = date.today()
        printed_images = PrintedImage.get_printed_images(
            current_user.id,
            lesson_key,
            today
        )
        printed_urls = {img.image_url for img in printed_images}
        
        # 构建状态映射
        status_map = {url: (url in printed_urls) for url in image_urls}
        
        return jsonify({
            'success': True,
            'status': status_map,
            'printed_count': len(printed_urls)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取打印状态失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def download_image(url):
    """下载图片并返回二进制数据"""
    try:
        # 处理本地文件路径
        if url.startswith('/uploads/') or url.startswith('/static/'):
            # 本地文件
            if url.startswith('/'):
                url = url[1:]  # 移除开头的/
            
            file_path = os.path.join(current_app.root_path, '..', url)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            else:
                current_app.logger.warning(f'本地文件不存在: {file_path}')
                return None
        
        # 处理HTTP/HTTPS URL
        elif url.startswith('http://') or url.startswith('https://'):
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                current_app.logger.warning(f'HTTP请求失败: {url}, 状态码: {response.status_code}')
                return None
        
        else:
            current_app.logger.warning(f'不支持的URL格式: {url}')
            return None
            
    except Exception as e:
        current_app.logger.error(f'下载图片失败 {url}: {str(e)}')
        return None


def get_file_extension(url):
    """从URL中提取文件扩展名"""
    parsed = urlparse(url)
    path = parsed.path
    
    # 获取扩展名
    _, ext = os.path.splitext(path)
    
    # 如果没有扩展名，默认使用.png
    if not ext:
        ext = '.png'
    
    return ext
