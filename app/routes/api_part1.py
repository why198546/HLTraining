"""API路由（所有/api/*路由）"""
import json
import os
import re
import traceback
import uuid
from datetime import datetime
from io import BytesIO

import cv2
import numpy as np
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from PIL import Image
from werkzeug.utils import secure_filename

# 导入API模块
from api.nano_banana import NanoBananaAPI
from api.prompt_translator import translate_prompt
from api.sam3d_api import SAM3DAPI
from app.utils import allowed_file, normalize_path_for_url, preprocess_sketch
# 导入数据库和模型
from auth.models import (Artwork, ArtworkView, ArtworkVote, CanvasProject,
                         User, db)

api_bp = Blueprint('api', __name__)

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

# ========== 3D模型API ==========

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

# 此文件继续... (第2部分将包含视频API、作品API等)
