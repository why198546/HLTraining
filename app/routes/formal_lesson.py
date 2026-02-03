"""松果正式课程相关API端点"""
import base64
import io
import os
import uuid
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# 导入AI API
from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_prompt
# 导入数据库
from auth.models import db

formal_lesson_bp = Blueprint('formal_lesson', __name__)


@formal_lesson_bp.route('/api/formal-lesson/generate-image', methods=['POST'])
@login_required
def generate_image():
    """生成图片 - 基于特征选择，支持多种风格"""
    try:
        # 解析请求数据
        try:
            data = request.json
            if not data:
                current_app.logger.error('❌ 请求体为空或格式错误')
                return jsonify({'success': False, 'error': '请求数据格式错误'}), 400
        except Exception as e:
            current_app.logger.error(f'❌ JSON解析失败: {str(e)}')
            return jsonify({'success': False, 'error': f'JSON解析失败: {str(e)}'}), 400
        
        prompt = data.get('prompt', '').strip()
        lesson_key = data.get('lesson_key', '')
        styles = data.get('styles', ['realistic'])  # 默认真实风格
        
        current_app.logger.info(f'📥 收到生成请求 - 提示词: "{prompt}", 课程: {lesson_key}, 风格: {styles}')
        
        # 验证提示词
        if not prompt:
            current_app.logger.warning('❌ 提示词为空')
            return jsonify({'success': False, 'error': '提示词不能为空'}), 400
        
        # 验证风格列表
        if not styles or len(styles) == 0:
            current_app.logger.warning('❌ 未选择风格')
            return jsonify({'success': False, 'error': '请至少选择一种生成风格'}), 400
        
        current_app.logger.info(f'✅ 参数验证通过，开始生成图片...')
        
        # 课程针对性构图提示配置
        lesson_composition_hints = {
            'formal_hairstyle': '上半身肖像，突出发型特征，干净纯色背景',
            'formal_face': '面部清晰',
            'formal_facial_features': '五官清晰',
            'formal_body_type': '全身展示',
            'formal_clothing': '展示服装',
            'formal_weather': '自然光线',
            'formal_location': '场景完整',
            'formal_composition1': '构图完整',
            'formal_composition2': '氛围协调',
            'formal_composition3': '画面丰富',
            'formal_ai_animation': '创意表现',
            'formal_final_work': '综合创作'
        }
        
        # 强制需要构图提示的课程（如发型课程必须指定上半身+干净背景）
        force_composition_lessons = ['formal_hairstyle']
        
        # 获取当前课程的构图提示
        composition_hint = lesson_composition_hints.get(lesson_key, '')
        
        # 判断是否需要强制添加构图提示
        force_composition = lesson_key in force_composition_lessons
        
        # 风格配置
        style_configs = {
            'realistic': {
                'name': '真实照片风格',
                'icon': 'fa-camera-retro',
                'suffix': '真实照片风格'
            },
            'cartoon': {
                'name': '卡通可爱风格',
                'icon': 'fa-smile',
                'suffix': '卡通可爱Q版风格'
            },
            'sketch': {
                'name': '素描线稿风格',
                'icon': 'fa-pencil-alt',
                'suffix': '黑白素描线稿'
            },
            'anime': {
                'name': '动漫风格',
                'icon': 'fa-star',
                'suffix': '日式动漫风格'
            },
            'watercolor': {
                'name': '水彩风格',
                'icon': 'fa-fill-drip',
                'suffix': '柔和水彩画风格'
            }
        }
        
        # 调用Nano Banana API生成多种风格的图片
        nb_api = NanoBananaAPI()
        results = []
        
        for style in styles:
            style_config = style_configs.get(style, style_configs['realistic'])
            
            # 组合完整提示词：确保用户提示词优先级最高
            # 特殊处理：发型等需要特定构图的课程，始终添加构图提示
            user_prompt_length = len(prompt.replace(' ', '').replace(',', '').replace('，', ''))
            
            # 发型课程强制添加构图提示
            if force_composition and composition_hint:
                full_prompt = f"{prompt}，{style_config['suffix']}，{composition_hint}"
                current_app.logger.info(f"课程类型({lesson_key})需要强制构图，已添加构图提示")
            # 用户提示词详细且不需要强制构图时，只加风格后缀
            elif user_prompt_length > 10 and not force_composition:
                full_prompt = f"{prompt}，{style_config['suffix']}"
                current_app.logger.info(f"用户提示词详细({user_prompt_length}字)，不添加构图提示")
            # 提示词简短时，添加构图辅助
            elif composition_hint:
                full_prompt = f"{prompt}，{style_config['suffix']}，{composition_hint}"
                current_app.logger.info(f"用户提示词简短({user_prompt_length}字)，添加构图辅助")
            else:
                full_prompt = f"{prompt}，{style_config['suffix']}"
            
            current_app.logger.info(f"=== {style_config['name']} 生成流程 ===")
            current_app.logger.info(f"1. 课程类型: {lesson_key}")
            current_app.logger.info(f"2. 原始用户提示词: {prompt}")
            current_app.logger.info(f"3. 提示词长度: {user_prompt_length}字")
            current_app.logger.info(f"4. 是否强制构图: {force_composition}")
            current_app.logger.info(f"5. 风格后缀: {style_config['suffix']}")
            current_app.logger.info(f"6. 构图提示: {composition_hint if composition_hint else '无'}")
            current_app.logger.info(f"7. 完整中文提示词: {full_prompt}")
            
            try:
                # 翻译成英文
                english_prompt = translate_prompt(full_prompt)
                current_app.logger.info(f"8. 翻译后英文提示词: {english_prompt}")
                current_app.logger.info(f"9. Gemini生成模型: models/gemini-2.5-flash-image")
                current_app.logger.info(f"10. 生成风格参数: {'cute' if style == 'cartoon' else 'realistic'}")
                current_app.logger.info(f"11. 图片尺寸: 512x512")
                
                # 生成图片
                image_path = nb_api.generate_image_from_text(
                    english_prompt, 
                    style="cute" if style == 'cartoon' else "realistic", 
                    aspect_ratio="512x512"
                )
                
                if image_path:
                    image_url = f"/uploads/{os.path.basename(image_path)}"
                    results.append({
                        'style': style,
                        'style_name': style_config['name'],
                        'style_icon': style_config['icon'],
                        'image_url': image_url
                    })
                    current_app.logger.info(f"✅ {style_config['name']}生成成功")
                else:
                    current_app.logger.error(f"❌ {style_config['name']}生成失败")
                    
            except Exception as e:
                current_app.logger.error(f"❌ {style_config['name']}生成异常: {str(e)}")
                continue
        
        if not results:
            current_app.logger.error('❌ 所有风格生成都失败了')
            return jsonify({
                'success': False, 
                'error': '所有风格生成都失败了，请稍后重试'
            }), 500
        
        current_app.logger.info(f'✅ 成功生成 {len(results)}/{len(styles)} 张图片')
        return jsonify({
            'success': True,
            'results': results,
            'message': f'成功生成{len(results)}张图片'
        }), 200
            
    except Exception as e:
        current_app.logger.error(f"❌ 图片生成异常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False, 
            'error': f'生成失败: {str(e)}'
        }), 500


@formal_lesson_bp.route('/api/formal-lesson/combine-images', methods=['POST'])
@login_required
def combine_images():
    """组合图片 - 课后小游戏 - 使用AI生成多种风格的融合效果"""
    try:
        current_app.logger.info('=== 开始处理图片组合请求 ===')
        
        lesson_key = request.form.get('lesson_key', '')
        photo = request.files.get('photo')
        artwork = request.files.get('artwork')
        styles_json = request.form.get('styles', '["realistic"]')
        
        # 解析风格列表
        import json
        selected_styles = json.loads(styles_json)
        
        current_app.logger.info(f'课程key: {lesson_key}')
        current_app.logger.info(f'照片: {photo.filename if photo else "None"}')
        current_app.logger.info(f'画作: {artwork.filename if artwork else "None"}')
        current_app.logger.info(f'选中风格: {selected_styles}')
        
        if not photo or not artwork:
            current_app.logger.error('缺少照片或画作')
            return jsonify({'success': False, 'error': '请同时上传照片和画作'})
        
        # 保存上传的图片到临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_photo_filename = f"temp_photo_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        temp_artwork_filename = f"temp_artwork_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        
        uploads_dir = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        photo_path = os.path.join(uploads_dir, temp_photo_filename)
        artwork_path = os.path.join(uploads_dir, temp_artwork_filename)
        
        current_app.logger.info(f'保存照片到: {photo_path}')
        current_app.logger.info(f'保存画作到: {artwork_path}')
        
        # 加载并压缩图片（提升API处理速度）
        from app.utils import compress_image
        
        photo_img = Image.open(photo.stream)
        artwork_img = Image.open(artwork.stream)
        
        current_app.logger.info(f'原始照片大小: {photo_img.size}')
        current_app.logger.info(f'原始画作大小: {artwork_img.size}')
        
        # 压缩到1024px最大边长，质量85%
        photo_img = compress_image(photo_img, max_size=1024, quality=85)
        artwork_img = compress_image(artwork_img, max_size=1024, quality=85)
        
        # 保存压缩后的图片
        photo_img.save(photo_path, 'JPEG', quality=85)
        artwork_img.save(artwork_path, 'JPEG', quality=85)
        
        current_app.logger.info(f'压缩后照片大小: {photo_img.size}')
        current_app.logger.info(f'压缩后画作大小: {artwork_img.size}')
        
        # 风格配置
        style_configs = {
            'realistic': {
                'name': '真实照片风格',
                'icon': 'fa-camera-retro',
                'suffix': '保持真实照片风格，只应用特征变化，不做风格转换。'
            },
            'cartoon': {
                'name': '卡通可爱风格',
                'icon': 'fa-smile',
                'suffix': '转换为可爱的卡通风格（Q版、儿童插画风格），色彩明亮、线条简洁，儿童友好。'
            },
            'sketch': {
                'name': '素描线稿风格',
                'icon': 'fa-pencil-alt',
                'suffix': '转换为黑白素描风格，使用线条勾勒轮廓和细节，展现艺术感。'
            },
            'anime': {
                'name': '动漫风格',
                'icon': 'fa-star',
                'suffix': '转换为日式动漫风格，大眼睛、流畅线条、鲜艳色彩，充满活力。'
            },
            'watercolor': {
                'name': '水彩风格',
                'icon': 'fa-fill-drip',
                'suffix': '转换为柔和的水彩画风格，色彩渐变自然，边缘柔和，艺术气息浓厚。'
            }
        }
        
        # 根据课程类型生成基础描述（默认值 - 使用变量占位符格式）
        base_descriptions = {
            'formal_hairstyle': '''请仔细观察第二张图中的发型，包括：
1. 发型的长度和层次
2. 刘海的样式
3. 头发的卷曲程度和纹理
4. 发饰和装饰物（如花朵、发带等）
5. 整体发型轮廓
然后将这个完整的发型精确地应用到第一张照片中的人物头上，确保发型的所有细节都能体现。保持人物的面部特征、表情、肤色完全不变。

{composition_hint}

风格要求：{style_suffix}''',
            'formal_face': '''请将第二张图中的脸型（脸部轮廓、下巴形状）应用到第一张照片中的人物上。保持五官特征不变。

{composition_hint}

风格要求：{style_suffix}''',
            'formal_facial_features': '''请将第二张图中的五官特征（眼睛、鼻子、嘴巴的形状和大小）应用到第一张照片中的人物上。保持脸型轮廓不变。

{composition_hint}

风格要求：{style_suffix}''',
            'formal_skin_color': '''请将第二张图中的肤色色调应用到第一张照片中的人物上。保持面部特征和轮廓不变。

{composition_hint}

风格要求：{style_suffix}''',
            'formal_body_type': '''请仔细观察第二张图中手绘作品的人物形体特征，包括：
1. 身材比例（头身比、四肢长度比例）
2. 体型特点（高矮胖瘦、身材轮廓）
3. 姿态和站姿
4. 整体形体风格
然后将这个手绘作品中的形体特征应用到第一张照片中的真人上，采用第一张照片人物的面部特征（脸型、五官、表情），结合第二张图手绘作品的身体形态，生成一个完整的人物形象。保持第一张照片中人物的面部完全不变，只改变身体的体型和比例。

{composition_hint}

风格要求：{style_suffix}''',
            'formal_clothing': '''请将第二张图中的服装（款式、颜色、图案）应用到第一张照片中的人物上。保持人物姿态和面部特征不变。

{composition_hint}

风格要求：{style_suffix}'''
        }
        
        # 课程针对性构图提示
        composition_hints = {
            'formal_hairstyle': '生成头部特写和上半身照片，重点展示发型细节，面部特征可以适当简化，使用干净的背景。',
            'formal_face': '生成面部特写，清晰展示脸型轮廓。',
            'formal_facial_features': '生成面部特写，突出五官细节。',
            'formal_body_type': '生成全身照，展示身材比例。',
            'formal_clothing': '生成全身或半身照，突出服装细节。'
        }
        
        # 尝试从模板系统读取自定义的base_description（模块二）
        try:
            from sqlalchemy import text
            from auth.models import User
            
            # 获取当前用户或其教师的模板
            teacher = None
            if current_user.role == 'student':
                result = db.session.execute(
                    text('SELECT teacher_id FROM student_courses WHERE student_id = :sid LIMIT 1'),
                    {'sid': current_user.id}
                ).fetchone()
                if result and result[0]:
                    teacher = User.query.get(result[0])
            elif current_user.role in ['teacher', 'admin']:
                teacher = current_user
            
            # 检查是否有自定义模板
            if teacher and teacher.module_templates:
                lesson_templates = teacher.module_templates.get(lesson_key, {})
                module2_template = lesson_templates.get('module2', {})
                
                # 如果模板是text模式且有raw_prompt，使用它替换base_description
                if module2_template.get('mode') == 'text' and module2_template.get('raw_prompt'):
                    base_description = module2_template['raw_prompt']
                    current_app.logger.info(f'✅ 使用自定义模板: {base_description[:50]}...')
                else:
                    base_description = base_descriptions.get(lesson_key, '请将第二张图中的特征应用到第一张照片的人物上。\n\n{composition_hint}\n\n风格要求：{style_suffix}')
            else:
                base_description = base_descriptions.get(lesson_key, '请将第二张图中的特征应用到第一张照片的人物上。\n\n{composition_hint}\n\n风格要求：{style_suffix}')
        except Exception as e:
            current_app.logger.warning(f'读取自定义模板失败，使用默认值: {str(e)}')
            base_description = base_descriptions.get(lesson_key, '请将第二张图中的特征应用到第一张照片的人物上。\n\n{composition_hint}\n\n风格要求：{style_suffix}')
        
        composition_hint = composition_hints.get(lesson_key, '')
        
        # 使用 Nano Banana API 进行图像融合
        current_app.logger.info('开始调用Gemini API进行图像融合...')
        nb_api = NanoBananaAPI()
        
        # 检查API是否正确初始化
        if not nb_api.client:
            error_msg = "Gemini API 未正确配置，请检查 GEMINI_API_KEY 环境变量"
            current_app.logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg})
        
        # 检查是否启用Vision提取模式（从请求中获取，默认启用）
        use_vision_extraction = request.form.get('use_vision_extraction', 'true').lower() == 'true'
        current_app.logger.info(f"🔬 Vision提取模式: {'已启用' if use_vision_extraction else '已禁用'}")
        
        # 为每种风格生成图片（串行生成，确保稳定性）
        results = []
        errors = []
        extracted_features = None  # 存储提取的特征（只需提取一次）
        
        current_app.logger.info(f"📋 准备生成 {len(selected_styles)} 种风格的图片")
        
        for idx, style in enumerate(selected_styles, 1):
            style_config = style_configs.get(style, style_configs['realistic'])
            
            current_app.logger.info(f"========================================")
            current_app.logger.info(f"🎨 [{idx}/{len(selected_styles)}] 开始生成 {style_config['name']}")
            current_app.logger.info(f"风格代码: {style}")
            current_app.logger.info(f"========================================")
            
            try:
                # 风格映射到API参数
                api_style_map = {
                    'realistic': 'realistic',
                    'cartoon': 'cute',
                    'sketch': 'realistic',  # 素描使用realistic，通过description控制
                    'anime': 'anime',
                    'watercolor': 'realistic'  # 水彩使用realistic，通过description控制
                }
                api_style = api_style_map.get(style, 'cute')
                
                current_app.logger.info(f"🔧 API风格参数: {api_style}")
                current_app.logger.info(f"📸 照片路径: {photo_path}")
                current_app.logger.info(f"🎨 画作路径: {artwork_path}")
                current_app.logger.info(f"⏰ 准备调用API...")
                
                # 根据模式选择生成方法
                result_path = None
                features = None
                
                if use_vision_extraction:
                    current_app.logger.info(f"🔬 使用Vision提取模式")
                    try:
                        result_path, features = nb_api.combine_with_vision_extraction(
                            image1_path=photo_path,
                            image2_path=artwork_path,
                            lesson_type=lesson_key,
                            style=api_style,
                            aspect_ratio="512x512"
                        )
                        
                        if result_path:
                            current_app.logger.info(f"✅ Vision提取模式生成成功")
                            # 第一次提取时保存特征信息
                            if features and not extracted_features:
                                extracted_features = features
                                current_app.logger.info(f"💾 已保存提取的特征信息")
                        else:
                            current_app.logger.warning(f"⚠️ Vision提取模式返回None，回退到传统模式")
                            
                    except Exception as vision_error:
                        current_app.logger.error(f"❌ Vision提取模式异常: {str(vision_error)}")
                        current_app.logger.exception(vision_error)
                        result_path = None
                
                # 如果Vision模式失败或未启用，使用传统模式
                if not result_path:
                    if use_vision_extraction:
                        current_app.logger.info(f"🔄 自动回退到传统Prompt模式")
                    else:
                        current_app.logger.info(f"📝 使用传统Prompt模式")
                    
                    # 传统方法：使用模板变量
                    description = base_description.replace('{composition_hint}', composition_hint)
                    description = description.replace('{style_suffix}', style_config['suffix'])
                    current_app.logger.info(f"完整提示词: {description[:200]}...")
                    
                    try:
                        result_path = nb_api.combine_two_images(
                            image1_path=photo_path,
                            image2_path=artwork_path,
                            description=description,
                            style=api_style,
                            aspect_ratio="512x512"
                        )
                    except Exception as trad_error:
                        current_app.logger.error(f"❌ 传统模式也失败: {str(trad_error)}")
                        current_app.logger.exception(trad_error)
                        result_path = None
                
                current_app.logger.info(f"⏰ API调用完成，result_path: {result_path}")
                
                if result_path:
                    # 构建URL
                    if 'combined' in result_path:
                        idx_pos = result_path.find('combined')
                        relative_path = result_path[idx_pos:]
                        image_url = f"/uploads/{relative_path}"
                    else:
                        image_url = f"/uploads/{os.path.basename(result_path)}"
                    
                    result_item = {
                        'style': style,
                        'style_name': style_config['name'],
                        'style_icon': style_config['icon'],
                        'image_url': image_url
                    }
                    
                    # 如果有提取的特征信息，附加到第一个结果
                    if extracted_features and len(results) == 0:
                        result_item['features'] = extracted_features
                    
                    results.append(result_item)
                    current_app.logger.info(f"✅ [{idx}/{len(selected_styles)}] {style_config['name']}生成成功: {image_url}")
                    current_app.logger.info(f"✅ 当前已成功生成 {len(results)} 张，失败 {len(errors)} 张")
                else:
                    error_msg = f"{style_config['name']}生成失败: API返回None"
                    current_app.logger.error(f"❌ [{idx}/{len(selected_styles)}] {error_msg}")
                    errors.append(error_msg)
                    current_app.logger.error(f"⚠️ 继续处理下一个风格...")
                    # 即使失败也继续生成其他风格
                    
            except Exception as e:
                error_msg = f"{style_config['name']}生成异常: {str(e)}"
                current_app.logger.error(f"❌ [{idx}/{len(selected_styles)}] {error_msg}")
                current_app.logger.exception(e)
                errors.append(error_msg)
                current_app.logger.error(f"⚠️ 捕获异常，继续处理下一个风格...")
                # 即使异常也继续生成其他风格
                continue
        
        current_app.logger.info(f"========================================")
        current_app.logger.info(f"🏁 循环结束: 成功{len(results)}个, 失败{len(errors)}个")
        current_app.logger.info(f"========================================")
        
        if not results:
            error_detail = '; '.join(errors) if errors else '所有风格生成都失败了'
            return jsonify({'success': False, 'error': error_detail})
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'成功生成{len(results)}张图片'
        })
            
    except Exception as e:
        error_msg = f"图片组合失败: {str(e)}"
        current_app.logger.error(error_msg)
        current_app.logger.exception(e)
        return jsonify({'success': False, 'error': str(e)})
        current_app.logger.error(error_msg)
        current_app.logger.exception(e)
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


@formal_lesson_bp.route('/api/formal-lesson/artwork-feedback', methods=['POST'])
@login_required
def artwork_feedback():
    """AI点评作品 - 使用Gemini Vision真实分析图片内容 + TTS语音播放
    
    自动使用课程级模板（course-specific template）或教师的全局模板
    """
    try:
        lesson_key = request.form.get('lesson_key', '')
        image = request.files.get('image')
        
        if not image:
            return jsonify({'success': False, 'error': '请上传作品图片'})
        
        # 保存上传的图片到临时文件
        temp_filename = f"temp_artwork_{uuid.uuid4()}.png"
        temp_path = os.path.join('uploads', temp_filename)
        image.save(temp_path)
        
        current_app.logger.info(f"📥 收到作品点评请求 - 课程: {lesson_key}, 图片: {temp_path}")
        
        # 获取点评模板 - 优先级：课程级模板 > 教师全局模板 > 默认模板
        from auth.models import User
        
        feedback_templates = get_default_feedback_templates()  # 先用默认
        teacher = None
        
        # 确定教师身份（如果当前用户是学生，需要查找其教师）
        if current_user.role == 'teacher':
            teacher = current_user
        elif current_user.role == 'student':
            # 从enrollment中获取学生所属的教师
            from sqlalchemy import text
            result = db.session.execute(
                text('''
                    SELECT DISTINCT u.id, u.username FROM users u 
                    JOIN student_courses sc ON u.id = sc.teacher_id 
                    WHERE sc.student_id = :student_id AND u.role = 'teacher'
                    LIMIT 1
                '''),
                {'student_id': current_user.id}
            )
            row = result.fetchone()
            if row:
                teacher = User.query.get(row[0])
        
        # 使用教师的模板（如果存在）
        if teacher and teacher.feedback_templates:
            feedback_templates = teacher.feedback_templates
            current_app.logger.info(f"✅ 使用教师 {teacher.username} 的自定义模板")
        else:
            current_app.logger.info(f"ℹ️ 使用默认评审模板")
        
        # 获取该课程的模板
        template = feedback_templates.get(lesson_key, {
            'aspects': ['整体构图', '色彩运用', '创意表现'],
            'encouragement': '你的作品很有想象力！'
        })
        mode = template.get('mode', 'structured')
        aspects = template.get('aspects', ['整体构图', '色彩运用', '创意表现'])
        encouragement = template.get('encouragement', '你的作品很有想象力！')

        # 文本模式下允许自定义提示词
        prompt_override = None
        if mode == 'text' and template.get('raw_prompt'):
            aspects_text = "\n".join([f"{i + 1}. {a}" for i, a in enumerate(aspects)]) if aspects else ""
            prompt_override = (
                template['raw_prompt']
                .replace("{lesson_type}", lesson_key.replace('formal_', '').replace('_', ' '))
                .replace("{aspects}", aspects_text)
            )
        
        # 调用Gemini Vision分析图片
        current_app.logger.info(f"🔍 开始Vision分析 - 维度: {aspects}")
        nano_api = NanoBananaAPI()
        vision_result = nano_api.analyze_artwork_with_vision(
            image_path=temp_path,
            lesson_type=lesson_key,
            aspects=aspects,
            prompt_override=prompt_override
        )
        
        # 如果Vision分析成功，使用分析结果；否则使用默认模板
        if vision_result:
            current_app.logger.info(f"✅ Vision分析成功")
            highlights = vision_result.get('highlights') or ['作品很有创意', '色彩运用大胆', '整体效果不错']
            suggestions = vision_result.get('suggestions') or ['可以注意细节处理', '尝试更多风格', '继续保持创作热情']
            overall = vision_result.get('overall') or '整体表现不错，继续保持你的创作热情！'

            highlights_text = "\n".join([f"• {item}" for item in highlights if item])
            suggestions_text = "\n".join([f"• {item}" for item in suggestions if item])

            feedback = f"""🌟 {encouragement}

✨ 作品亮点：
{highlights_text}

💡 改进建议：
{suggestions_text}

🎯 总体评价：
{overall}

记住：每一幅作品都是你成长的印记，继续加油！💪"""
        else:
            # Vision分析失败，使用默认模板
            current_app.logger.warning(f"⚠️ Vision分析失败，使用默认模板")
            fallback_highlights = ['你的作品很有自己的特色', '能看出你很认真地在创作', '色彩的运用很大胆，很有创意']
            if aspects:
                fallback_suggestions = [f"可以重点关注 {a} 的表现" for a in aspects]
            else:
                fallback_suggestions = ['可以在细节上再多花一些心思', '尝试更多不同的风格', '继续保持创作热情']

            highlights_text = "\n".join([f"• {item}" for item in fallback_highlights if item])
            suggestions_text = "\n".join([f"• {item}" for item in fallback_suggestions if item])

            feedback = f"""🌟 {encouragement}

✨ 亮点：
{highlights_text}

💡 建议：
{suggestions_text}

🎯 练习方向：
继续保持你的创作热情！下次创作时，试着在以上维度上多做一点点调整，你一定会画得更好！

记住：每一幅作品都是你成长的印记，继续加油！💪"""
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'feedback': feedback,
            'analyzed_by_vision': vision_result is not None
        })
        
    except Exception as e:
        current_app.logger.error(f"作品点评失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/formal-lesson/generate-tts', methods=['POST'])
@login_required
def generate_tts():
    """独立的TTS生成接口 - 按需生成语音"""
    try:
        data = request.json
        text = data.get('text', '')
        voice_name = data.get('voice_name', 'Puck')
        use_pro_model = data.get('use_pro_model', False)
        
        if not text:
            return jsonify({'success': False, 'error': '文本不能为空'})
        
        current_app.logger.info(f"🔊 按需生成TTS语音...")
        
        from api.tts_service import get_tts_service
        tts = get_tts_service()
        audio_result = tts.generate_feedback_audio(
            feedback_text=text,
            use_pro_model=use_pro_model,
            voice_name=voice_name
        )
        
        if audio_result:
            current_app.logger.info(f"✅ TTS生成成功 ({audio_result['model']}, {audio_result['voice_name']})")
            return jsonify({
                'success': True,
                'audio': audio_result['audio_base64'],
                'audio_mime_type': audio_result.get('mime_type', 'audio/wav'),
                'tts_model': audio_result['model'],
                'tts_voice': audio_result['voice_name']
            })
        else:
            return jsonify({'success': False, 'error': 'TTS生成失败'})
            
    except Exception as e:
        current_app.logger.error(f"TTS生成失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


def get_formal_curriculum_structure():
    """
    获取正式课程体系结构 - 共15课时
    """
    return {
        'modules': [
            {
                'id': 'portrait',
                'name': '一、人像',
                'icon': 'fa-user-circle',
                'description': '学习人物肖像绘制',
                'hours': 3,
                'lessons': [
                    {
                        'id': 'formal_facial_features',
                        'name': '五官/比例',
                        'description': '五官位置关系与人物比例',
                        'hours': 1,
                        'order': 1
                    },
                    {
                        'id': 'formal_face',
                        'name': '表情',
                        'description': '丰富的表情表现',
                        'hours': 1,
                        'order': 2
                    },
                    {
                        'id': 'formal_hairstyle',
                        'name': '发型',
                        'description': '各种发型的绘制表现',
                        'hours': 1,
                        'order': 3
                    }
                ]
            },
            {
                'id': 'posture',
                'name': '二、体态',
                'icon': 'fa-walking',
                'description': '学习人体结构与动作',
                'hours': 3,
                'lessons': [
                    {
                        'id': 'formal_body_type',
                        'name': '体型',
                        'description': '人体比例与体型塑造',
                        'hours': 1,
                        'order': 1
                    },
                    {
                        'id': 'formal_ai_animation',
                        'name': '动作',
                        'description': '人物动态姿态表现',
                        'hours': 1,
                        'order': 2
                    },
                    {
                        'id': 'formal_clothing',
                        'name': '服装',
                        'description': '服装设计与穿着效果',
                        'hours': 1,
                        'order': 3
                    }
                ]
            },
            {
                'id': 'scene',
                'name': '三、场景',
                'icon': 'fa-image',
                'description': '学习场景与环境表现',
                'hours': 3,
                'lessons': [
                    {
                        'id': 'formal_location',
                        'name': '生活场景',
                        'description': '日常生活场景的刻画',
                        'hours': 1,
                        'order': 1
                    },
                    {
                        'id': 'formal_weather',
                        'name': '自然场景',
                        'description': '山水、植物等自然元素',
                        'hours': 1,
                        'order': 2
                    },
                    {
                        'id': 'formal_perspective',
                        'name': '气候与光影',
                        'description': '天气效果与特殊光影',
                        'hours': 1,
                        'order': 3
                    }
                ]
            },
            {
                'id': 'composition',
                'name': '四、综合创作',
                'icon': 'fa-palette',
                'description': '综合应用与创意创作',
                'hours': 5,
                'lessons': [
                    {
                        'id': 'formal_composition1',
                        'name': '生活组合',
                        'description': '生活场景的多人物组合创作',
                        'hours': 2,
                        'order': 1
                    },
                    {
                        'id': 'formal_accessories',
                        'name': '科幻 x 玄幻主题',
                        'description': '科幻与奇幻元素的创意表现',
                        'hours': 2,
                        'order': 2
                    },
                    {
                        'id': 'formal_final_work',
                        'name': '自由创意',
                        'description': '完全自由的创意表现',
                        'hours': 1,
                        'order': 3
                    }
                ]
            }
        ]
    }


def get_default_feedback_templates():
    """
    获取默认点评模板 - 专业艺术教学评估标准
    基于以下评估维度：
    1. 技法维度：基础技能掌握程度
    2. 审美维度：艺术表现力和美感
    3. 创意维度：创新性和个性表达
    """
    return {
        'formal_hairstyle': {
            'aspects': ['线条精准度与蓬松感', '层次感与空间表现', '风格特征的表现力'],
            'encouragement': '你对发型细节的观察很敏锐！'
        },
        'formal_face': {
            'aspects': ['脸型比例的准确性', '脸部轮廓的立体感', '脸型特征的个性体现'],
            'encouragement': '你对脸型结构的理解很深入！'
        },
        'formal_facial_features': {
            'aspects': ['五官位置关系的准确性', '眼睛神韵与情感表达', '五官整体协调度'],
            'encouragement': '你捕捉的表情很富有生命力！'
        },
        'formal_body_type': {
            'aspects': ['人体比例结构的科学性', '肢体姿态的自然度', '身体动态的灵活性'],
            'encouragement': '你对人体结构的把握很专业！'
        },
        'formal_clothing': {
            'aspects': ['服装褶皱与质感的表现', '色彩搭配的审美水准', '穿着效果的逼真度'],
            'encouragement': '你对服装设计的感知很敏锐！'
        },
        'formal_weather': {
            'aspects': ['气象特征的视觉表现', '光线变化对画面的影响', '氛围渲染的感染力'],
            'encouragement': '你营造的意境很富有画意！'
        },
        'formal_location': {
            'aspects': ['环境细节的丰富度与准确性', '场景特征的识别度', '环境与人物的融合度'],
            'encouragement': '你对环境刻画的细致程度很专业！'
        },
        'formal_perspective': {
            'aspects': ['天气氛围的营造', '光影变化的表现力', '整体意境的传达'],
            'encouragement': '你对气候与光影的表现很富有感染力！'
        },
        'formal_composition1': {
            'aspects': ['生活场景布局的合理性', '多人物关系的表现力', '故事叙述的完整度'],
            'encouragement': '你对生活场景的表现力很强！'
        },
        'formal_accessories': {
            'aspects': ['科幻与奇幻元素的融合', '想象力的创意表现', '视觉冲击力和感染力'],
            'encouragement': '你的想象力和创意表现很出众！'
        },
        'formal_ai_animation': {
            'aspects': ['动作连贯性与自然度', '节奏感与表现力', '视觉吸引力'],
            'encouragement': '你创作的动画充满活力！'
        },
        'formal_final_work': {
            'aspects': ['创意主题的独特表达', '综合技法的整体运用', '个人艺术风格的形成'],
            'encouragement': '这是一部充满想象力的作品！'
        }
    }


def build_default_feedback_prompt(lesson_key, aspects):
    """生成默认的AI点评提示词模板（保留占位符）"""
    return """你是一位专业的儿童美术教师，正在点评一位10-14岁学生的AI生成作品。

课程主题：{lesson_type}

请从以下维度分析这幅作品：
{aspects}

要求：
1. 语气温和友好，适合儿童阅读
2. 多鼓励，少批评
3. 具体指出画面中的优点（至少3个）
4. 给出可操作的改进建议（至少3个）
5. 用简洁的语言总结整体印象

请以JSON格式返回：
{
    "highlights": ["具体亮点1", "具体亮点2", "具体亮点3"],
    "suggestions": ["具体建议1", "具体建议2", "具体建议3"],
    "overall": "一句话总体评价"
}

注意：
- highlights要具体描述画面中的优点，不要泛泛而谈
- suggestions要给出明确的改进方向，让孩子知道下次怎么做
- 语言要简单直白，避免专业术语"""


@formal_lesson_bp.route('/api/formal-lesson/feedback-templates', methods=['GET'])
@login_required
def get_feedback_templates():
    """获取当前教师的点评模板"""
    try:
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({'success': False, 'error': '仅教师和管理员可访问'})
        
        # 如果教师还没有自定义模板，返回默认模板
        if not current_user.feedback_templates:
            return jsonify({'success': True, 'templates': get_default_feedback_templates()})
        
        return jsonify({'success': True, 'templates': current_user.feedback_templates})
        
    except Exception as e:
        current_app.logger.error(f"获取点评模板失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/formal-lesson/feedback-templates', methods=['POST'])
@login_required
def update_feedback_templates():
    """更新教师的点评模板"""
    try:
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({'success': False, 'error': '仅教师和管理员可修改模板'})
        
        templates = request.json.get('templates')
        if not templates:
            return jsonify({'success': False, 'error': '模板数据不能为空'})
        
        # 验证模板格式
        for lesson_key, template in templates.items():
            if 'aspects' not in template or 'encouragement' not in template:
                return jsonify({'success': False, 'error': f'模板 {lesson_key} 格式错误'})
            if not isinstance(template['aspects'], list) or len(template['aspects']) != 3:
                return jsonify({'success': False, 'error': f'模板 {lesson_key} 的aspects必须是包含3个元素的列表'})
        
        # 保存到数据库（深拷贝确保变化被检测）
        import copy
        current_user.feedback_templates = copy.deepcopy(templates)
        
        # 标记字段已修改
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, 'feedback_templates')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '模板更新成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新点评模板失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/formal-lesson/generate-improved', methods=['POST'])
@login_required
def generate_improved():
    """根据AI点评生成改良版图片"""
    try:
        import base64
        import io
        import tempfile

        from PIL import Image

        from api.nano_banana import NanoBananaAPI
        from api.prompt_translator import translate_prompt
        
        current_app.logger.info('🎨 接收改良版生成请求...')
        
        # 验证必要的文件和参数
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '缺少上传的图片文件'}), 400
        
        image_file = request.files['image']
        improvement_prompt = request.form.get('improvement_prompt', '')
        lesson_key = request.form.get('lesson_key', '')
        
        if not image_file or image_file.filename == '':
            return jsonify({'success': False, 'error': '图片文件无效'}), 400
        
        if not improvement_prompt:
            return jsonify({'success': False, 'error': '改良提示词不能为空'}), 400
        
        current_app.logger.info(f'📝 改良提示词: {improvement_prompt[:100]}...')
        current_app.logger.info(f'📚 课程: {lesson_key}')
        
        # 读取原始图片并保存到临时文件（因为API需要文件路径）
        try:
            image_data = image_file.read()
            original_image = Image.open(io.BytesIO(image_data))
            current_app.logger.info(f'✅ 成功读取原始图片: {original_image.size}')
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                original_image.save(tmp_file.name)
                temp_image_path = tmp_file.name
                current_app.logger.info(f'✅ 临时图片文件: {temp_image_path}')
        except Exception as e:
            current_app.logger.error(f'❌ 图片读取失败: {str(e)}')
            return jsonify({'success': False, 'error': '图片处理失败'}), 400
        
        # 翻译提示词
        try:
            translated_prompt = translate_prompt(improvement_prompt)
            current_app.logger.info(f'🌐 翻译后提示词: {translated_prompt[:100]}...')
        except Exception as e:
            current_app.logger.warning(f'⚠️ 提示词翻译失败，使用原文: {str(e)}')
            translated_prompt = improvement_prompt
        
        # 调用生成API
        try:
            nano_api = NanoBananaAPI()
            
            current_app.logger.info('🚀 调用Nano Banana API生成改良版...')
            
            # 使用generate_image_from_reference作为改良版生成
            # 这个方法接收一张参考图和描述，生成相关的新图片
            image_path = nano_api.generate_image_from_reference(
                sketch_path=temp_image_path,
                description=translated_prompt,
                style="cute",
                aspect_ratio="512x512",
                require_skeleton=False
            )
            
            if not image_path:
                current_app.logger.error('❌ 生成API返回无效结果')
                return jsonify({'success': False, 'error': 'AI生成失败，请重试'}), 500
            
            current_app.logger.info(f'✅ 改良版生成成功!')
            current_app.logger.info(f'📸 生成图片路径: {image_path}')
            
            # 清理临时文件
            try:
                import os
                os.remove(temp_image_path)
            except:
                pass
            
            # 转换为可访问的URL格式
            image_url = f"/uploads/{os.path.basename(image_path)}"
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'model': 'nano-banana'
            })
            
        except Exception as e:
            current_app.logger.error(f'❌ 生成API调用失败: {str(e)}')
            # 清理临时文件
            try:
                import os
                os.remove(temp_image_path)
            except:
                pass
            return jsonify({'success': False, 'error': f'生成失败: {str(e)}'}), 500
    
    except Exception as e:
        current_app.logger.error(f'❌ 改良版生成异常: {str(e)}')
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


@formal_lesson_bp.route('/api/formal-lesson/curriculum', methods=['GET'])
@login_required
def get_curriculum():
    """获取正式课程体系结构"""
    try:
        curriculum = get_formal_curriculum_structure()
        return jsonify({'success': True, 'curriculum': curriculum})
    except Exception as e:
        current_app.logger.error(f"获取课程体系失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/formal-lesson/lesson-template', methods=['GET'])
@login_required
def get_lesson_template():
    """获取单个课程的AI点评模板"""
    try:
        lesson_key = request.args.get('lesson_key')
        if not lesson_key:
            return jsonify({'success': False, 'error': '课程key不能为空'})
        
        # 如果用户是学生，获取其所属教师的模板
        teacher = None
        if current_user.role == 'student':
            # 获取学生所属的教师（假设在enrollment中有关系）
            # 从student_courses表中获取教师
            from sqlalchemy import text

            from auth.models import User
            result = db.session.execute(
                text('''
                    SELECT u.id FROM users u 
                    JOIN student_courses sc ON u.id = sc.teacher_id 
                    WHERE sc.student_id = :student_id LIMIT 1
                '''),
                {'student_id': current_user.id}
            )
            row = result.fetchone()
            if row:
                from auth.models import User
                teacher = User.query.get(row[0])
        elif current_user.role in ['teacher', 'admin']:
            teacher = current_user
        
        # 获取模板
        if teacher and teacher.feedback_templates and lesson_key in teacher.feedback_templates:
            template = teacher.feedback_templates[lesson_key]
        else:
            # 返回默认模板
            default_templates = get_default_feedback_templates()
            template = default_templates.get(lesson_key, {
                'aspects': ['整体构图', '色彩运用', '创意表现'],
                'encouragement': '你的作品很有想象力！'
            })

        # 补齐字段
        if 'mode' not in template:
            template['mode'] = 'structured'
        if 'raw_prompt' not in template or not template.get('raw_prompt'):
            template['raw_prompt'] = build_default_feedback_prompt(lesson_key, template.get('aspects', []))
        
        return jsonify({'success': True, 'template': template})
        
    except Exception as e:
        current_app.logger.error(f'获取课程模板失败: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@formal_lesson_bp.route('/api/formal-lesson/lesson-template', methods=['POST'])
@login_required
def save_lesson_template():
    """保存单个课程的AI点评模板（课程级覆盖）"""
    try:
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({'success': False, 'error': '仅教师和管理员可修改模板'})
        
        data = request.json
        lesson_key = data.get('lesson_key')
        encouragement = data.get('encouragement', '').strip()
        aspects = data.get('aspects', [])
        mode = data.get('mode', 'structured')
        raw_prompt = data.get('raw_prompt', '').strip()
        
        if not lesson_key or not encouragement:
            return jsonify({'success': False, 'error': '参数不完整或格式错误'})

        if not isinstance(aspects, list) or not all(a.strip() for a in aspects):
            return jsonify({'success': False, 'error': '评价维度不能为空'})

        if mode == 'structured' and len(aspects) != 3:
            return jsonify({'success': False, 'error': '结构化模式需要填写3个评价维度'})

        if mode == 'text' and not raw_prompt:
            return jsonify({'success': False, 'error': '纯文字模式需要填写提示词'})
        
        # 初始化教师的模板字典（如果为空）
        # 使用深拷贝确保SQLAlchemy能检测到变化
        import copy
        if not current_user.feedback_templates:
            feedback_templates_copy = get_default_feedback_templates()
        else:
            feedback_templates_copy = copy.deepcopy(current_user.feedback_templates)
        
        # 更新该课程的模板
        feedback_templates_copy[lesson_key] = {
            'encouragement': encouragement,
            'aspects': [a.strip() for a in aspects],
            'mode': mode,
            'raw_prompt': raw_prompt
        }
        
        # 重新赋值整个对象
        current_user.feedback_templates = feedback_templates_copy
        
        # 标记字段已修改
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, 'feedback_templates')
        
        db.session.commit()
        
        current_app.logger.info(f"✅ 教师 {current_user.username} 保存了课程 {lesson_key} 的模板")
        return jsonify({'success': True, 'message': '模板保存成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'保存课程模板失败: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})

