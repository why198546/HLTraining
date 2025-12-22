"""工具类API路由 - 提示词处理、图片获取等"""
import json
import os
import re
from datetime import datetime
from io import BytesIO

import google.generativeai as genai
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from PIL import Image

from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_prompt

utils_api_bp = Blueprint('utils_api', __name__)


@utils_api_bp.route('/get-image-info', methods=['POST'])
def get_image_info():
    """获取图片信息和推荐框选区域"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        use_expanded = data.get('use_expanded', False)  # 是否使用扩展图片模式
        
        if not image_path:
            return jsonify({'success': False, 'error': '缺少图片路径'}), 400
        
        # 转换路径
        if image_path.startswith('/uploads/'):
            image_path = 'uploads' + image_path[8:]
        elif image_path.startswith('uploads/'):
            pass
        else:
            image_path = os.path.join('uploads', image_path)
        
        print(f"📐 获取图片信息: {image_path} (扩展模式: {use_expanded})")
        
        # 获取图片信息
        nano_banana = NanoBananaAPI()
        info = nano_banana.get_image_info(image_path, use_expanded=use_expanded)
        
        if info['success']:
            print(f"✅ 图片信息获取成功: {info['width']}x{info['height']}")
            return jsonify(info)
        else:
            return jsonify({'success': False, 'error': info['error']}), 500
            
    except Exception as e:
        print(f"❌ 获取图片信息失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@utils_api_bp.route('/fetch-image', methods=['POST'])
@login_required
def fetch_image_from_url():
    """从URL获取图片并保存到本地"""
    try:
        data = request.get_json()
        image_url = data.get('url', '').strip()
        
        if not image_url:
            return jsonify({'success': False, 'error': '图片链接不能为空'}), 400
        
        print(f"🔗 正在获取图片: {image_url}")
        
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 下载图片
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 检查是否是图片
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return jsonify({'success': False, 'error': '链接不是有效的图片'}), 400
        
        # 读取图片数据
        image_data = BytesIO(response.content)
        img = Image.open(image_data)
        
        # 转换为RGB（如果需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # 生成唯一文件名
        filename = f"url_image_{int(datetime.now().timestamp())}.png"
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = os.path.join(upload_folder, filename)
        
        # 确保目录存在
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存图片
        img.save(filepath, 'PNG')
        
        print(f"✅ 图片已保存: {filepath}")
        
        return jsonify({
            'success': True,
            'image_url': f'/uploads/{filename}',
            'filename': filename
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': '图片下载超时，请重试'}), 400
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载图片失败: {str(e)}")
        return jsonify({'success': False, 'error': '无法访问该图片链接'}), 400
    except Exception as e:
        print(f"❌ 处理图片失败: {str(e)}")
        return jsonify({'success': False, 'error': f'图片处理失败: {str(e)}'}), 500


@utils_api_bp.route('/translate-prompt', methods=['POST'])
def translate_prompt_api():
    """翻译prompt并返回预览信息"""
    try:
        data = request.get_json()
        original_prompt = data.get('prompt', '').strip()
        
        if not original_prompt:
            return jsonify({'success': False, 'error': '提示词不能为空'}), 400
        
        print(f"🌐 翻译prompt: {original_prompt}")
        
        # 翻译prompt
        translated_prompt = translate_prompt(original_prompt)
        
        print(f"✅ 翻译完成: {translated_prompt}")
        
        # 添加详细的对话检查日志
        if "saying in Chinese:" in translated_prompt:
            print("🗣️ 检测到对话保护：找到 'saying in Chinese:' 标记")
            # 提取并检查对话内容
            chinese_content = re.search(r'saying in Chinese:\s*["""\'\'](.*?)["""\'\'"]', translated_prompt)
            if chinese_content:
                dialogue_text = chinese_content.group(1)
                print(f"🔍 保护的对话内容: '{dialogue_text}'")
                # 检查是否包含中文
                if re.search(r'[\u4e00-\u9fff]', dialogue_text):
                    print("✅ 对话内容确实保持中文")
                else:
                    print("❌ 对话内容没有中文")
            else:
                print("⚠️ 没有找到对话内容")
        else:
            print("❌ 没有检测到对话保护标记")
        
        return jsonify({
            'success': True,
            'original_prompt': original_prompt,
            'translated_prompt': translated_prompt
        })
        
    except Exception as e:
        print(f"❌ prompt翻译失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@utils_api_bp.route('/organize-prompt', methods=['POST'])
def organize_prompt_api():
    """使用AI整理语音输入的内容成为清晰的prompt"""
    try:
        data = request.get_json()
        voice_input = data.get('voice_input', '').strip()
        
        if not voice_input:
            return jsonify({'success': False, 'error': '语音内容为空'}), 400
        
        print(f"🎤 收到语音输入: {voice_input}")
        
        # 配置Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API密钥未配置'}), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 构建整理指令
        system_prompt = """你是一个创意助手，专门帮助儿童将他们的创意想法整理成清晰的画面描述。

请根据孩子的语音输入，整理成一个清晰、生动的画面描述。要求：
1. 保持孩子的原创想法和创意
2. 补充必要的画面细节（颜色、动作、环境等）
3. 使用儿童友好的语言
4. 长度控制在50-100字
5. 如果输入包含对话内容，请保持对话的中文原文

示例：
输入："我想画一只猫，它在彩虹上面"
输出："一只可爱的小猫咪，戴着红色的帽子，坐在七彩的彩虹上，彩虹的颜色非常鲜艳，小猫开心地笑着"

现在请整理以下内容："""
        
        # 调用AI整理
        full_prompt = f"{system_prompt}\n\n用户语音：{voice_input}"
        response = model.generate_content(full_prompt)
        organized_prompt = response.text.strip()
        
        print(f"✨ AI整理后: {organized_prompt}")
        
        return jsonify({
            'success': True,
            'original_input': voice_input,
            'organized_prompt': organized_prompt
        })
        
    except Exception as e:
        print(f"❌ AI整理失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@utils_api_bp.route('/convert-to-mp4', methods=['POST'])
def convert_to_mp4():
    """将WebM视频转换为MP4格式"""
    import subprocess
    import tempfile
    from pathlib import Path
    
    try:
        # 获取上传的视频文件
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': '没有上传视频文件'}), 400
        
        video_file = request.files['video']
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
            webm_path = webm_file.name
            video_file.save(webm_path)
        
        # 创建输出MP4文件路径
        mp4_path = webm_path.replace('.webm', '.mp4')
        
        # 使用ffmpeg转换
        # -y: 覆盖输出文件
        # -i: 输入文件
        # -c:v libx264: 使用H.264编码器
        # -preset fast: 快速编码
        # -crf 23: 质量参数（18-28，越小质量越好）
        # -c:a aac: 音频编码器（虽然canvas录制没有音频，但保持兼容性）
        cmd = [
            'ffmpeg',
            '-y',
            '-i', webm_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',  # 兼容性更好
            '-movflags', '+faststart',  # 优化网络播放
            mp4_path
        ]
        
        # 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"FFmpeg错误: {result.stderr}")
            return jsonify({'success': False, 'error': '视频转换失败'}), 500
        
        # 读取MP4文件
        with open(mp4_path, 'rb') as f:
            mp4_data = f.read()
        
        # 清理临时文件
        try:
            os.unlink(webm_path)
            os.unlink(mp4_path)
        except:
            pass
        
        # 返回MP4文件
        from flask import send_file
        return send_file(
            BytesIO(mp4_data),
            mimetype='video/mp4',
            as_attachment=False,
            download_name='animation.mp4'
        )
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': '视频转换超时'}), 500
    except Exception as e:
        print(f"转换MP4失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
