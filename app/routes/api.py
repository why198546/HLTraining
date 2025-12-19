"""API路由（所有/api/*路由）"""
import json
import os
import re
import shutil
import traceback
import uuid
from datetime import datetime
from io import BytesIO

import cv2
import google.generativeai as genai
import numpy as np
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename

# 导入API模块
from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_prompt
from api.sam3d_api import SAM3DAPI
from app.config import Config
from app.utils import allowed_file, normalize_path_for_url, preprocess_sketch
# 导入数据库和模型
from auth.models import (Artwork, ArtworkView, ArtworkVote, CanvasProject,
                         User, db)
# 导入managers
from managers.creation_session_manager import CreationSessionManager

api_bp = Blueprint('api', __name__)

# 初始化managers
session_manager = CreationSessionManager()

# ========== 画布相关API ==========

@api_bp.route('/canvas/generate', methods=['POST'])
@login_required
def canvas_generate():
    """画布图片生成API"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': '请输入描述'
            }), 400
        
        print(f"🎨 画布生成请求: {prompt}")
        
        # 如果提示词中包含人物但未指定国籍，默认添加"中国人形象"
        has_nationality = bool(re.search(r'外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾', prompt, re.IGNORECASE))
        has_person = bool(re.search(r'人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师', prompt))
        
        if not has_nationality and has_person and '中国' not in prompt:
            prompt = '中国人形象，' + prompt
            print(f"✅ 自动添加中国人形象，新提示词: {prompt}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 生成图片
        generated_image_path = nano_banana.generate_image_from_text(
            prompt, 
            style='realistic',
            color_preference='colorful',
            expert_mode=False,
            aspect_ratio='1:1'
        )
        
        if not generated_image_path:
            return jsonify({
                'success': False,
                'error': '图片生成失败'
            }), 500
        
        # 转换为URL路径
        image_url = normalize_path_for_url(generated_image_path)
        
        print(f"✅ 图片生成成功: {image_url}")
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'prompt': prompt
        })
        
    except Exception as e:
        print(f"❌ 画布生成错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/chat', methods=['POST'])
@login_required
def canvas_chat():
    """画布对话API - 判断用户意图"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        selected_image_index = data.get('selectedImageIndex')
        has_images = data.get('hasImages', False)
        forced_intent = data.get('forcedIntent')  # 命令模式强制的意图
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': '请输入内容'
            }), 400
        
        print(f"💬 画布对话: {prompt}, 选中图片: {selected_image_index}, 有图片: {has_images}, 强制意图: {forced_intent}")
        
        # 如果有强制意图，直接使用
        if forced_intent:
            intent = forced_intent
            refined_prompt = prompt
            
            if intent == 'generate':
                response = '好的，我来为你生成图片...'
            elif intent == 'modify':
                response = '好的，我来帮你修改这张图片...'
            elif intent == 'chat':
                # 简单的对话响应 - 对话模式下不生成图片
                prompt_lower = prompt.lower()
                if '建议' in prompt_lower or '技巧' in prompt_lower:
                    response = '创作建议：\n1. 描述要具体，包含主体、环境、光线、风格等\n2. 可以参考艺术家风格，如"梵高风格"、"水彩画风格"\n3. 想修改图片时，先选中它再告诉我改什么'
                elif '教程' in prompt_lower or '怎么' in prompt_lower:
                    response = '使用方法：\n📝 生成新图：直接描述想要的图片，如"画一只松鼠"\n✨ 修改图片：单击选中图片，然后说"换成夜晚场景"\n💬 对话交流：问我任何创作相关的问题\n⚡ 快捷命令：输入 / 可以快速切换模式'
                elif '谢谢' in prompt_lower or '感谢' in prompt_lower:
                    response = '不客气！很高兴能帮到你 😊 还需要什么帮助吗？'
                elif any(kw in prompt_lower for kw in ['画', '生成', '创作', '做一个', '做一张']):
                    # 对话模式下，即使提到生成关键词，也只是对话
                    response = f'我理解你想要生成："{prompt}"。\n\n💡 提示：当前是对话模式，我不会生成图片。如果要生成图片，可以：\n1. 输入 / 选择"生成"模式\n2. 或者退出对话模式，直接描述你想要的图片'
                else:
                    response = f'关于"{prompt}"的问题，我很乐意为你解答。你可以问我创作技巧、工具使用等问题。\n\n如果想生成图片，可以输入 / 切换到生成模式。'
            
            return jsonify({
                'success': True,
                'intent': intent,
                'refined_prompt': refined_prompt,
                'response': response
            })
        
        # 使用简单的关键词匹配判断意图（原有逻辑）
        # 修改意图的关键词
        modify_keywords = ['修改', '改成', '换', '变成', '调整', '优化', '改进', '让它', '把它', '更', '加上', '去掉', '删除', '移除']
        
        # 生成意图的关键词
        generate_keywords = ['画', '生成', '创作', '做一个', '做一张', '帮我', '我想要', '给我', '设计', '制作']
        
        # 对话意图的关键词
        chat_keywords = ['什么', '为什么', '怎么', '如何', '能不能', '可以吗', '建议', '技巧', '教程', '帮助', '说明', '?', '？']
        
        prompt_lower = prompt.lower()
        
        # 判断意图
        intent = 'chat'  # 默认为对话
        refined_prompt = prompt
        response = ''
        
        # 检查是否选中了图片且包含修改关键词
        if selected_image_index is not None and any(kw in prompt_lower for kw in modify_keywords):
            intent = 'modify'
            response = '好的，我来帮你修改这张图片...'
        # 检查是否包含生成关键词
        elif any(kw in prompt_lower for kw in generate_keywords):
            intent = 'generate'
            response = '好的，我来为你生成图片...'
        # 检查是否包含明确的对话关键词
        elif any(kw in prompt_lower for kw in chat_keywords):
            intent = 'chat'
            # 根据不同的问题给出不同的回答
            if '建议' in prompt_lower or '技巧' in prompt_lower:
                response = '创作建议：\n1. 描述要具体，包含主体、环境、光线、风格等\n2. 可以参考艺术家风格，如"梵高风格"、"水彩画风格"\n3. 想修改图片时，先选中它再告诉我改什么'
            elif '教程' in prompt_lower or '怎么' in prompt_lower:
                response = '使用方法：\n📝 生成新图：直接描述想要的图片\n✨ 修改图片：单击选中图片，然后说出修改要求\n💬 对话交流：问我任何问题'
            else:
                response = '我会尽力回答你的问题。如果想生成图片，可以直接描述你想要的内容。'
        
        return jsonify({
            'success': True,
            'intent': intent,
            'refined_prompt': refined_prompt,
            'response': response
        })
        
    except Exception as e:
        print(f"❌ 画布对话错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/modify', methods=['POST'])
@login_required
def canvas_modify():
    """画布图片修改API"""
    try:
        data = request.get_json()
        image_url = data.get('image_url', '').strip()
        original_prompt = data.get('original_prompt', '').strip()
        instruction = data.get('instruction', '').strip()
        
        if not image_url or not instruction:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        print(f"✨ 修改图片请求: {instruction}")
        
        # 将URL路径转换为文件路径
        if image_url.startswith('/uploads/'):
            image_path = 'uploads' + image_url[8:]
        else:
            image_path = image_url.replace('/uploads/', 'uploads/')
        
        # 构建新的提示词
        new_prompt = f"{original_prompt}，{instruction}"
        
        print(f"📝 原提示词: {original_prompt}")
        print(f"📝 新提示词: {new_prompt}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 使用图片+文字生成模式
        generated_image_path = nano_banana.generate_image_from_sketch_and_text(
            image_path,
            new_prompt,
            style='realistic',
            color_preference='colorful',
            expert_mode=False,
            aspect_ratio='1:1'
        )
        
        if not generated_image_path:
            return jsonify({
                'success': False,
                'error': '图片修改失败'
            }), 500
        
        # 转换为URL路径
        new_image_url = normalize_path_for_url(generated_image_path)
        
        print(f"✅ 图片修改成功: {new_image_url}")
        
        return jsonify({
            'success': True,
            'image_url': new_image_url,
            'new_prompt': new_prompt
        })
        
    except Exception as e:
        print(f"❌ 修改错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 画布项目管理 API ==========

@api_bp.route('/canvas/projects', methods=['GET'])
@login_required
def get_canvas_projects():
    """获取用户的所有画布项目"""
    try:
        projects = CanvasProject.query.filter_by(
            user_id=current_user.id,
            is_deleted=False
        ).order_by(CanvasProject.last_accessed.desc()).all()
        
        return jsonify({
            'success': True,
            'projects': [p.to_dict() for p in projects]
        })
    except Exception as e:
        print(f"❌ 获取项目列表错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/projects/create', methods=['POST'])
@login_required
def create_canvas_project():
    """创建新的画布项目"""
    try:
        data = request.get_json()
        title = data.get('title', '未命名项目')
        
        project_id = str(uuid.uuid4())
        project = CanvasProject(
            project_id=project_id,
            user_id=current_user.id,
            title=title
        )
        
        db.session.add(project)
        db.session.commit()
        
        print(f"✅ 创建画布项目: {project_id} - {title}")
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ 创建项目错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/projects/<project_id>', methods=['GET'])
@login_required
def get_canvas_project(project_id):
    """获取特定画布项目"""
    try:
        project = CanvasProject.query.filter_by(
            project_id=project_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not project:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404
        
        # 更新最后访问时间
        project.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        print(f"❌ 获取项目错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/projects/<project_id>', methods=['PUT'])
@login_required
def update_canvas_project(project_id):
    """更新画布项目"""
    try:
        project = CanvasProject.query.filter_by(
            project_id=project_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not project:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新标题
        if 'title' in data:
            project.title = data['title']
        
        # 更新描述
        if 'description' in data:
            project.description = data['description']
        
        # 更新画布数据
        if 'canvas_data' in data:
            project.update_canvas_data(data['canvas_data'])
        
        # 更新缩略图
        if 'thumbnail' in data:
            project.thumbnail = data['thumbnail']
        
        db.session.commit()
        
        print(f"✅ 更新画布项目: {project_id}")
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新项目错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/projects/<project_id>', methods=['DELETE'])
@login_required
def delete_canvas_project(project_id):
    """删除画布项目（软删除）"""
    try:
        project = CanvasProject.query.filter_by(
            project_id=project_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not project:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404
        
        project.is_deleted = True
        db.session.commit()
        
        print(f"✅ 删除画布项目: {project_id}")
        
        return jsonify({
            'success': True,
            'message': '项目已删除'
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ 删除项目错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/canvas/projects/<project_id>/chat', methods=['POST'])
@login_required
def add_canvas_chat_message(project_id):
    """添加对话消息到项目"""
    try:
        project = CanvasProject.query.filter_by(
            project_id=project_id,
            user_id=current_user.id,
            is_deleted=False
        ).first()
        
        if not project:
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404
        
        data = request.get_json()
        role = data.get('role', 'user')  # 'user' or 'assistant'
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        project.add_chat_message(role, content, metadata)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '对话已保存'
        })
    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存对话错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== 3D模型相关API ==========

@api_bp.route('/sam3d/info')
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


# ========== 作品保存和管理API ==========

@api_bp.route('/save-artwork', methods=['POST'])
@login_required
def save_artwork():
    """从创作会话保存作品到数据库"""
    try:
        data = request.get_json()
        print(f"📨 收到保存作品请求: {data}")
        
        # 验证必需的参数
        session_id = data.get('session_id')
        print(f"🔍 会话ID: {session_id}")
        
        if not session_id:
            print("❌ 缺少会话ID")
            return jsonify({'error': '缺少会话ID'}), 400
        
        # 获取会话的所有版本历史
        print(f"🔄 获取会话 {session_id} 的所有版本...")
        session_folder = f"creation_sessions/{session_id}"
        
        # 从会话文件夹获取所有文件
        all_files = {
            'original_sketch': None,
            'colored_images': [],
            'adjusted_images': [],
            'model_3d': None,
            'video_file': None
        }
        
        if os.path.exists(session_folder):
            files_in_folder = sorted(os.listdir(session_folder))
            
            for filename in files_in_folder:
                if filename.startswith('.'):  # 跳过隐藏文件
                    continue
                    
                file_path = os.path.join(session_folder, filename)
                file_lower = filename.lower()
                
                # 原始简笔画 - 上传的或手绘的
                if 'upload' in file_lower or 'sketch' in file_lower or 'original' in file_lower:
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        all_files['original_sketch'] = filename
                
                # 调整后的图片（包含'adjusted'关键字）
                elif 'adjusted' in file_lower:
                    all_files['adjusted_images'].append(filename)
                
                # AI生成的图片（包含'colored', 'generated', 或时间戳格式）
                elif any(keyword in file_lower for keyword in ['colored', 'generated', 'image_']):
                    all_files['colored_images'].append(filename)
                
                # 如果是普通的PNG/JPG但不属于以上类别，也算作生成图片
                elif filename.endswith(('.png', '.jpg', '.jpeg')):
                    # 排除明确标记为其他类型的文件
                    if not any(x in file_lower for x in ['model', 'thumbnail']):
                        all_files['colored_images'].append(filename)
                
                # 3D模型
                elif filename.endswith(('.glb', '.obj', '.fbx', '.gltf')):
                    all_files['model_3d'] = filename
                
                # 视频文件
                elif filename.endswith(('.mp4', '.mov', '.avi')):
                    all_files['video_file'] = filename
        
        # 对列表排序（按文件名，通常包含时间戳）
        all_files['colored_images'].sort()
        all_files['adjusted_images'].sort()
        
        print(f"📂 找到的文件:")
        print(f"   原始简笔画: {all_files['original_sketch']}")
        print(f"   生成图片: {all_files['colored_images']}")
        print(f"   调整图片: {all_files['adjusted_images']}")
        print(f"   3D模型: {all_files['model_3d']}")
        print(f"   视频: {all_files['video_file']}")
        
        # 获取或创建作品记录
        artwork = Artwork.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        is_new = False
        if not artwork:
            artwork = Artwork(
                user_id=current_user.id,
                session_id=session_id,
                title=data.get('title', '未命名作品'),
                description=data.get('description', ''),
                category=data.get('category', 'other')
            )
            is_new = True
            print(f"🆕 创建新作品记录")
        else:
            # 更新现有作品信息
            if 'title' in data:
                artwork.title = data['title']
            if 'description' in data:
                artwork.description = data['description']
            if 'category' in data:
                artwork.category = data['category']
            print(f"♻️ 更新现有作品记录")
        
        # 更新文件路径 - 使用最新的文件
        if all_files['original_sketch']:
            artwork.original_sketch_path = f"{session_id}/{all_files['original_sketch']}"
        
        if all_files['colored_images']:
            # 使用最新的生成图片
            artwork.colored_image_path = f"{session_id}/{all_files['colored_images'][-1]}"
        
        if all_files['adjusted_images']:
            # 使用最新的调整图片
            artwork.figurine_image_path = f"{session_id}/{all_files['adjusted_images'][-1]}"
        
        if all_files['model_3d']:
            artwork.model_3d_path = f"{session_id}/{all_files['model_3d']}"
        
        if all_files['video_file']:
            artwork.video_file_path = f"{session_id}/{all_files['video_file']}"
        
        # 保存到数据库
        if is_new:
            db.session.add(artwork)
        
        db.session.commit()
        
        print(f"✅ 作品保存成功: ID {artwork.id}")
        
        return jsonify({
            'success': True,
            'artwork_id': artwork.id,
            'message': '作品保存成功！' if is_new else '作品更新成功！'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存作品失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'保存失败: {str(e)}'}), 500


# ========== 图片处理相关API ==========

@api_bp.route('/get-image-info', methods=['POST'])
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

@api_bp.route('/fetch-image', methods=['POST'])
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


# ========== Prompt处理相关API ==========

@api_bp.route('/translate-prompt', methods=['POST'])
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

@api_bp.route('/organize-prompt', methods=['POST'])
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

@api_bp.route('/generate-artwork-info', methods=['POST'])
def generate_artwork_info_api():
    """使用AI生成作品的标题、分类和介绍"""
    try:
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


# ========== 视频生成相关API ==========

@api_bp.route('/generate-video', methods=['POST'])
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

@api_bp.route('/video-status/<path:task_id>')
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

@api_bp.route('/save-video', methods=['POST'])
def save_video():
    """保存视频到作品集"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        video_url = data.get('video_url')
        prompt = data.get('prompt', '')
        
        if not session_id or not video_url:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        # TODO: 实现视频保存到作品集的逻辑
        # 这里可以扩展gallery_manager来支持视频作品
        
        print(f"✅ 视频已保存: {video_url}")
        
        return jsonify({
            'success': True,
            'message': '视频已保存到作品集'
        })
        
    except Exception as e:
        print(f"❌ 视频保存错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== 作品展示和互动API ==========

@api_bp.route('/feature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def feature_artwork(artwork_id):
    """设置作品为推荐作品"""
    try:
        # 获取作品
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 取消当前用户的其他推荐作品
        Artwork.query.filter_by(user_id=current_user.id, is_featured=True).update({
            'is_featured': False,
            'featured_at': None
        })
        
        # 设置新的推荐作品
        artwork.is_featured = True
        artwork.is_public = True  # 推荐作品自动设为公开
        artwork.featured_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已设为推荐作品！'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

@api_bp.route('/vote-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def vote_artwork(artwork_id):
    """为作品投票"""
    try:
        data = request.get_json()
        vote_type = data.get('vote_type', 'like')
        
        # 验证投票类型
        if vote_type not in ['like', 'love', 'wow', 'cool']:
            return jsonify({'error': '无效的投票类型'}), 400
        
        # 获取作品
        artwork = Artwork.query.get(artwork_id)
        if not artwork or not artwork.is_public:
            return jsonify({'error': '作品不存在或未公开'}), 404
        
        # 允许给自己的作品投票
        # 检查是否已投票
        existing_vote = ArtworkVote.query.filter_by(
            artwork_id=artwork_id, 
            voter_id=current_user.id
        ).first()
        
        if existing_vote:
            # 已经投过票，不允许重复投票
            return jsonify({
                'success': False,
                'error': '您已经为这个作品点过赞了！',
                'vote_count': artwork.vote_count
            })
        else:
            # 新投票
            vote = ArtworkVote(artwork_id, current_user.id, vote_type)
            db.session.add(vote)
            
            # 更新作品投票数
            artwork.vote_count = (artwork.vote_count or 0) + 1
            message = '点赞成功！'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'vote_count': artwork.vote_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'投票失败: {str(e)}'}), 500

@api_bp.route('/increment-view/<int:artwork_id>', methods=['POST'])
@login_required
def increment_view(artwork_id):
    """增加作品浏览次数（每个用户只记录一次）"""
    try:
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return jsonify({'error': '作品不存在'}), 404
        
        # 检查该用户是否已经浏览过这个作品
        existing_view = ArtworkView.query.filter_by(
            artwork_id=artwork_id,
            viewer_id=current_user.id
        ).first()
        
        if not existing_view:
            # 首次浏览，创建浏览记录
            view = ArtworkView(artwork_id, current_user.id)
            db.session.add(view)
            
            # 增加浏览次数
            artwork.view_count = (artwork.view_count or 0) + 1
            db.session.commit()
            
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': True
            })
        else:
            # 已经浏览过，不增加计数
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': False
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新浏览次数失败: {str(e)}'}), 500

@api_bp.route('/unfeature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def unfeature_artwork(artwork_id):
    """取消推荐作品"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_featured = False
        artwork.featured_at = None
        # 注意：保持is_public状态，用户可以单独控制
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已取消推荐'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'操作失败: {str(e)}'}), 500


# ========== 作品详情和管理API ==========

@api_bp.route('/artwork/<int:artwork_id>', methods=['GET'])
@login_required
def get_artwork_api(artwork_id):
    """获取作品详情API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        file_urls = artwork.get_file_urls()
        
        artwork_data = {
            'id': artwork.id,
            'title': artwork.title or '未命名作品',
            'description': artwork.description,
            'created_at': artwork.created_at.strftime('%Y年%m月%d日 %H:%M'),
            'artwork_type': '3D模型' if file_urls['model_3d'] else 'AI上色' if file_urls['colored_image'] else '手绘作品',
            'image_url': file_urls['colored_image'] or file_urls['figurine_image'] or file_urls['original_sketch'] or '/static/images/placeholder.png',
            'views': artwork.view_count or 0,
            'likes': artwork.vote_count or 0,
            'is_featured': artwork.is_featured,
            'is_public': artwork.is_public,
            'files': {
                'original_sketch': file_urls['original_sketch'],
                'colored_image': file_urls['colored_image'],
                'figurine_image': file_urls['figurine_image'],
                'model_3d': file_urls['model_3d'],
                'video_file': file_urls['video_file']
            }
        }
        
        return jsonify(artwork_data)
        
    except Exception as e:
        return jsonify({'error': f'获取作品详情失败: {str(e)}'}), 500

@api_bp.route('/artwork/<int:artwork_id>', methods=['DELETE'])
@login_required
def delete_artwork_api(artwork_id):
    """删除作品API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 删除相关的投票记录
        ArtworkVote.query.filter_by(artwork_id=artwork_id).delete()
        
        # 删除文件
        session_folder = os.path.join('creation_sessions', artwork.session_id)
        if os.path.exists(session_folder):
            try:
                shutil.rmtree(session_folder)
            except Exception as file_error:
                print(f"删除文件失败: {file_error}")
        
        # 删除数据库记录
        db.session.delete(artwork)
        db.session.commit()
        
        # 计算删除后的统计信息
        remaining_count = Artwork.query.filter_by(user_id=current_user.id).count()
        total_likes = db.session.query(func.sum(Artwork.vote_count)).filter_by(user_id=current_user.id).scalar() or 0
        total_views = db.session.query(func.sum(Artwork.view_count)).filter_by(user_id=current_user.id).scalar() or 0
        
        return jsonify({
            'success': True,
            'message': '作品已删除',
            'stats': {
                'total_artworks': remaining_count,
                'total_likes': total_likes,
                'total_views': total_views
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@api_bp.route('/artwork/<int:artwork_id>/privacy', methods=['POST'])
@login_required
def update_artwork_privacy(artwork_id):
    """更新作品隐私设置API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        data = request.get_json()
        is_public = data.get('is_public', False)
        
        artwork.is_public = is_public
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '隐私设置已更新',
            'is_public': artwork.is_public
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500

@api_bp.route('/artwork/<int:artwork_id>/set-public', methods=['POST'])
@login_required
def set_artwork_public(artwork_id):
    """设置作品为公开"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为公开',
            'is_public': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

@api_bp.route('/artwork/<int:artwork_id>/set-private', methods=['POST'])
@login_required
def set_artwork_private(artwork_id):
    """设置作品为私密"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为私密',
            'is_public': False
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500


# ========== 图片生成API ==========

@api_bp.route('/generate-image', methods=['POST'])
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
        
        print(f"📝 输入参数: prompt={prompt}, style={style}, uploaded_file={uploaded_file.filename if uploaded_file else None}")
        
        if not prompt and not uploaded_file and not original_image_path:
            print("❌ 缺少必要参数")
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
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
            
            # 预处理手绘图片
            from app.utils import preprocess_sketch
            processed_sketch = preprocess_sketch(sketch_path)
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
        
        print(f"🎨 开始生成图片 - 文字: {prompt}, 图片: {sketch_path}")
        
        # 根据输入类型生成图片
        if sketch_path and prompt:
            # 图片+文字模式
            generated_image_path = nano_banana.generate_image_from_sketch_and_text(
                sketch_path, prompt, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        elif sketch_path:
            # 纯图片模式
            generated_image_path = nano_banana.generate_image_from_sketch(
                sketch_path, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        else:
            # 纯文字模式
            generated_image_path = nano_banana.generate_image_from_text(
                prompt, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        
        print(f"✅ 图片生成完成: {generated_image_path}")
        
        # 检查图片是否真的生成成功
        if not generated_image_path or not os.path.exists(generated_image_path):
            print(f"❌ 图片生成失败，不保存到数据库")
            return jsonify({'error': '图片生成失败，请重试'}), 500
        
        # 返回相对路径用于前端显示
        from app.utils import normalize_path_for_url
        relative_path = normalize_path_for_url(generated_image_path)
        print(f"📍 返回图片URL: {relative_path}")
        
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
            'image_url': relative_path,
            'image_path': relative_path,
            'version_id': version_id,
            'message': '图片生成成功！'
        }
        
        # 如果有上传的图片，也返回原始图片路径
        if sketch_path:
            response_data['original_image_url'] = normalize_path_for_url(sketch_path)
        
        return jsonify(response_data)
            
    except Exception as e:
        print(f"❌ 图片生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


# ========== 会话管理API ==========

@api_bp.route('/create-session', methods=['POST'])
def create_session():
    """创建新的创作会话"""
    try:
        user_info = request.get_json() or {}
        session_id = session_manager.create_session(user_info)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': '创作会话已创建'
        })
        
    except Exception as e:
        return jsonify({'error': f'创建会话失败: {str(e)}'}), 500


@api_bp.route('/session/<session_id>/info')
def get_session_info(session_id):
    """获取会话信息"""
    try:
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({'error': '会话不存在'}), 404
        
        return jsonify({
            'success': True,
            'session': session_info
        })
        
    except Exception as e:
        return jsonify({'error': f'获取会话信息失败: {str(e)}'}), 500


@api_bp.route('/session/<session_id>/versions')
def get_session_versions(session_id):
    """获取会话的所有版本"""
    try:
        version_type = request.args.get('type')  # 'image' 或 'model'
        versions = session_manager.get_session_versions(session_id, version_type)
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        return jsonify({'error': f'获取版本失败: {str(e)}'}), 500


@api_bp.route('/session/<session_id>/selected-versions')
def get_selected_versions(session_id):
    """获取当前选择的版本"""
    try:
        selected = session_manager.get_selected_versions(session_id)
        
        return jsonify({
            'success': True,
            'selected': selected
        })
        
    except Exception as e:
        return jsonify({'error': f'获取选择版本失败: {str(e)}'}), 500


@api_bp.route('/session/<session_id>/select-version', methods=['POST'])
def select_version(session_id):
    """选择版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.select_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'选择版本失败: {str(e)}'}), 500


@api_bp.route('/session/<session_id>/delete-version', methods=['DELETE'])
def delete_version(session_id):
    """删除版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.delete_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'删除版本失败: {str(e)}'}), 500
