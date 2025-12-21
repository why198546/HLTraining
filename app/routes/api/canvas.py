"""画布相关API路由"""
import os
import re
import uuid
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from api.nano_banana import NanoBananaAPI
from app.utils import normalize_path_for_url
from auth.models import CanvasProject, db

canvas_api_bp = Blueprint('canvas_api', __name__)


@canvas_api_bp.route('/generate', methods=['POST'])
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


@canvas_api_bp.route('/chat', methods=['POST'])
@login_required
def canvas_chat():
    """画布对话API - 使用Gemini AI对话"""
    try:
        import google.generativeai as genai
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        selected_image_index = data.get('selectedImageIndex')
        has_images = data.get('hasImages', False)
        forced_intent = data.get('forcedIntent')  # 命令模式强制的意图
        chat_history = data.get('chatHistory', [])  # 获取历史对话
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': '请输入内容'
            }), 400
        
        print(f"🌰 松果助手对话: {prompt}, 历史消息数: {len(chat_history)}, 选中图片: {selected_image_index}, 有图片: {has_images}, 强制意图: {forced_intent}")
        
        # 配置Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'GEMINI_API_KEY 未配置'
            }), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 自动总结聊天历史（类似VS Code Chat）
        conversation_summary = ""
        if chat_history and len(chat_history) > 4:  # 超过2轮对话才需要总结
            try:
                print(f"📝 开始总结 {len(chat_history)} 条历史消息...")
                
                # 构建总结提示
                history_text = "\n".join([
                    f"{'用户' if msg.get('role') == 'user' else '助手'}: {msg.get('content', '')}"
                    for msg in chat_history
                ])
                
                summarize_prompt = f"""请总结以下对话的关键信息，提取：
1. 用户的创作目标和意图
2. 已经完成的操作（生成/修改了什么图片）
3. 用户的偏好和要求
4. 当前需要解决的问题或待完成的任务

对话历史：
{history_text}

请用简洁的2-3句话总结，突出最重要的上下文信息。"""
                
                summary_response = model.generate_content(summarize_prompt)
                conversation_summary = summary_response.text.strip()
                print(f"✅ 总结完成: {conversation_summary[:100]}...")
                
            except Exception as e:
                print(f"⚠️ 总结失败，将使用原始历史: {str(e)}")
                # 降级：使用最近几条消息
                recent_messages = chat_history[-6:]
                conversation_summary = "最近对话：\n" + "\n".join([
                    f"{'用户' if msg.get('role') == 'user' else '助手'}: {msg.get('content', '')}"
                    for msg in recent_messages
                ])
        
        # 如果有强制意图，按意图执行
        if forced_intent:
            if forced_intent == 'generate':
                return jsonify({
                    'success': True,
                    'intent': 'generate',
                    'refined_prompt': prompt,
                    'response': '好的，我来为你生成图片...'
                })
            elif forced_intent == 'modify':
                return jsonify({
                    'success': True,
                    'intent': 'modify',
                    'refined_prompt': prompt,
                    'response': '好的，我来帮你修改这张图片...'
                })
        
        # 构建系统提示
        system_prompt = """你是松果助手，一个友好的AI画布创作助手。你需要帮助用户：
1. 判断用户意图：生成图片、修改图片、还是普通对话
2. 如果是生成或修改图片，提取关键信息
3. 如果是对话，友好地回答问题（参考之前的对话总结）

当前画布状态：
- 有图片：{has_images}
- 选中图片：{selected}

判断规则：
- 包含"画"、"生成"、"创作"等词 → 意图是generate
- 选中了图片且包含"修改"、"改成"、"换"等词 → 意图是modify  
- 其他情况 → 意图是chat

请用JSON格式回复：
{{
  "intent": "generate/modify/chat",
  "refined_prompt": "提炼后的提示词(仅生成/修改时)",
  "response": "给用户的回复文字"
}}""".format(
            has_images='是' if has_images else '否',
            selected='是' if selected_image_index is not None else '否'
        )
        
        # 构建完整的对话上下文
        conversation_context = system_prompt + "\n\n"
        
        # 添加对话总结（如果有）
        if conversation_summary:
            conversation_context += f"对话上下文总结：\n{conversation_summary}\n\n"
        elif chat_history and len(chat_history) <= 4:
            # 对话较短，直接包含最近消息
            conversation_context += "最近对话：\n"
            for msg in chat_history[-4:]:
                role_name = "用户" if msg.get('role') == 'user' else "助手"
                conversation_context += f"{role_name}: {msg.get('content', '')}\n"
            conversation_context += "\n"
        
        # 添加当前用户消息
        conversation_context += f"用户最新消息：{prompt}"
        
        # 调用Gemini
        response = model.generate_content(conversation_context)
        
        # 解析Gemini返回的JSON
        import json
        response_text = response.text.strip()
        
        # 去除可能的markdown代码块标记
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
        return jsonify({
            'success': True,
            'intent': result.get('intent', 'chat'),
            'refined_prompt': result.get('refined_prompt', prompt),
            'response': result.get('response', '我明白了。')
        })
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {str(e)}")
        # 降级到简单匹配
        return simple_intent_detection(prompt, selected_image_index, has_images)
    except Exception as e:
        print(f"❌ 画布对话错误: {str(e)}")
        import traceback
        traceback.print_exc()
        # 降级到简单匹配
        return simple_intent_detection(prompt, selected_image_index, has_images)


def simple_intent_detection(prompt, selected_image_index, has_images):
    """简单的意图检测（降级方案）"""
    modify_keywords = ['修改', '改成', '换', '变成', '调整', '优化', '改进', '让它', '把它', '更', '加上', '去掉', '删除', '移除']
    generate_keywords = ['画', '生成', '创作', '做一个', '做一张', '帮我', '我想要', '给我', '设计', '制作']
    
    prompt_lower = prompt.lower()
    
    if selected_image_index is not None and any(kw in prompt_lower for kw in modify_keywords):
        return jsonify({
            'success': True,
            'intent': 'modify',
            'refined_prompt': prompt,
            'response': '好的，我来帮你修改这张图片...'
        })
    elif any(kw in prompt_lower for kw in generate_keywords):
        return jsonify({
            'success': True,
            'intent': 'generate',
            'refined_prompt': prompt,
            'response': '好的，我来为你生成图片...'
        })
    else:
        return jsonify({
            'success': True,
            'intent': 'chat',
            'refined_prompt': prompt,
            'response': '我是松果助手，很高兴为你服务！你可以问我创作相关的问题，或者直接描述想要生成的图片。'
        })


@canvas_api_bp.route('/modify', methods=['POST'])
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

@canvas_api_bp.route('/projects', methods=['GET'])
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


@canvas_api_bp.route('/projects/create', methods=['POST'])
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


@canvas_api_bp.route('/projects/<project_id>', methods=['GET'])
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


@canvas_api_bp.route('/projects/<project_id>', methods=['PUT'])
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


@canvas_api_bp.route('/projects/<project_id>', methods=['DELETE'])
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


@canvas_api_bp.route('/projects/<project_id>/chat', methods=['POST'])
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
