"""创作相关API端点 - 支持图片、3D模型、视频生成"""
import os
import re
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

# 美术专业术语字典 - 用于日志记录和验证
# 注意：不再转换成英文，因为Gemini能很好理解中文
ART_TERMINOLOGY_MAPPING = {
    r'[一二三四五六七八九]头身比例': True,  # 用于检测，不转换
    r'[一二三四五六七八九]\.5头身比例': True,
    r'S型身材': True,
    r'A字身材': True,
    r'H字身材': True,
    r'梨形身材': True,
    r'沙漏型': True,
    r'矩形身材': True,
}

def enhance_art_terminology(prompt: str) -> str:
    """检测美术专业术语并记录日志
    不进行转换 - 保留原始中文，因为Gemini能很好理解中文术语
    """
    if not prompt:
        return prompt
    
    # 仅用于日志记录
    for pattern in ART_TERMINOLOGY_MAPPING.keys():
        if re.search(pattern, prompt, re.IGNORECASE):
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                print(f"   📚 检测到美术术语: {match.group(0)}")
    
    # 返回原始提示词，不做任何转换
    return prompt

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
    
    print("="*50, flush=True)
    print("🎨 /api/generate_image 被调用", flush=True)
    print(f"👤 用户: {current_user.nickname} (ID: {current_user.id})", flush=True)
    current_app.logger.info("="*50)
    current_app.logger.info("🎨 /api/generate_image 被调用")
    current_app.logger.info(f"👤 用户: {current_user.nickname} (ID: {current_user.id})")
    
    try:
        # 导入API（延迟导入以避免循环依赖）
        print("🔄 开始导入NanoBananaAPI...", flush=True)
        from api.nano_banana import NanoBananaAPI
        from api.prompt_translator import translate_prompt
        print("✅ NanoBananaAPI导入成功", flush=True)
        
        print(f"🎫 Token剩余: {current_user.image_token_remaining}", flush=True)
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
        pose_description = request.form.get('pose_description', '').strip()  # 自然语言姿态描述
        style = request.form.get('style', 'cute')
        color_preference = request.form.get('color_preference', 'colorful')
        aspect_ratio = request.form.get('aspect_ratio', '512x512')
        session_id = request.form.get('session_id') or str(uuid.uuid4())
        # 不再支持JSON模式，仅使用骨架图+prompt
        
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
        # 简化日志
        
        # 获取上传的骨架图（必须）
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
                    
                    # 验证图片有效性
                    if os.path.exists(uploaded_image_path):
                        file_size = os.path.getsize(uploaded_image_path)
                        print(f"   📊 文件大小: {file_size / 1024:.1f} KB")
                        
                        # 尝试验证图片格式
                        try:
                            from PIL import Image
                            img = Image.open(uploaded_image_path)
                            print(f"   📐 图片尺寸: {img.width} x {img.height}")
                            print(f"   🎨 图片模式: {img.mode}")
                            
                            # 检查图片是否包含内容（不全是黑色或白色）
                            pixels = list(img.getdata())
                            unique_colors = len(set(pixels))
                            print(f"   🌈 唯一颜色数: {unique_colors}")
                            if unique_colors <= 2:
                                print(f"   ⚠️ 警告：图片颜色过少，可能不是有效的OpenPose图")
                        except Exception as e:
                            print(f"   ⚠️ 图片验证失败: {str(e)}")
        
        # 如果没有上传新图片，但有session_id，尝试从之前的记录中获取
        if not uploaded_image_path and session_id:
            artwork = Artwork.query.filter_by(session_id=session_id).first()
            if artwork and artwork.original_sketch:
                uploaded_image_path = os.path.join(current_app.root_path, '..', 'uploads', artwork.original_sketch)
                uploaded_filename = artwork.original_sketch
                # 验证文件是否真实存在
                if os.path.exists(uploaded_image_path):
                    print(f"♻️ 使用已保存的图片: {uploaded_filename}")
                else:
                    print(f"⚠️ 数据库中的图片文件不存在: {uploaded_image_path}")
                    uploaded_image_path = None
                    uploaded_filename = None
        
        # 验证：必须提供提示词和骨架图
        if not prompt:
            print("❌ 缺少prompt")
            return jsonify({
                'success': False,
                'error': '请输入角色描述'
            }), 400
        
        if not uploaded_image_path:
            print("❌ 缺少骨架图")
            return jsonify({
                'success': False,
                'error': '请先绘制姿态骨架图'
            }), 400
        
        # 不需要默认prompt和临时画布，必须由用户提供骨架图
        
        try:
            # 调用AI生成图片
            print(f"🚀 调用NanoBanana API...")
            nano_api = NanoBananaAPI()
            print(f"   sketch_path: {uploaded_image_path}")
            print(f"   prompt: {prompt[:50] if prompt else '(无)'}...")
            
            # 获取temperature参数（用于控制生成的创意程度）
            # 对于action lesson，使用稍高的temperature以获得更丰富的效果（类似Gemini网站的默认行为）
            lesson_type = request.form.get('lesson', 'default')
            if request.form.get('temperature'):
                temperature = request.form.get('temperature')
            else:
                # action lesson默认使用1.5以获得更生动的效果
                temperature = '1.5' if lesson_type == 'action' else '1.0'
            try:
                temperature = float(temperature)
                temperature = max(0.0, min(2.0, temperature))  # nano banana允许到2.0
            except (ValueError, TypeError):
                temperature = 1.5 if lesson_type == 'action' else 1.0
            
            # 获取top_p参数（核采样 - 控制多样性）
            # 对于action lesson，使用稍低的top_p以获得更稳定的质量
            if request.form.get('top_p'):
                top_p = request.form.get('top_p')
            else:
                top_p = '0.85' if lesson_type == 'action' else '0.95'
            try:
                top_p = float(top_p)
                top_p = max(0.0, min(1.0, top_p))  # 限制在0.0-1.0之间
            except (ValueError, TypeError):
                top_p = 0.85 if lesson_type == 'action' else 0.95
            
            # 获取seed参数（用于控制随机性）
            seed = request.form.get('seed')
            if seed:
                try:
                    seed = int(seed)
                except (ValueError, TypeError):
                    seed = None
            
            print(f"   temperature: {temperature}, top_p: {top_p}, seed: {seed}")
            
            # 如果有姿态描述，优先使用（比空洞的“严格遵循”更有效）
            if pose_description:
                print(f"   姿态描述: {pose_description}")
                # 嵌入默认风格：素描、白色背景、现代中国人形象
                enhanced_prompt = (
                    f"Detailed pencil sketch of a modern Chinese person. Pose: {pose_description}. "
                    f"Use the provided hand-drawn pose as ground truth and match it exactly; all other details follow the prompt. "
                    f"Appearance: {prompt}. "
                    f"Style: fine shading and hatching technique, anatomically accurate. "
                    f"Background: pure white. "
                    f"IMPORTANT: Draw only the person, NO skeleton lines, NO bones, NO reference markers visible."
                )
                prompt = enhanced_prompt
                print(f"   增强提示词(素描风格): {prompt[:200]}...")
            else:
                # 如果没有姿态描述，为action lesson追加系统prompt
                if lesson_type == 'action':
                    action_system_prompt = (
                        "Use the hand-drawn pose as ground truth and match it exactly; all other details follow the prompt. "
                        "Modern Chinese character, full-body shot, colorful manga style, pure white background. "
                        "IMPORTANT: Draw only the person, no skeleton lines, no bones, no reference markers visible."
                    )
                    prompt = f"{prompt}. {action_system_prompt}"
                    print(f"   追加action系统prompt: {prompt[:200]}...")
                else:
                    # 如果没有姿态描述且不是action lesson，使用原有的空间引导语
                    spatial_guidance = (
                        "CRITICAL: The character's pose must EXACTLY match the provided color-coded OpenPose skeleton reference image. "
                        "Blue lines indicate LEFT limbs, orange/red lines indicate RIGHT limbs. "
                        "Character description: "
                    )
                    prompt = spatial_guidance + prompt
                    print(f"   使用默认引导语: {prompt[:200]}...")

            # 检测美术专业术语
            print(f"🎨 检测美术专业术语...")
            enhance_art_terminology(prompt)  # 仅用于日志，返回值不使用
            
            # *** 关键改变：优先使用中文，因为Gemini对中文的理解很好 ***
            has_chinese = prompt and any('\u4e00' <= c <= '\u9fff' for c in prompt)
            has_art_terms = any(re.search(pattern, prompt, re.IGNORECASE) for pattern in ART_TERMINOLOGY_MAPPING.keys())
            
            if has_art_terms:
                print(f"✅ 检测到美术术语，保留中文原文以获得最佳理解")
                print(f"   (Gemini能很好理解中文的几头身、身材等术语)")
            elif has_chinese and not has_art_terms:
                print(f"🌐 检测到中文但无美术术语，翻译为英文...")
                print(f"   原始: {prompt[:100]}...")
                try:
                    translated_prompt = translate_prompt(prompt)
                    print(f"   ✅ 翻译成功: {translated_prompt[:100]}...")
                    prompt = translated_prompt
                except Exception as e:
                    print(f"⚠️ 翻译失败，保留中文: {e}")
            else:
                print(f"✅ 已是英文，直接使用")
            
            print(f"📝 最终使用的提示词: {prompt[:150]}...")
            
            # 使用骨架图模式（Gemini 2.5 Flash Image需要图片输入）
            sketch_arg = uploaded_image_path

            result = nano_api.generate_image_from_reference(
                sketch_path=sketch_arg,
                description=prompt,
                style=style,
                aspect_ratio=aspect_ratio,
                temperature=temperature,
                top_p=top_p,
                seed=seed
            )
            current_app.logger.info(f"✅ API调用完成")
            
            if not result:
                current_app.logger.error(f"❌ API返回空结果（可能触发了内容过滤或网络问题）")
                print(f"⚠️ 提示：AI服务可能暂时不可用，请检查网络连接或稍后重试", flush=True)
                print(f"   sketch_arg: {sketch_arg}")
                return jsonify({
                    'success': False,
                    'error': 'AI服务返回空结果，可能是：1) 提示词被过滤 2) 网络问题 3) API配额耗尽',
                    'tip': '尝试修改提示词或稍后重试'
                }), 503
        except Exception as api_error:
            current_app.logger.error(f"❌ API调用异常: {str(api_error)}")
            print(f"❌ API调用异常详情: {type(api_error).__name__}: {str(api_error)}")
            import traceback
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'生成失败: {str(api_error)}',
                'tip': '请检查后台日志获取详细错误信息'
            }), 503
        
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
        
        print(f"📦 移动文件")
        print(f"   源文件: {colored_image_path}")
        print(f"   目标文件: {colored_filename}")
        print(f"   完整路径: {colored_dest}")
        
        current_app.logger.info(f"📦 移动文件: {colored_filename}")
        import shutil
        shutil.copy2(colored_image_path, colored_dest)
        
        # 验证目标文件是否正确保存
        if not os.path.exists(colored_dest):
            print(f"❌ 文件移动失败: {colored_dest}")
            current_app.logger.error(f"❌ 文件移动失败: {colored_dest}")
            return jsonify({
                'success': False,
                'error': '文件保存失败'
            }), 500
        
        # 验证文件大小
        file_size = os.path.getsize(colored_dest)
        print(f"✅ 文件已保存到uploads (大小: {file_size} bytes)")
        current_app.logger.info(f"✅ 文件已保存到uploads (大小: {file_size} bytes)")
        
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
        
        print("="*50, flush=True)
        print(f"❌❌❌ 严重错误!", flush=True)
        print(f"错误类型: {error_type}", flush=True)
        print(f"错误信息: {str(e)}", flush=True)
        print("="*50, flush=True)
        
        current_app.logger.error("="*50)
        current_app.logger.error(f"❌❌❌ 严重错误!")
        current_app.logger.error(f"错误类型: {error_type}")
        current_app.logger.error(f"错误信息: {str(e)}")
        current_app.logger.error("="*50)
        
        import traceback
        print(traceback.format_exc(), flush=True)
        current_app.logger.error(traceback.format_exc())
        
        # 区分错误类型
        status_code = 500
        user_error_msg = error_msg
        
        # 网络错误
        if 'Connection refused' in str(e) or 'refused' in str(e).lower():
            status_code = 503
            user_error_msg = 'AI服务暂时不可用，请检查网络连接或稍后重试'
        # API密钥错误
        elif 'api' in str(e).lower() or 'key' in str(e).lower():
            status_code = 503
            user_error_msg = 'AI服务配置错误，请联系管理员'
        # 超时
        elif 'timeout' in str(e).lower():
            status_code = 504
            user_error_msg = 'AI服务响应超时，请重试'
        
        return jsonify({
            'success': False,
            'error': user_error_msg,
            'error_type': error_type,
            'traceback': traceback.format_exc() if current_app.debug else None
        }), status_code


@api_create_bp.route('/api/load_image_from_url', methods=['POST'])
@login_required
def load_image_from_url():
    """从URL加载图片（用于粘贴图片链接）"""
    try:
        import base64
        from io import BytesIO

        import requests
        from PIL import Image
        
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'message': '请提供图片URL'
            }), 400
        
        current_app.logger.info(f"🔗 加载图片链接: {url}")
        
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 验证是否为图片
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return jsonify({
                'success': False,
                'message': '链接不是有效的图片'
            }), 400
        
        # 转换为base64
        img = Image.open(BytesIO(response.content))
        
        # 限制图片大小
        max_size = 2048
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 转换为PNG格式的base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        current_app.logger.info(f"✅ 图片加载成功，尺寸: {img.width}x{img.height}")
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{img_base64}'
        })
        
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"❌ 下载图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '无法下载图片，请检查链接是否有效'
        }), 400
    except Exception as e:
        current_app.logger.error(f"❌ 加载图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '加载图片失败'
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


@api_create_bp.route('/api/analyze-image-features', methods=['POST'])
@login_required
def analyze_image_features():
    """分析上传图片中的人物特征"""
    try:
        # 获取上传的图片
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到图片文件'
            }), 400
        
        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({
                'success': False,
                'error': '图片文件为空'
            }), 400
        
        # 保存临时文件
        session_id = str(uuid.uuid4())
        filename = save_uploaded_file(file, session_id, 'analyze')
        if not filename:
            return jsonify({
                'success': False,
                'error': '图片格式不支持'
            }), 400
        
        image_path = os.path.join(current_app.root_path, '..', 'uploads', filename)
        
        try:
            # 使用Gemini Vision API分析图片特征
            import google.generativeai as genai
            from PIL import Image

            # 读取图片
            img = Image.open(image_path)
            
            # 配置Gemini API
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise Exception('GEMINI_API_KEY未配置')
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # 提示词：提取人物特征
            prompt = """请仔细观察这张图片中的人物，用简洁的中文描述以下特征（如果图片中没有人物，请说明）：

1. 性别和年龄段（如：男孩、女孩、青年、中年等）
2. 发型（如：长发、短发、卷发、直发、马尾、光头等）
3. 头发颜色（如果能看出）
4. 脸型（如：圆脸、长脸、方脸等）
5. 眼睛特征（如：大眼睛、小眼睛、单眼皮、双眼皮等）
6. 鼻子特征（如：高鼻梁、塌鼻梁、小鼻子等）
7. 嘴巴特征（如：大嘴、小嘴、厚嘴唇、薄嘴唇等）
8. 是否戴眼镜
9. 特殊配饰（如：帽子、耳环、项链等）
10. 衣着风格（简要描述）

请用逗号分隔的短语形式输出，例如：
"10岁男孩，短发，圆脸，大眼睛，高鼻梁，小嘴，不戴眼镜，穿蓝色T恤"

只输出特征描述，不要其他解释。"""
            
            # 调用API
            response = model.generate_content([prompt, img])
            features = response.text.strip()
            
            print(f"✅ 提取的人物特征: {features}")
            
            return jsonify({
                'success': True,
                'features': features
            })
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(image_path):
                    os.unlink(image_path)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        
    except Exception as e:
        current_app.logger.error(f"分析图片特征失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500
