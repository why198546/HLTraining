"""松果正式课程相关API端点"""
import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

# 导入AI API
from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_to_english

formal_lesson_bp = Blueprint('formal_lesson', __name__)


@formal_lesson_bp.route('/api/generate-image', methods=['POST'])
@login_required
def generate_image():
    """生成图片 - 基于特征选择"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        lesson_key = data.get('lesson_key', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': '提示词不能为空'})
        
        # 添加固定后缀，确保生成儿童友好的图片
        full_prompt = f"{prompt}，卡通风格，可爱风格，儿童插画，简单背景，明亮色彩"
        
        # 翻译成英文
        english_prompt = translate_to_english(full_prompt)
        
        # 调用Nano Banana API生成图片
        nb_api = NanoBananaAPI()
        image_path = nb_api.generate_image_from_text(english_prompt, style="cute", aspect_ratio="512x512")
        
        if image_path:
            # 返回相对URL
            image_url = f"/uploads/{os.path.basename(image_path)}"
            return jsonify({
                'success': True,
                'image_url': image_url,
                'prompt': full_prompt
            })
        else:
            return jsonify({
                'success': False,
                'error': '图片生成失败，请重试'
            })
            
    except Exception as e:
        current_app.logger.error(f"图片生成失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/combine-images', methods=['POST'])
@login_required
def combine_images():
    """组合图片 - 课后小游戏"""
    try:
        lesson_key = request.form.get('lesson_key', '')
        photo = request.files.get('photo')
        artwork = request.files.get('artwork')
        
        if not photo or not artwork:
            return jsonify({'success': False, 'error': '请同时上传照片和画作'})
        
        # 读取图片
        photo_img = Image.open(photo.stream).convert('RGBA')
        artwork_img = Image.open(artwork.stream).convert('RGBA')
        
        # 根据课程类型进行不同的组合方式
        if 'hairstyle' in lesson_key:
            # 发型课：提取画作中的发型，叠加到照片的人物头部
            result_img = combine_hairstyle(photo_img, artwork_img)
        elif 'clothing' in lesson_key:
            # 服饰课：提取画作中的服装，叠加到照片的人物身体
            result_img = combine_clothing(photo_img, artwork_img)
        else:
            # 默认：简单并排显示
            result_img = combine_side_by_side(photo_img, artwork_img)
        
        # 保存到临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"combined_{lesson_key}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        
        # 确保uploads目录存在
        uploads_dir = os.path.join(current_app.root_path, '..', 'uploads', 'combined')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filepath = os.path.join(uploads_dir, filename)
        result_img.save(filepath, 'PNG')
        
        # 返回URL
        image_url = f"/uploads/combined/{filename}"
        
        return jsonify({
            'success': True,
            'image_url': image_url
        })
        
    except Exception as e:
        current_app.logger.error(f"图片组合失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


def combine_hairstyle(photo, artwork):
    """组合发型 - 简化版本"""
    # 创建画布
    width = max(photo.width, artwork.width) * 2 + 50
    height = max(photo.height, artwork.height) + 100
    
    canvas = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    
    # 调整图片大小
    photo = resize_to_fit(photo, (width // 2 - 50, height - 100))
    artwork = resize_to_fit(artwork, (width // 2 - 50, height - 100))
    
    # 粘贴图片
    canvas.paste(photo, (25, 50), photo)
    canvas.paste(artwork, (width // 2 + 25, 50), artwork)
    
    # 添加箭头和文字
    draw = ImageDraw.Draw(canvas)
    
    # 绘制箭头
    arrow_y = height // 2
    arrow_x1 = width // 2 - 20
    arrow_x2 = width // 2 + 20
    draw.line([(arrow_x1, arrow_y), (arrow_x2, arrow_y)], fill=(107, 91, 149), width=5)
    draw.polygon([(arrow_x2, arrow_y), (arrow_x2 - 15, arrow_y - 10), (arrow_x2 - 15, arrow_y + 10)], 
                 fill=(107, 91, 149))
    
    return canvas.convert('RGB')


def combine_clothing(photo, artwork):
    """组合服装 - 简化版本"""
    return combine_hairstyle(photo, artwork)  # 使用相同的并排显示方式


def combine_side_by_side(photo, artwork):
    """并排显示"""
    # 调整图片大小到相同高度
    target_height = 600
    photo_width = int(photo.width * (target_height / photo.height))
    artwork_width = int(artwork.width * (target_height / artwork.height))
    
    photo = photo.resize((photo_width, target_height), Image.LANCZOS)
    artwork = artwork.resize((artwork_width, target_height), Image.LANCZOS)
    
    # 创建画布
    total_width = photo_width + artwork_width + 60
    canvas = Image.new('RGB', (total_width, target_height + 40), (255, 255, 255))
    
    # 粘贴图片
    canvas.paste(photo, (20, 20))
    canvas.paste(artwork, (photo_width + 40, 20))
    
    return canvas


def resize_to_fit(img, max_size):
    """调整图片大小以适应最大尺寸"""
    ratio = min(max_size[0] / img.width, max_size[1] / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    return img.resize(new_size, Image.LANCZOS)


@formal_lesson_bp.route('/api/artwork-feedback', methods=['POST'])
@login_required
def artwork_feedback():
    """AI点评作品 - 适合8-14岁儿童"""
    try:
        lesson_key = request.form.get('lesson_key', '')
        image = request.files.get('image')
        
        if not image:
            return jsonify({'success': False, 'error': '请上传作品图片'})
        
        # 这里应该调用AI模型进行图片分析和点评
        # 为了演示，我们先返回一个模板化的点评
        
        # 根据课程类型生成不同的点评重点
        feedback_templates = {
            'formal_hairstyle': {
                'aspects': ['发型的线条流畅度', '发丝的层次感', '整体造型的美感'],
                'encouragement': '你对发型的观察很仔细！'
            },
            'formal_face': {
                'aspects': ['脸型的比例', '轮廓的清晰度', '整体的协调性'],
                'encouragement': '你画的脸型很有特点！'
            },
            'formal_facial_features': {
                'aspects': ['五官的位置', '眼睛的神态', '表情的生动性'],
                'encouragement': '你的五官画得很传神！'
            },
            'formal_skin_color': {
                'aspects': ['色彩的选择', '光影的处理', '质感的表现'],
                'encouragement': '你对色彩的运用很棒！'
            },
            'formal_body_type': {
                'aspects': ['身体比例', '姿态自然度', '动态感'],
                'encouragement': '你对人体比例把握得很好！'
            },
            'formal_clothing': {
                'aspects': ['服装的细节', '色彩搭配', '质感表现'],
                'encouragement': '你的服装设计很有创意！'
            },
            'formal_accessories': {
                'aspects': ['饰品的位置', '大小比例', '装饰效果'],
                'encouragement': '你的饰品设计很精致！'
            },
            'formal_perspective': {
                'aspects': ['透视的准确性', '空间感', '景深效果'],
                'encouragement': '你对空间的理解很到位！'
            },
            'formal_weather': {
                'aspects': ['天气氛围', '色调选择', '特效表现'],
                'encouragement': '你营造的氛围很有感染力！'
            },
            'formal_location': {
                'aspects': ['场景的完整性', '细节的丰富度', '环境氛围'],
                'encouragement': '你的场景设计很用心！'
            },
            'formal_composition1': {
                'aspects': ['人物与体态的协调', '整体比例', '视觉平衡'],
                'encouragement': '你的人物塑造很完整！'
            },
            'formal_composition2': {
                'aspects': ['人物与场景的融合', '空间关系', '故事性'],
                'encouragement': '你的画面很有故事感！'
            },
            'formal_composition3': {
                'aspects': ['多元素的协调', '画面的层次', '视觉焦点'],
                'encouragement': '你的构图很有章法！'
            },
            'formal_ai_animation': {
                'aspects': ['动态表现', '节奏感', '流畅度'],
                'encouragement': '你的作品充满了生命力！'
            },
            'formal_final_work': {
                'aspects': ['创意表达', '技法运用', '情感传递'],
                'encouragement': '这是一幅非常出色的作品！'
            }
        }
        
        template = feedback_templates.get(lesson_key, {
            'aspects': ['整体构图', '色彩运用', '创意表现'],
            'encouragement': '你的作品很有想象力！'
        })
        
        # 生成点评内容
        feedback = f"""🌟 {template['encouragement']}

✨ 亮点：
• 你的作品很有自己的特色
• 能看出你很认真地在创作
• 色彩的运用很大胆，很有创意

💡 建议：
• 可以在细节上再多花一些心思
• 注意{template['aspects'][0]}的处理
• 尝试让{template['aspects'][1]}更加突出

🎯 练习方向：
继续保持你的创作热情！下次创作时，可以特别关注{template['aspects'][2]}，相信你会画得更好！

记住：每一幅作品都是你成长的印记，继续加油！💪"""
        
        return jsonify({
            'success': True,
            'feedback': feedback
        })
        
    except Exception as e:
        current_app.logger.error(f"作品点评失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
