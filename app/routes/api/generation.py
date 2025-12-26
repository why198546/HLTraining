"""生成相关API路由 - 图片、视频、3D模型等生成"""
import json
import os
import re
import traceback
import uuid
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_prompt
from api.sam3d_api import SAM3DAPI
from app.utils import allowed_file, normalize_path_for_url, preprocess_sketch
from managers.creation_session_manager import CreationSessionManager
from app import db

generation_api_bp = Blueprint('generation_api', __name__)

# 初始化managers
session_manager = CreationSessionManager()


@generation_api_bp.route('/sam3d/info')
def sam3d_info():
    """获取SAM 3D模型信息"""
    try:
        sam3d = SAM3DAPI()
        info = sam3d.get_model_info()
        return jsonify({
            'success': True,
            'info': info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generation_api_bp.route('/generate-image', methods=['POST'])
def api_generate_image():
    """统一的图片生成接口 - 支持文字和图片混合输入，支持会话版本管理"""
    try:
        prompt = request.form.get('prompt', '').strip()
        style = request.form.get('style', 'cute')
        color_preference = request.form.get('color_preference', 'colorful')
        expert_mode = request.form.get('expert_mode', 'false').lower() == 'true'
        aspect_ratio = request.form.get('aspect_ratio', '1:1')
        uploaded_file = request.files.get('sketch')
        original_image_path = request.form.get('original_image_path', '').strip()
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        num_images = int(request.form.get('num_images', '1'))  # 默认生成1张，松果课堂会传入4
        
        # 获取自定义宽高（用于手绘画布）
        custom_width = request.form.get('width')
        custom_height = request.form.get('height')
        
        # 如果提供了自定义宽高，根据比例计算aspect_ratio
        if custom_width and custom_height:
            width = int(custom_width)
            height = int(custom_height)
            ratio = width / height
            
            # 映射到最接近的标准比例
            if 0.9 <= ratio <= 1.1:
                aspect_ratio = "1:1"
            elif 1.7 <= ratio <= 1.9:
                aspect_ratio = "16:9"
            elif 0.5 <= ratio <= 0.6:
                aspect_ratio = "9:16"
            elif 1.4 <= ratio <= 1.6:
                aspect_ratio = "3:2"
            elif 0.6 <= ratio <= 0.7:
                aspect_ratio = "2:3"
            else:
                aspect_ratio = "1:1"  # 默认使用1:1
            
            print(f"📐 自定义分辨率: {width}x{height}, 计算比例: {aspect_ratio}")
        
        print(f"📝 输入参数: prompt={prompt}, style={style}, uploaded_file={uploaded_file.filename if uploaded_file else None}")
        
        if not prompt and not uploaded_file and not original_image_path:
            print("❌ 缺少必要参数")
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
        # 检查用户松果币是否足够（教师和管理员不检查）
        if current_user and current_user.is_authenticated:
            if current_user.role not in ['teacher', 'admin']:
                if hasattr(current_user, 'image_token_remaining'):
                    tokens_needed = num_images  # 生成几张图需要几个币
                    if current_user.image_token_remaining < tokens_needed:
                        print(f"❌ 用户 {current_user.username} 松果币不足: 需要{tokens_needed}个，剩余{current_user.image_token_remaining}个")
                        return jsonify({
                            'error': f'松果币不足！需要{tokens_needed}个，当前剩余{current_user.image_token_remaining}个。请联系老师充值。',
                            'remaining_tokens': current_user.image_token_remaining
                        }), 403
                    print(f"✅ 用户 {current_user.username} 松果币充足: 需要{tokens_needed}个，剩余{current_user.image_token_remaining}个")
                else:
                    print(f"⚠️ 用户 {current_user.username} 没有 image_token_remaining 属性")
        
        # 如果提示词中包含人物但未指定国籍，默认添加"中国人形象"
        if prompt:
            has_nationality = bool(re.search(r'外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾', prompt, re.IGNORECASE))
            has_person = bool(re.search(r'人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师', prompt))
            
            if not has_nationality and has_person and '中国' not in prompt:
                prompt = '中国人形象，' + prompt
                print(f"✅ 自动添加中国人形象，新提示词: {prompt}")
        
        print(f"🎨 生成参数 - 风格: {style}, 色彩: {color_preference}, Expert模式: {expert_mode}, 高宽比: {aspect_ratio}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 处理上传的图片或使用原始图片路径
        sketch_path = None
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = str(uuid.uuid4()) + '_' + secure_filename(uploaded_file.filename)
            sketch_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(sketch_path)
            print(f"📁 图片已保存: {sketch_path}")
            
            # 智能预处理：自动判断是否需要处理（手绘线稿会处理，彩色参考图保持原样）
            processed_sketch = preprocess_sketch(sketch_path, force_process=False)
            if processed_sketch:
                sketch_path = processed_sketch
        elif original_image_path:
            # 使用已有的原始图片（生成更多功能）
            if original_image_path.startswith('/uploads/'):
                sketch_path = 'uploads' + original_image_path[8:]
            elif original_image_path.startswith('uploads/'):
                sketch_path = original_image_path
            else:
                sketch_path = os.path.join('uploads', original_image_path)
        
        print(f"🎨 开始生成 {num_images} 张图片 - 文字: {prompt}, 图片: {sketch_path}")
        
        # 智能分析prompt，检测10个核心特征，动态生成差异化描述
        def analyze_and_generate_variations(prompt_text, num_variations=4):
            """分析prompt中已提到的特征，为未提到的特征生成差异化描述
            返回: (variations, detected_features_dict)"""
            import random
            
            # 10个核心特征及其检测关键词和变化选项
            features = {
                'gender': {
                    'keywords': ['男孩', '女孩', '男', '女', '男生', '女生', '小伙', '姑娘', '闪男', '闪女'],
                    'options': [],
                    'index': 0
                },
                'body': {
                    'keywords': ['胖', '瘦', '壮', '苗条', '强壮', '纤细', '肥胖', '削瘦', '身材', '胖嘟嘟', '壮实', '结实'],
                    'options': ['偏瘦身材', '身材适中', '偏胖身材', '匀称身材'],
                    'index': 1
                },
                'hair_length': {
                    'keywords': ['长发', '短发', '中长发', '齐肩发', '披肩发', '长头发', '短头发', '头发'],
                    'options': ['短发', '中长发', '长发', '齐肩发'],
                    'index': 2
                },
                'hair_style': {
                    'keywords': ['卷发', '直发', '波浪', '自然卷', '微卷', '卷头发', '直头发', '平头', '寸头', '光头', '马尾', '辫子', '发型'],
                    'options': ['直发', '微卷发', '卷发', '自然发'],
                    'index': 3
                },
                'skin': {
                    'keywords': ['皮肤黑', '皮肤白', '肤色', '黑皮肤', '白皮肤', '皮肤', '黑', '白', '黑黑', '白白', '黑黑的', '白白的', '黑色', '白色', '黝黑', '白皙', '深色', '浅色', '深色皮肤', '浅色皮肤'],
                    'options': ['皮肤白皙', '皮肤偏黑', '皮肤中等', '健康肤色'],
                    'index': 4
                },
                'eyes': {
                    'keywords': ['大眼睛', '小眼睛', '眼睛大', '眼睛小', '单眼皮', '双眼皮', '眼睛', '大眼', '小眼'],
                    'options': ['大眼睛', '小眼睛', '中等眼睛', '明亮眼睛'],
                    'index': 5
                },
                'nose': {
                    'keywords': ['大鼻子', '小鼻子', '高鼻梁', '低鼻梁', '挺鼻', '鼻子大', '鼻子小', '塌鼻子', '鼻梁', '鼻子', '高高的鼻子', '高高的鼻梁'],
                    'options': ['小巧鼻子', '高挺鼻梁', '中等鼻子', '秀气鼻子'],
                    'index': 6
                },
                'mouth': {
                    'keywords': ['大嘴', '小嘴', '嘴大', '嘴小', '樱桃小嘴', '嘴巴'],
                    'options': ['嘴巴适中', '小嘴', '嘴型饱满', '嘴型秀气'],
                    'index': 7
                },
                'lips': {
                    'keywords': ['厚嘴唇', '薄嘴唇', '嘴唇厚', '嘴唇薄', '嘴唇', '肥厚的嘴唇', '肥肥的嘴唇', '肥嘴唇'],
                    'options': ['薄嘴唇', '嘴唇适中', '厚嘴唇', '嘴唇自然'],
                    'index': 8
                },
                'ears': {
                    'keywords': ['大耳朵', '小耳朵', '耳朵大', '耳朵小', '耳朵'],
                    'options': ['小耳朵', '耳朵适中', '大耳朵', '耳朵秀气'],
                    'index': 9
                }
            }
            
            # 检测prompt中已提到的特征
            mentioned_features = {}
            for feature_name, feature_data in features.items():
                for keyword in feature_data['keywords']:
                    if keyword in prompt_text:
                        # 返回特征索引和检测到的关键词
                        mentioned_features[feature_data['index']] = keyword
                        break
            
            print(f"🔍 检测到已提及的特征: {mentioned_features}")
            
            # 为未提及的特征生成差异化选项
            unmentioned_features = {k: v for k, v in features.items() 
                                   if v['index'] not in mentioned_features and v['options']}
            
            # 生成num_variations个变化描述
            variations = []
            for i in range(num_variations):
                variation_parts = []
                for feature_name, feature_data in unmentioned_features.items():
                    if feature_data['options']:
                        # 为每个变化选择不同的选项
                        option_index = i % len(feature_data['options'])
                        variation_parts.append(feature_data['options'][option_index])
                
                if variation_parts:
                    variations.append("，补充特征：" + "，".join(variation_parts))
                else:
                    # 如果所有特征都已提及，使用细微的绘画技法差异
                    variations.append(f"，第{i+1}个版本")
            
            print(f"✨ 生成的差异化描述: {variations}")
            return variations, mentioned_features
        
        # 智能生成变化因子和检测特征
        variations, mentioned_features = analyze_and_generate_variations(prompt, num_images)
        
        # 生成多张图片
        generated_images = []
        errors = []  # 收集错误信息
        for i in range(num_images):
            print(f"📸 生成第 {i+1}/{num_images} 张图片...")
            try:
                # 为每张图片添加变化后缀，避免人物一致性
                varied_prompt = prompt
                if num_images > 1 and i < len(variations):
                    varied_prompt = prompt + variations[i]
                    print(f"📝 变化后的提示词: {varied_prompt}")
                
                # 根据输入类型生成图片
                if sketch_path and varied_prompt:
                    # 图片+文字模式
                    generated_image_path = nano_banana.generate_image_from_sketch_and_text(
                        sketch_path, varied_prompt, style=style, aspect_ratio=aspect_ratio
                    )
                elif sketch_path:
                    # 纯图片模式
                    generated_image_path = nano_banana.generate_image_from_sketch(
                        sketch_path, style=style, aspect_ratio=aspect_ratio
                    )
                else:
                    # 纯文字模式
                    generated_image_path = nano_banana.generate_image_from_text(
                        varied_prompt, style=style, aspect_ratio=aspect_ratio
                    )
                
                if generated_image_path and os.path.exists(generated_image_path):
                    generated_images.append(generated_image_path)
                    print(f"✅ 第 {i+1} 张图片生成成功: {generated_image_path}")
                else:
                    error_msg = f"第 {i+1} 张图片生成返回None或文件不存在"
                    errors.append(error_msg)
                    print(f"⚠️ {error_msg}")
            except Exception as e:
                error_msg = f"第 {i+1} 张图片生成异常: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
                import traceback
                traceback.print_exc()
        
        # 检查是否至少有一张图片生成成功
        if not generated_images:
            error_detail = " | ".join(errors) if errors else "未知错误"
            print(f"❌ 所有图片生成失败: {error_detail}")
            return jsonify({'error': f'图片生成失败: {error_detail}'}), 500
        
        print(f"✅ 成功生成 {len(generated_images)} 张图片")
        
        # 返回相对路径用于前端显示
        relative_paths = [normalize_path_for_url(path) for path in generated_images]
        print(f"📍 返回 {len(relative_paths)} 张图片URL: {relative_paths}")
        
        # 使用第一张图片作为主图片
        generated_image_path = generated_images[0]
        relative_path = relative_paths[0]
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        version_file_path = None
        if session_id:
            metadata = {
                'prompt': prompt,
                'has_sketch': sketch_path is not None,
                'generation_type': 'mixed' if sketch_path and prompt else ('sketch' if sketch_path else 'text'),
                'note': version_note
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='image',
                file_path=generated_image_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                # 自动选择新生成的版本
                session_manager.select_version(session_id, version_id)
                
                # 使用版本管理器中的文件路径（已复制到creation_sessions目录）
                version_filename = version_result.get('filename')
                if version_filename:
                    version_file_path = f'/creation_sessions/{session_id}/{version_filename}'
                    relative_path = version_file_path  # 更新为版本管理器的路径
                    print(f"📍 更新为版本管理器路径: {relative_path}")
        
        # 准备返回数据
        response_data = {
            'success': True,
            'image_url': relative_path,  # 第一张图片作为主图
            'image_urls': relative_paths,  # 所有图片的URL数组
            'image_path': relative_path,
            'version_id': version_id,
            'detected_features': mentioned_features,  # 返回检测到的特征
            'message': f'成功生成 {len(relative_paths)} 张图片！'
        }
        
        # 如果有上传的图片，也返回原始图片路径
        if sketch_path:
            response_data['original_image_url'] = normalize_path_for_url(sketch_path)
        
        # 扣除用户的松果币（教师和管理员不扣）
        if current_user and current_user.is_authenticated:
            if current_user.role not in ['teacher', 'admin']:
                # 每生成一张图扣1个币，num_images张就扣num_images个币
                if hasattr(current_user, 'image_token_remaining'):
                    tokens_to_deduct = num_images
                    current_user.image_token_remaining -= tokens_to_deduct
                    db.session.commit()
                    response_data['remaining_tokens'] = current_user.image_token_remaining
                    print(f"💰 已为用户 {current_user.username} 扣除 {tokens_to_deduct} 个松果币，剩余: {current_user.image_token_remaining}")
                else:
                    print(f"⚠️ 用户 {current_user.username} 没有 image_token_remaining 属性")
            else:
                # 教师和管理员不扣币
                if hasattr(current_user, 'image_token_remaining'):
                    response_data['remaining_tokens'] = current_user.image_token_remaining
                    print(f"✅ 用户 {current_user.username} 是 {current_user.role}，无需扣币")
        
        return jsonify(response_data)
            
    except Exception as e:
        print(f"❌ 图片生成错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@generation_api_bp.route('/generate-video', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        from api.veo31 import get_veo_api
        
        data = request.get_json()
        session_id = data.get('session_id')
        image_url = data.get('image_url')
        original_prompt = data.get('prompt')
        duration = data.get('duration', 8)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        quality = data.get('quality', '720p')
        motion_intensity = data.get('motion_intensity', 'medium')
        model = data.get('model', 'veo-3.1-fast-generate-preview')  # 默认使用快速版模型
        
        if not session_id or not image_url or not original_prompt:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        print(f"🎬 开始生成视频...")
        print(f"   会话ID: {session_id}")
        print(f"   图片: {image_url}")
        print(f"   原始提示词: {original_prompt}")
        print(f"   时长: {duration}秒")
        print(f"   比例: {aspect_ratio}")
        print(f"   质量: {quality}")
        print(f"   运动强度: {motion_intensity}")
        print(f"   模型: {model}")
        
        # 翻译prompt
        print(f"🌐 翻译prompt...")
        translated_prompt = translate_prompt(original_prompt)
        print(f"✅ 翻译后: {translated_prompt}")
        
        # 调用Veo API生成视频
        veo_api = get_veo_api()
        result = veo_api.generate_video(
            image_url=image_url,
            prompt=translated_prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            quality=quality,
            motion_intensity=motion_intensity,
            model=model
        )
        
        if result['success']:
            print(f"✅ 视频生成任务已提交: {result.get('task_id')}")
            return jsonify(result)
        else:
            print(f"❌ 视频生成失败: {result.get('error')}")
            return jsonify(result), 500
        
    except Exception as e:
        print(f"❌ 视频生成错误: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@generation_api_bp.route('/video-status/<path:task_id>')
def video_status(task_id):
    """检查视频生成状态"""
    try:
        from api.veo31 import get_veo_api
        
        print(f"🔍 检查任务状态: {task_id}")
        
        veo_api = get_veo_api()
        status_result = veo_api.check_status(task_id)
        
        print(f"📊 状态结果: {status_result}")
        
        # 确保返回success字段
        if 'success' not in status_result:
            status_result['success'] = status_result.get('status') != 'failed'
        
        return jsonify(status_result)
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 状态检查错误: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'status': 'failed',
            'error': error_msg,
            'message': f'状态检查失败: {error_msg}'
        }), 500


@generation_api_bp.route('/generate-artwork-info', methods=['POST'])
def generate_artwork_info_api():
    """使用AI生成作品的标题、分类和介绍"""
    try:
        import google.generativeai as genai
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'prompt为空'}), 400
        
        print(f"🎨 为prompt生成作品信息: {prompt}")
        
        # 配置Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API密钥未配置'}), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 构建生成指令
        system_prompt = """你是一个创意作品命名和介绍专家，请根据用户的创作提示词，生成以下内容：

1. 作品标题：简短有趣（4-10个字），适合儿童作品
2. 作品分类：从以下类别选择一个最合适的：
   - animals（动物）
   - characters（人物）
   - objects（物品）
   - nature（自然）
   - other（其他）
3. 作品介绍：编写一个100字左右的儿童友好小故事，描述这个创作的奇妙之处

请严格按照以下JSON格式返回（不要任何markdown标记或代码块标记）：
{
  "title": "作品标题",
  "category": "分类英文",
  "description": "作品介绍小故事"
}

示例：
提示词："一只可爱的小猫咪，戴着红色的帽子，坐在彩虹上..."

返回：
{
  "title": "彩虹上的猫咪",
  "category": "animals",
  "description": "在一个阳光明媚的早晨，一只勇敢的小猫咪戴上了它最喜欢的红色帽子，踏上了一场奇妙的冒险。它爬上了天边的彩虹，那里有七种颜色的道路，每一步都闪闪发光。小猫咪坐在彩虹的最顶端，俯瞰着整个世界，感觉自己就像一个小小的探险家。这是属于它的奇妙时刻！"
}

现在请为以下提示词生成作品信息："""
        
        # 调用AI生成
        full_prompt = f"{system_prompt}\n\n提示词：{prompt}"
        response = model.generate_content(full_prompt)
        result_text = response.text.strip()
        
        # 移除可能的markdown代码块标记
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            # 移除第一行和最后一行的```
            result_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
        if result_text.startswith('json'):
            result_text = result_text[4:].strip()
        
        print(f"📝 AI生成的JSON: {result_text}")
        
        # 解析JSON
        artwork_info = json.loads(result_text)
        
        return jsonify({
            'success': True,
            'title': artwork_info.get('title', ''),
            'category': artwork_info.get('category', 'other'),
            'description': artwork_info.get('description', '')
        })
        
    except Exception as e:
        print(f"❌ 生成作品信息失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
