"""创作相关API端点 - 支持图片、3D模型、视频生成"""
import os
import uuid
from datetime import datetime

from flask import Blueprint, current_app, flash, jsonify, request, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from auth.models import Artwork, db

api_create_bp = Blueprint('api_create', __name__)

# 允许的图片文件扩展名
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def save_uploaded_file(file, session_id=None, file_type='upload'):
    """保存上传的文件到uploads目录"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{file_type}_{uuid.uuid4().hex}.{ext}"
    
    # 保存到uploads目录
    uploads_dir = os.path.join(current_app.root_path, '..', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    filepath = os.path.join(uploads_dir, filename)
    file.save(filepath)
    
    return filename

def get_or_create_artwork(session_id, user_id, title=None):
    """获取或创建Artwork记录"""
    artwork = Artwork.query.filter_by(session_id=session_id).first()
    
    if not artwork:
        artwork = Artwork(
            session_id=session_id,
            title=title or f"创作_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id
        )
        db.session.add(artwork)
        db.session.commit()
    
    return artwork


@api_create_bp.route('/api/generate_image', methods=['POST'])
@login_required
def generate_image():
    """生成图片 - 支持文字描述或图片上传"""
    import sys
    sys.stdout.flush()
    
    current_app.logger.info("="*50)
    current_app.logger.info("🎨 /api/generate_image 被调用")
    current_app.logger.info(f"👤 用户: {current_user.nickname} (ID: {current_user.id})")
    
    try:
        # 导入API（延迟导入以避免循环依赖）
        from api.nano_banana import NanoBananaAPI
        
        current_app.logger.info(f"🎫 Token剩余: {current_user.image_token_remaining}")

        # 检查token剩余
        if current_user.image_token_remaining <= 0 and current_user.role not in ['teacher', 'admin']:
            print("❌ Token不足")
            return jsonify({
                'success': False,
                'error': 'Token不足，请联系教师充值'
            }), 403
        
        # 获取参数
        prompt = request.form.get('prompt', '').strip()
        style = request.form.get('style', 'cute')
        color_preference = request.form.get('color_preference', 'colorful')
        aspect_ratio = request.form.get('aspect_ratio', '512x512')
        session_id = request.form.get('session_id') or str(uuid.uuid4())
        
        # 根据用户角色设置默认 style：管理员、老师为 none，其他为 cute
        if not request.form.get('style'):  # 如果前端没有传 style
            if current_user.role in ['admin', 'teacher']:
                style = 'none'
            else:
                style = 'cute'
        
        print(f"📝 参数:")
        print(f"   prompt: {prompt[:50] if prompt else '(无)'}...")
        print(f"   style: {style} (用户角色: {current_user.role})")
        print(f"   aspect_ratio: {aspect_ratio}")
        print(f"   session_id: {session_id}")
        
        # 获取上传的图片（可选）
        uploaded_image_path = None
        uploaded_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                print(f"📤 上传文件: {file.filename}")
                uploaded_filename = save_uploaded_file(file, session_id, 'original')
                if uploaded_filename:
                    uploaded_image_path = os.path.join(current_app.root_path, '..', 'uploads', uploaded_filename)
                    print(f"✅ 文件已保存: {uploaded_filename}")
        
        # 验证：必须有prompt或上传图片
        if not prompt and not uploaded_image_path:
            print("❌ 缺少prompt和图片")
            return jsonify({
                'success': False,
                'error': '请输入文字描述或上传图片'
            }), 400
        
        # 如果只有prompt没有图片，创建一个临时白色画布作为基础
        if prompt and not uploaded_image_path:
            print("🎨 创建临时白色画布（仅文字模式）")
            import tempfile

            from PIL import Image

            # 创建临时白色画布
            temp_img = Image.new('RGB', (512, 512), 'white')
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_img.save(temp_file.name)
            temp_file.close()
            uploaded_image_path = temp_file.name
            
            # 标记为临时文件，稍后删除
            temp_file_to_delete = temp_file.name
            print(f"✅ 临时文件创建: {temp_file.name}")
        else:
            temp_file_to_delete = None
        
        try:
            # 调用AI生成图片
            print(f"🚀 调用NanoBanana API...")
            nano_api = NanoBananaAPI()
            print(f"   sketch_path: {uploaded_image_path}")
            print(f"   prompt: {prompt[:50] if prompt else '(无)'}...")
            
            result = nano_api.generate_image_from_reference(
                sketch_path=uploaded_image_path,
                description=prompt,
                style=style,
                aspect_ratio=aspect_ratio
            )
            current_app.logger.info(f"✅ API调用完成")
            
            if not result:
                current_app.logger.error(f"❌ API返回空结果")
                return jsonify({
                    'success': False,
                    'error': '图片生成失败，请稍后重试'
                }), 400
        finally:
            # 清理临时文件
            if temp_file_to_delete and os.path.exists(temp_file_to_delete):
                try:
                    os.unlink(temp_file_to_delete)
                    print(f"🗑️ 临时文件已删除: {temp_file_to_delete}")
                except Exception as e:
                    print(f"⚠️ 删除临时文件失败: {e}")
        
        # result现在是图片路径字符串
        colored_image_path = result
        current_app.logger.info(f"📸 生成图片路径: {colored_image_path}")
        
        if not colored_image_path or not os.path.exists(colored_image_path):
            current_app.logger.error(f"❌ 图片文件未找到!")
            current_app.logger.error(f"   路径: {colored_image_path}")
            return jsonify({
                'success': False,
                'error': '生成的图片文件未找到'
            }), 500
        
        # 移动文件到uploads目录
        colored_filename = f"colored_{uuid.uuid4().hex}.png"
        uploads_dir = os.path.join(current_app.root_path, '..', 'uploads')
        colored_dest = os.path.join(uploads_dir, colored_filename)
        
        current_app.logger.info(f"📦 移动文件: {colored_filename}")
        import shutil
        shutil.copy2(colored_image_path, colored_dest)
        current_app.logger.info(f"✅ 文件已保存到uploads")
        
        # 创建或更新Artwork记录
        current_app.logger.info(f"💾 更新数据库: session_id={session_id}")
        artwork = get_or_create_artwork(
            session_id=session_id,
            user_id=current_user.id
        )
        
        # 更新artwork信息
        artwork.colored_image = colored_filename
        if uploaded_filename:
            artwork.original_sketch = uploaded_filename
        artwork.style_type = style
        artwork.color_preference = color_preference
        if prompt:
            artwork.prompt_text = prompt
        
        # 初始化版本历史
        if not artwork.all_colored_versions:
            artwork.all_colored_versions = []
        artwork.all_colored_versions.append(colored_filename)
        
        db.session.commit()
        
        # 扣除token（教师和管理员不扣）
        if current_user.role not in ['teacher', 'admin']:
            current_user.image_token_remaining -= 1
            db.session.commit()
            current_app.logger.info(f"💰 Token已扣除，剩余: {current_user.image_token_remaining}")
        
        current_app.logger.info(f"🎉 图片生成成功!")
        current_app.logger.info(f"   session_id: {session_id}")
        current_app.logger.info(f"   image_url: /uploads/{colored_filename}")
        current_app.logger.info("="*50)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'image_url': f"/uploads/{colored_filename}",
            'remaining_tokens': current_user.image_token_remaining
        })
        
    except Exception as e:
        error_msg = f"生成图片失败: {str(e)}"
        error_type = type(e).__name__
        
        current_app.logger.error("="*50)
        current_app.logger.error(f"❌❌❌ 严重错误!")
        current_app.logger.error(f"错误类型: {error_type}")
        current_app.logger.error(f"错误信息: {str(e)}")
        current_app.logger.error("="*50)
        
        import traceback
        current_app.logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'error_type': error_type,
            'traceback': traceback.format_exc() if current_app.debug else None
        }), 500


@api_create_bp.route('/api/adjust_image', methods=['POST'])
@login_required
def adjust_image():
    """快速调整图片（更亮、更鲜艳、更柔和）"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        adjustment_type = data.get('adjustment_type')  # brighter, vibrant, soft
        
        if not session_id or not adjustment_type:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        # 获取artwork
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        # 调用图片调整API（这里需要实现具体的图片处理逻辑）
        # 暂时返回模拟数据
        import io

        from PIL import Image, ImageEnhance

        # 读取当前图片
        current_image_path = os.path.join(current_app.root_path, '..', 'uploads', artwork.colored_image)
        img = Image.open(current_image_path)
        
        # 根据调整类型进行处理
        if adjustment_type == 'brighter':
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.3)
        elif adjustment_type == 'vibrant':
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.5)
        elif adjustment_type == 'soft':
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(0.8)
        
        # 保存调整后的图片
        adjusted_filename = f"adjusted_{uuid.uuid4().hex}.png"
        adjusted_path = os.path.join(current_app.root_path, '..', 'uploads', adjusted_filename)
        img.save(adjusted_path)
        
        # 更新artwork
        artwork.colored_image = adjusted_filename
        if not artwork.all_adjusted_versions:
            artwork.all_adjusted_versions = []
        artwork.all_adjusted_versions.append(adjusted_filename)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'image_url': f"/uploads/{adjusted_filename}"
        })
        
    except Exception as e:
        current_app.logger.error(f"调整图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'调整失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/save_artwork', methods=['POST'])
@login_required
def save_artwork():
    """保存作品到数据库"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少session_id'
            }), 400
        
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        # 更新状态为已完成
        if artwork.status == 'draft':
            artwork.status = 'completed'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已保存'
        })
        
    except Exception as e:
        current_app.logger.error(f"保存作品失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/generate_3d', methods=['POST'])
@login_required
def generate_3d():
    """基于session生成3D模型"""
    try:
        # 导入API
        from api.hunyuan3d import Hunyuan3DGenerator

        # 检查权限
        if not current_user.can_use_3d_model():
            return jsonify({
                'success': False,
                'error': '您暂无3D建模权限，请报名课程'
            }), 403
        
        data = request.get_json()
        session_id = data.get('session_id')
        quality = data.get('quality', 'fast')  # fast or high
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少session_id'
            }), 400
        
        # 获取artwork
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        if not artwork.colored_image:
            return jsonify({
                'success': False,
                'error': '请先生成2D图片'
            }), 400
        
        # 调用3D生成API
        image_path = os.path.join(current_app.root_path, '..', 'uploads', artwork.colored_image)
        
        generator = Hunyuan3DGenerator()
        api_version = 'rapid' if quality == 'fast' else 'pro'
        result = generator.generate_3d_model(
            image_path=image_path,
            session_id=session_id,
            api_version=api_version
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', '3D模型生成失败')
            }), 500
        
        # 保存模型文件路径（相对于uploads目录）
        model_path = result.get('model_path')
        if model_path and os.path.exists(model_path):
            # 提取文件名
            model_filename = os.path.basename(model_path)
            artwork.model_3d = model_filename
            db.session.commit()
            
            return jsonify({
                'success': True,
                'model_url': f"/uploads/3d_models/{model_filename}",
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '模型文件保存失败'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"生成3D模型失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/generate_3d_direct', methods=['POST'])
@login_required
def generate_3d_direct():
    """独立生成3D模型（教师/管理员）"""
    try:
        # 导入API
        from api.hunyuan3d import Hunyuan3DGenerator
        from api.nano_banana import NanoBananaAPI

        # 检查权限
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({
                'success': False,
                'error': '需要教师或管理员权限'
            }), 403
        
        # 获取参数
        prompt = request.form.get('prompt', '').strip()
        quality = request.form.get('quality', 'fast')
        session_id = str(uuid.uuid4())
        
        # 获取上传的图片（可选）
        uploaded_image_path = None
        uploaded_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                uploaded_filename = save_uploaded_file(file, session_id, 'model_input')
                if uploaded_filename:
                    uploaded_image_path = os.path.join(current_app.root_path, '..', 'uploads', uploaded_filename)
        
        # 验证：必须有prompt或图片
        if not prompt and not uploaded_image_path:
            return jsonify({
                'success': False,
                'error': '请输入文字描述或上传图片'
            }), 400
        
        # 如果有prompt，先生成图片
        if prompt:
            nano_api = NanoBananaAPI()
            result = nano_api.generate_image_from_reference(
                sketch_path='dummy.png',
                description=prompt,
                style='model_3d',  # 使用3D模型专用风格
                aspect_ratio='512x512'
            )
            if not result.get('success'):
                return jsonify({
                    'success': False,
                    'error': '图片生成失败'
                }), 500
            
            # 移动生成的图片
            colored_image_path = result.get('image_path')
            image_filename = f"3d_input_{uuid.uuid4().hex}.png"
            uploads_dir = os.path.join(current_app.root_path, '..', 'uploads')
            image_dest = os.path.join(uploads_dir, image_filename)
            
            import shutil
            shutil.copy2(colored_image_path, image_dest)
            image_path = image_dest
        else:
            image_filename = uploaded_filename
            image_path = uploaded_image_path
        
        # 生成3D模型
        generator = Hunyuan3DGenerator()
        api_version = 'rapid' if quality == 'fast' else 'pro'
        result = generator.generate_3d_model(
            image_path=image_path,
            session_id=session_id,
            api_version=api_version
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', '3D模型生成失败')
            }), 500
        
        # 创建artwork记录
        artwork = get_or_create_artwork(
            session_id=session_id,
            user_id=current_user.id,
            title=f"3D模型_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        artwork.colored_image = image_filename
        
        # 保存模型文件路径
        model_path = result.get('model_path')
        if model_path and os.path.exists(model_path):
            model_filename = os.path.basename(model_path)
            artwork.model_3d = model_filename
        
        if prompt:
            artwork.prompt_text = prompt
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'model_url': f"/uploads/3d_models/{model_filename}" if model_path else None,
            'session_id': session_id
        })
        
    except Exception as e:
        current_app.logger.error(f"独立生成3D模型失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/generate_video', methods=['POST'])
@login_required
def generate_video():
    """基于session生成视频"""
    try:
        # 导入API
        from api.veo31 import Veo31API

        # 检查权限
        if not current_user.can_use_video_generation():
            return jsonify({
                'success': False,
                'error': '您暂无视频生成权限，请报名课程'
            }), 403
        
        data = request.get_json()
        session_id = data.get('session_id')
        prompt = data.get('prompt', '').strip()
        aspect_ratio = data.get('aspect_ratio', '16:9')
        duration = int(data.get('duration', 5))
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少session_id'
            }), 400
        
        # 获取artwork
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        if not artwork.colored_image:
            return jsonify({
                'success': False,
                'error': '请先生成2D图片'
            }), 400
        
        # 调用视频生成API
        image_url = f"/uploads/{artwork.colored_image}"
        
        veo_api = Veo31API()
        result = veo_api.generate_video(
            image_url=image_url,
            prompt=prompt or "让图片动起来",
            duration=duration,
            aspect_ratio=aspect_ratio
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', '视频生成失败')
            }), 500
        
        # 保存视频文件信息
        video_url = result.get('video_url')
        if video_url:
            # 提取文件名（假设返回的是相对路径）
            video_filename = os.path.basename(video_url)
            artwork.video_file = video_filename
            artwork.video_prompt = prompt
            artwork.video_aspect_ratio = aspect_ratio
            db.session.commit()
            
            return jsonify({
                'success': True,
                'video_url': video_url,
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '视频文件保存失败'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"生成视频失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/generate_video_direct', methods=['POST'])
@login_required
def generate_video_direct():
    """独立生成视频（教师/管理员）"""
    try:
        # 导入API
        from api.nano_banana import NanoBananaAPI
        from api.veo31 import Veo31API

        # 检查权限
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({
                'success': False,
                'error': '需要教师或管理员权限'
            }), 403
        
        # 获取参数
        prompt = request.form.get('prompt', '').strip()
        aspect_ratio = request.form.get('aspect_ratio', '16:9')
        duration = int(request.form.get('duration', 5))
        session_id = str(uuid.uuid4())
        
        # 获取上传的图片（可选）
        uploaded_image_path = None
        uploaded_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                uploaded_filename = save_uploaded_file(file, session_id, 'video_input')
                if uploaded_filename:
                    uploaded_image_path = os.path.join(current_app.root_path, '..', 'uploads', uploaded_filename)
        
        # 验证：必须有prompt或图片
        if not prompt and not uploaded_image_path:
            return jsonify({
                'success': False,
                'error': '请输入文字描述或上传图片'
            }), 400
        
        # 如果有图片上传，使用上传的图片
        if uploaded_image_path:
            image_filename = uploaded_filename
            image_url = f"/uploads/{uploaded_filename}"
        # 否则，先生成图片
        elif prompt:
            nano_api = NanoBananaAPI()
            result = nano_api.generate_image_from_reference(
                sketch_path='dummy.png',
                description=prompt,
                style='cute',
                aspect_ratio='512x512'
            )
            if not result.get('success'):
                return jsonify({
                    'success': False,
                    'error': '图片生成失败'
                }), 500
            
            # 移动生成的图片
            colored_image_path = result.get('image_path')
            image_filename = f"video_input_{uuid.uuid4().hex}.png"
            uploads_dir = os.path.join(current_app.root_path, '..', 'uploads')
            image_dest = os.path.join(uploads_dir, image_filename)
            
            import shutil
            shutil.copy2(colored_image_path, image_dest)
            image_url = f"/uploads/{image_filename}"
        
        # 生成视频
        veo_api = Veo31API()
        result = veo_api.generate_video(
            image_url=image_url,
            prompt=prompt or "让图片动起来",
            duration=duration,
            aspect_ratio=aspect_ratio
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', '视频生成失败')
            }), 500
        
        # 创建artwork记录
        artwork = get_or_create_artwork(
            session_id=session_id,
            user_id=current_user.id,
            title=f"视频_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        artwork.colored_image = image_filename
        
        # 保存视频文件信息
        video_url = result.get('video_url')
        if video_url:
            video_filename = os.path.basename(video_url)
            artwork.video_file = video_filename
        
        artwork.video_prompt = prompt
        artwork.video_aspect_ratio = aspect_ratio
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'video_url': video_url,
            'session_id': session_id
        })
        
    except Exception as e:
        current_app.logger.error(f"独立生成视频失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'生成失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/finalize_artwork', methods=['POST'])
@login_required
def finalize_artwork():
    """完成作品并标记为已完成"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少session_id'
            }), 400
        
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        # 更新状态为已完成
        artwork.status = 'completed'
        artwork.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已完成',
            'redirect_url': '/gallery'
        })
        
    except Exception as e:
        current_app.logger.error(f"完成作品失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/download_model/<session_id>')
@login_required
def download_model(session_id):
    """下载3D模型文件"""
    try:
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        if not artwork.model_3d:
            return jsonify({
                'success': False,
                'error': '该作品没有3D模型'
            }), 404
        
        model_path = os.path.join(current_app.root_path, '..', 'uploads', artwork.model_3d)
        if not os.path.exists(model_path):
            return jsonify({
                'success': False,
                'error': '模型文件不存在'
            }), 404
        
        return send_file(
            model_path,
            as_attachment=True,
            download_name=f"model_{session_id}.glb",
            mimetype='model/gltf-binary'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'下载失败: {str(e)}'
        }), 500


@api_create_bp.route('/api/download_video/<session_id>')
@login_required
def download_video(session_id):
    """下载视频文件"""
    try:
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': '未找到作品或无权限'
            }), 403
        
        if not artwork.video_file:
            return jsonify({
                'success': False,
                'error': '该作品没有视频'
            }), 404
        
        video_path = os.path.join(current_app.root_path, '..', 'uploads', artwork.video_file)
        if not os.path.exists(video_path):
            return jsonify({
                'success': False,
                'error': '视频文件不存在'
            }), 404
        
        return send_file(
            video_path,
            as_attachment=True,
            download_name=f"video_{session_id}.mp4",
            mimetype='video/mp4'
        )
        
    except Exception as e:
        current_app.logger.error(f"下载视频失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'下载失败: {str(e)}'
        }), 500
