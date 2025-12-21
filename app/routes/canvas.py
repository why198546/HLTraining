"""画布相关路由"""
import json
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from auth.models import CanvasProject, db

canvas_bp = Blueprint('canvas', __name__)


@canvas_bp.route('/')
@login_required
def canvas():
    """项目管理页面（新的默认页面）"""
    return render_template('canvas_projects.html')


@canvas_bp.route('/projects')
@login_required
def projects():
    """项目管理页面（别名）"""
    return render_template('canvas_projects.html')


@canvas_bp.route('/projects/list')
@login_required
def list_projects():
    """获取用户的项目列表"""
    try:
        # 获取手绘项目
        sketch_projects = CanvasProject.query.filter_by(
            user_id=current_user.id,
            project_type='sketch',
            is_deleted=False
        ).order_by(CanvasProject.updated_at.desc()).limit(20).all()
        
        # 获取创意项目（包括旧数据，如果project_type为None则视为infinite）
        infinite_projects = CanvasProject.query.filter(
            CanvasProject.user_id == current_user.id,
            CanvasProject.is_deleted == False,
            db.or_(
                CanvasProject.project_type == 'infinite',
                CanvasProject.project_type == None
            )
        ).order_by(CanvasProject.updated_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'sketch_projects': [p.to_dict() for p in sketch_projects],
            'infinite_projects': [p.to_dict() for p in infinite_projects]
        })
    except Exception as e:
        import traceback
        print(f"Error in list_projects: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@canvas_bp.route('/projects/<int:project_id>')
@login_required
def get_project(project_id):
    """获取单个项目详情"""
    try:
        project = CanvasProject.query.filter_by(
            id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        # 更新最后打开时间
        project.last_opened_at = datetime.utcnow()
        project.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # 调试日志
        canvas_data = project.canvas_data if project.canvas_data else None
        images = canvas_data.get('images', []) if canvas_data else []
        print(f"\n📂 加载项目:")
        print(f"  - project_id: {project.id}")
        print(f"  - canvas_data存在: {canvas_data is not None}")
        print(f"  - 图片数量: {len(images)}")
        if images:
            print(f"  - 第一张图片: {images[0]}")
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'canvas_data': project.canvas_data if project.canvas_data else None,
            'chat_history': project.chat_history if project.chat_history else []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@canvas_bp.route('/projects/save', methods=['POST'])
@login_required
def save_project():
    """保存项目"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # 调试日志
        canvas_data = data.get('canvas_data', {})
        images = canvas_data.get('images', [])
        print(f"\n📦 接收到保存请求:")
        print(f"  - project_id: {project_id}")
        print(f"  - 图片数量: {len(images)}")
        if images:
            print(f"  - 第一张图片: {images[0]}")
        print(f"  - canvas_data keys: {canvas_data.keys()}")
        print(f"  - chat_history数量: {len(data.get('chat_history', []))}")
        
        if project_id:
            # 更新现有项目
            project = CanvasProject.query.filter_by(
                id=project_id,
                user_id=current_user.id
            ).first()
            
            if not project:
                return jsonify({'success': False, 'error': '项目不存在'}), 404
            
            project.title = data.get('title', project.title)
            if data.get('thumbnail'):
                project.thumbnail = data.get('thumbnail')
            project.canvas_data = data.get('canvas_data', {})
            if data.get('chat_history'):
                project.chat_history = data.get('chat_history', [])
            project.width = data.get('width', project.width)
            project.height = data.get('height', project.height)
            project.updated_at = datetime.utcnow()
        else:
            # 创建新项目
            new_project_id = str(uuid.uuid4())
            project = CanvasProject(
                project_id=new_project_id,
                user_id=current_user.id,
                title=data.get('title', '未命名项目'),
                project_type=data.get('project_type', 'sketch'),
                thumbnail=data.get('thumbnail'),
                canvas_data=data.get('canvas_data', {}),
                chat_history=data.get('chat_history', []),
                width=data.get('width', 512),
                height=data.get('height', 512)
            )
            db.session.add(project)
        
        db.session.commit()
        
        # 验证保存
        saved_canvas_data = project.canvas_data
        saved_images = saved_canvas_data.get('images', []) if saved_canvas_data else []
        print(f"\n✅ 保存成功:")
        print(f"  - project.id: {project.id}")
        print(f"  - 已保存图片数量: {len(saved_images)}")
        if saved_images:
            print(f"  - 第一张图片URL: {saved_images[0].get('url', 'N/A')}")
        
        return jsonify({
            'success': True,
            'project_id': project.id,
            'message': '项目保存成功'
        })
    except Exception as e:
        import traceback
        print(f"Error in save_project: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@canvas_bp.route('/projects/generate-title', methods=['POST'])
@login_required
def generate_project_title():
    """使用AI生成项目标题"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        project_type = data.get('type', 'sketch')
        
        if not prompt:
            return jsonify({'success': False, 'error': '需要提供提示词'})
        
        # 使用简单的规则生成标题（也可以调用AI API）
        # 这里先用简单的提取关键词方式
        title = generate_title_from_prompt(prompt, project_type)
        
        return jsonify({
            'success': True,
            'title': title
        })
    except Exception as e:
        print(f"Error generating title: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def generate_title_from_prompt(prompt, project_type='sketch'):
    """从提示词生成项目标题"""
    import re

    # 清理提示词
    prompt = prompt.strip()[:100]  # 限制长度
    
    # 移除常见的冗余词
    remove_words = ['生成', '创建', '画', '图片', '图像', '一个', '一张', '请', '帮我', '我想要']
    for word in remove_words:
        prompt = prompt.replace(word, '')
    
    # 提取关键词（简单版本）
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    
    # 限制标题长度
    if len(prompt) > 30:
        # 尝试在标点符号处截断
        for char in ['，', '。', ',', '.', '、']:
            if char in prompt[:30]:
                prompt = prompt.split(char)[0]
                break
        else:
            prompt = prompt[:27] + '...'
    
    # 如果提取后太短，使用默认名称
    if len(prompt) < 2:
        return '手绘项目' if project_type == 'sketch' else '创意项目'
    
    return prompt


@canvas_bp.route('/projects/<int:project_id>/rename', methods=['POST'])
@login_required
def rename_project(project_id):
    """重命名项目"""
    try:
        data = request.json
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({'success': False, 'error': '项目名称不能为空'}), 400
        
        project = CanvasProject.query.filter_by(
            id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        project.title = new_title
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': '重命名成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@canvas_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目"""
    try:
        project = CanvasProject.query.filter_by(
            id=project_id,
            user_id=current_user.id
        ).first()
        
        if not project:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '项目已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@canvas_bp.route('/sketch')
@login_required
def canvas_sketch():
    """手绘画布页面"""
    project_id = request.args.get('project_id')
    is_new = request.args.get('new') == '1'
    title = request.args.get('title', '')  # 改为空字符串
    
    return render_template('canvas_sketch.html', 
                         project_id=project_id,
                         is_new=is_new,
                         project_title=title)


@canvas_bp.route('/infinite')
@canvas_bp.route('/-infinite')  # 兼容旧的URL格式
@login_required
def canvas_infinite():
    """AI画布页面（无限画布版本）"""
    project_id = request.args.get('project_id')
    is_new = request.args.get('new') == '1'
    title = request.args.get('title', '')  # 改为空字符串
    
    return render_template('canvas_infinite.html',
                         project_id=project_id,
                         is_new=is_new,
                         project_title=title)
