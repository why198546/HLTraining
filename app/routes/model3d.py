"""3D模型相关路由"""
import os
import uuid

from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

from api.nano_banana import NanoBananaAPI
from app.utils import auto_save_artwork_to_db, normalize_path_for_url
from managers.creation_session_manager import CreationSessionManager
from managers.model3d_manager import Model3DManager

model3d_bp = Blueprint('model3d', __name__)

# 初始化管理器
session_manager = CreationSessionManager()


@model3d_bp.route('/generate-image', methods=['POST'])
def generate_image():
    """统一的图片生成接口 - 支持文字和图片混合输入，支持会话版本管理"""
    import sys
    sys.stdout.flush()
    sys.stderr.write("=" * 80 + "\n")
    sys.stderr.write("🚀 收到图片生成请求\n")
    sys.stderr.flush()
    
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
        
        print(f"📝 输入参数: prompt={prompt}, style={style}, uploaded_file={uploaded_file.filename if uploaded_file else None}")
        
        if not prompt and not uploaded_file and not original_image_path:
            print("❌ 缺少必要参数")
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
        # 使用PromptManager处理提示词
        from managers.prompt_manager import PromptManager
        if prompt:
            prompt = PromptManager.add_default_nationality(prompt)
        
        print(f"🎨 生成参数 - 风格: {style}, 色彩: {color_preference}, Expert模式: {expert_mode}, 高宽比: {aspect_ratio}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 处理上传的图片或使用原始图片路径
        sketch_path = None
        if uploaded_file and Model3DManager.allowed_file(uploaded_file.filename):
            from flask import current_app
            filename = str(uuid.uuid4()) + '_' + secure_filename(uploaded_file.filename)
            sketch_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(sketch_path)
            
            # 预处理手绘图片
            processed_sketch = Model3DManager.preprocess_sketch(sketch_path)
            if processed_sketch:
                sketch_path = processed_sketch
        elif original_image_path:
            # 使用已有的原始图片
            if original_image_path.startswith('/uploads/'):
                sketch_path = 'uploads' + original_image_path[8:]
            elif original_image_path.startswith('uploads/'):
                sketch_path = original_image_path
            else:
                sketch_path = os.path.join('uploads', original_image_path)
        
        print(f"🎨 开始生成图片 - 文字: {prompt}, 图片: {sketch_path}")
        
        # 根据输入类型生成图片
        if sketch_path and prompt:
            generated_image_path = nano_banana.generate_image_from_sketch_and_text(
                sketch_path, prompt, style=style, color_preference=color_preference, 
                expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        elif sketch_path:
            generated_image_path = nano_banana.generate_image_from_sketch(
                sketch_path, style=style, color_preference=color_preference, 
                expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        else:
            generated_image_path = nano_banana.generate_image_from_text(
                prompt, style=style, color_preference=color_preference, 
                expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        
        print(f"✅ 图片生成完成: {generated_image_path}")
        
        # 检查图片是否真的生成成功
        if not generated_image_path or not os.path.exists(generated_image_path):
            print(f"❌ 图片生成失败，不保存到数据库")
            return jsonify({'error': '图片生成失败，请重试'}), 500
        
        # 返回相对路径用于前端显示
        relative_path = normalize_path_for_url(generated_image_path)
        print(f"📍 返回图片URL: {relative_path}")
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
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
                session_manager.select_version(session_id, version_id)
                
                # 自动保存到数据库（如果用户已登录且图片生成成功）
                if current_user.is_authenticated:
                    try:
                        auto_save_artwork_to_db(session_id, generated_image_path, sketch_path, prompt)
                        print(f"🎨 作品已自动保存到数据库: {session_id}")
                    except Exception as e:
                        print(f"⚠️ 自动保存失败: {str(e)}")
        
        # 准备返回数据
        response_data = {
            'success': True,
            'image_url': relative_path,
            'version_id': version_id,
            'message': '图片生成成功！'
        }
        
        if sketch_path:
            response_data['original_image_url'] = normalize_path_for_url(sketch_path)
        
        return jsonify(response_data)
            
    except Exception as e:
        print(f"❌ 图片生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@model3d_bp.route('/adjust-image', methods=['POST'])
def adjust_image():
    """调整现有图片"""
    try:
        current_image = request.form.get('current_image')
        adjust_prompt = request.form.get('adjust_prompt', '').strip()
        expert_mode = request.form.get('expert_mode', 'false').lower() == 'true'
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not current_image or not adjust_prompt:
            return jsonify({'error': '缺少图片路径或调整说明'}), 400
        
        # 将相对路径转换为绝对路径
        if current_image.startswith('/uploads/'):
            current_image = current_image.replace('/uploads/', 'uploads/')
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        print(f"🔧 开始调整图片: {current_image} - 调整说明: {adjust_prompt}, Expert模式: {expert_mode}")
        
        # 使用调整提示词重新生成图片
        adjusted_image_path = nano_banana.adjust_image(current_image, adjust_prompt, expert_mode=expert_mode)
        
        print(f"✅ 图片调整完成: {adjusted_image_path}")
        
        # 返回相对路径
        relative_path = normalize_path_for_url(adjusted_image_path)
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'adjust_prompt': adjust_prompt,
                'base_image': current_image,
                'generation_type': 'adjustment',
                'note': version_note
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='image',
                file_path=adjusted_image_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'image_url': relative_path,
            'version_id': version_id,
            'message': '图片调整成功！'
        })
            
    except Exception as e:
        print(f"❌ 图片调整错误: {str(e)}")
        return jsonify({'error': f'调整失败: {str(e)}'}), 500


@model3d_bp.route('/generate-multi-view', methods=['POST'])
def generate_multi_view():
    """生成多视角图片用于3D建模（正、反、左、右）"""
    try:
        prompt = request.form.get('prompt', '').strip()
        color_preference = request.form.get('color_preference', 'colorful')
        aspect_ratio = request.form.get('aspect_ratio', '1:1')
        session_id = request.form.get('session_id')
        
        if not prompt:
            return jsonify({'error': '请输入文字描述'}), 400
        
        print(f"🎨 多视角生成参数 - 描述: {prompt}, 色彩: {color_preference}, 高宽比: {aspect_ratio}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 生成4个视角的图片
        result = nano_banana.generate_multi_view_images(
            text_prompt=prompt,
            color_preference=color_preference,
            aspect_ratio=aspect_ratio
        )
        
        if not result:
            return jsonify({'error': '多视角图片生成失败，请重试'}), 500
        
        # 转换为相对路径
        image_urls = {}
        for view_name, path in result.items():
            image_urls[view_name] = normalize_path_for_url(path)
        
        print(f"✅ 多视角图片生成完成: {image_urls}")
        
        return jsonify({
            'success': True,
            'images': image_urls,
            'message': '多视角图片生成成功！'
        })
            
    except Exception as e:
        print(f"❌ 多视角图片生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@model3d_bp.route('/upload-reference-image', methods=['POST'])
def upload_reference_image():
    """上传参考图片并返回URL，用于直接生成视频"""
    try:
        if 'reference_image' not in request.files:
            return jsonify({'success': False, 'error': '未找到上传的文件'}), 400
        
        file = request.files['reference_image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400
        
        # 创建临时会话目录
        session_id = str(uuid.uuid4())
        session_dir = os.path.join('creation_sessions', session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # 保存上传的文件
        file_ext = os.path.splitext(file.filename)[1]
        filename = f'reference_image{file_ext}'
        filepath = os.path.join(session_dir, filename)
        file.save(filepath)
        
        # 构建URL
        image_url = url_for('static', filename=f'../creation_sessions/{session_id}/{filename}', _external=True)
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"❌ 上传参考图片错误: {str(e)}")
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500


@model3d_bp.route('/generate-3d-model', methods=['POST'])
def generate_3d_model_endpoint():
    """从图片生成3D模型，支持会话版本管理和多视角输入"""
    try:
        # 检查是否是多视角模式
        is_multi_view = request.form.get('multi_view') == 'true'
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if is_multi_view:
            # 多视角模式
            front_image = request.form.get('front_image')
            back_image = request.form.get('back_image')
            left_image = request.form.get('left_image')
            right_image = request.form.get('right_image')
            
            if not all([front_image, back_image, left_image, right_image]):
                return jsonify({'error': '多视角模式需要提供所有4个视角的图片'}), 400
            
            # 转换路径
            view_images = {
                'front': front_image.replace('/uploads/', 'uploads/') if front_image.startswith('/uploads/') else front_image,
                'back': back_image.replace('/uploads/', 'uploads/') if back_image.startswith('/uploads/') else back_image,
                'left': left_image.replace('/uploads/', 'uploads/') if left_image.startswith('/uploads/') else left_image,
                'right': right_image.replace('/uploads/', 'uploads/') if right_image.startswith('/uploads/') else right_image
            }
            
            print(f"🧊 开始生成3D模型（多视角模式）")
            model_path = Model3DManager.generate_3d_model_from_multi_view(view_images)
            source_image = front_image
            
        else:
            # 单图模式
            image_path = request.form.get('image_path')
            if not image_path:
                return jsonify({'error': '缺少图片路径'}), 400
            
            if image_path.startswith('/uploads/'):
                image_path = image_path.replace('/uploads/', 'uploads/')
            
            print(f"🧊 开始生成3D模型（单图模式）: {image_path}")
            model_path = Model3DManager.generate_3d_model_from_image(image_path)
            source_image = image_path
        
        print(f"✅ 3D模型生成完成: {model_path}")
        
        # 转换为URL路径
        model_url = normalize_path_for_url(model_path)
        
        # 会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'source_image': source_image,
                'note': version_note,
                'multi_view': is_multi_view
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='model',
                file_path=model_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'model_url': model_url,
            'version_id': version_id,
            'message': '3D模型生成成功！'
        })
            
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@model3d_bp.route('/generate-3d-model-sam', methods=['POST'])
def generate_3d_model_sam():
    """使用SAM 3D从图片生成3D模型"""
    try:
        image_path = request.form.get('image_path')
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        # 使用Model3DManager生成
        model_path, engine_used = Model3DManager.generate_with_sam3d(image_path)
        
        # 转换为URL路径
        model_url = normalize_path_for_url(model_path.replace('models/', 'uploads/models/'))
        
        # 会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'source_image': image_path,
                'note': version_note,
                'engine': engine_used
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='model',
                file_path=model_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'model_url': model_url,
            'version_id': version_id,
            'engine': engine_used,
            'message': f'3D模型生成成功！(使用 {engine_used})'
        })
            
    except Exception as e:
        print(f"❌ SAM 3D模型生成错误: {str(e)}")
        # 尝试降级到Hunyuan3D
        try:
            print("🔄 尝试降级到Hunyuan3D...")
            model_path = Model3DManager.generate_3d_model_from_image(image_path)
            model_url = normalize_path_for_url(model_path.replace('models/', 'uploads/models/'))
            return jsonify({
                'success': True,
                'model_url': model_url,
                'engine': 'hunyuan3d',
                'message': '3D模型生成成功！(使用 Hunyuan3D 备用引擎)'
            })
        except Exception as fallback_error:
            print(f"❌ Hunyuan3D降级也失败: {str(fallback_error)}")
            return jsonify({'error': f'生成失败: {str(e)}'}), 500


@model3d_bp.route('/compare-3d-engines', methods=['POST'])
def compare_3d_engines():
    """同时使用SAM 3D和Hunyuan3D生成，让用户比较"""
    try:
        image_path = request.form.get('image_path')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        # 使用Model3DManager对比引擎
        results = Model3DManager.compare_engines(image_path)
        
        # 转换路径为URL
        for engine, result in results.items():
            if result.get('success') and 'model_path' in result:
                result['model_url'] = result['model_path'].replace('models/', '/models/')
                del result['model_path']
        
        # 检查是否至少有一个成功
        if not results['sam3d']['success'] and not results['hunyuan3d']['success']:
            return jsonify({
                'error': '两个引擎都失败了',
                'details': results
            }), 500
        
        return jsonify({
            'success': True,
            'results': results,
            'message': '3D引擎对比完成'
        })
            
    except Exception as e:
        print(f"❌ 3D引擎对比错误: {str(e)}")
        return jsonify({'error': f'对比失败: {str(e)}'}), 500
