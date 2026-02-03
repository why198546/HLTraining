"""
模块级模板API - 用于管理课程中各个模块（模块一、二、三）的提示词模板
"""
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from auth.models import db

# 创建Blueprint
module_template_bp = Blueprint('module_template', __name__)


# 默认模板配置
def get_default_module_templates():
    """获取默认的模块模板配置"""
    return {
        'module1': {
            'name': '模块一：图片生成',
            'mode': 'text',
            'raw_prompt': '''请根据用户的描述生成一张高质量的图片。

要求：
1. 准确理解用户的描述内容
2. 生成符合描述的图像元素
3. 保持画面构图合理、色彩协调
4. 注重细节的精细表现

请生成真实照片风格的图片。'''
        },
        'module2': {
            'name': '模块二：图像融合',
            'mode': 'dual',  # 双模板模式：传统 + Vision提取
            'traditional_prompt': '''请将第二张图中的特征应用到第一张照片的人物上。

{composition_hint}

风格要求：{style_suffix}''',
            'vision_extraction_prompt': '''请根据提取的特征生成图片：

人物特征（来自照片1）：
{person_features}

服饰特征（来自手绘2）：
{outfit_features}

{composition_hint}

风格要求：{style_suffix}'''
        },
        'module3': {
            'name': '模块三：AI点评',
            'encouragement': '很棒的作品！',
            'aspects': ['线条流畅度', '色彩运用', '创意表现'],
            'mode': 'structured',
            'raw_prompt': ''
        }
    }


@module_template_bp.route('/api/formal-lesson/module-template', methods=['GET'])
@login_required
def get_module_template():
    """获取指定课程的指定模块模板"""
    try:
        lesson_key = request.args.get('lesson_key')
        module_key = request.args.get('module_key')
        
        if not lesson_key or not module_key:
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 刷新当前用户数据，确保获取最新的数据库内容
        from auth.models import User
        db.session.expire(current_user)
        current_user_refreshed = User.query.get(current_user.id)
        
        # 如果用户是学生，获取其所属教师的模板
        teacher = None
        if current_user_refreshed.role == 'student':
            from sqlalchemy import text
            
            result = db.session.execute(
                text('''
                    SELECT teacher_id FROM student_courses 
                    WHERE student_id = :student_id 
                    LIMIT 1
                '''),
                {'student_id': current_user_refreshed.id}
            ).fetchone()
            
            if result and result[0]:
                teacher = User.query.get(result[0])
        elif current_user_refreshed.role in ['teacher', 'admin']:
            # 教师和管理员使用自己的模板
            teacher = current_user_refreshed
        
        # 尝试获取教师的自定义模板
        template = None
        if teacher and teacher.module_templates:
            # module_templates的结构: {lesson_key: {module_key: {...}}}
            lesson_templates = teacher.module_templates.get(lesson_key, {})
            template = lesson_templates.get(module_key)
            
            if template:
                current_app.logger.info(f"✅ 找到 {teacher.username} 的自定义模板")
                current_app.logger.info(f"  课程: {lesson_key}, 模块: {module_key}")
                current_app.logger.info(f"  模式: {template.get('mode')}")
                current_app.logger.info(f"  提示词: {template.get('raw_prompt', '')[:100]}...")
            else:
                current_app.logger.info(f"⚠️ {teacher.username} 的 module_templates 中没有 {lesson_key}/{module_key}")
                current_app.logger.info(f"  完整结构: {teacher.module_templates}")
        else:
            if teacher:
                current_app.logger.info(f"⚠️ {teacher.username} 的 module_templates 为空")
            else:
                current_app.logger.info(f"⚠️ 未找到 teacher 对象")
        
        # 如果没有自定义模板，使用默认模板
        if not template:
            current_app.logger.info(f"使用默认模板（课程: {lesson_key}, 模块: {module_key}）")
            default_templates = get_default_module_templates()
            template = default_templates.get(module_key, {
                'encouragement': '',
                'aspects': [],
                'mode': 'text',
                'raw_prompt': ''
            })
        
        # 生成最终提示词预览（仅模块二需要）
        final_prompt_examples = []
        if module_key == 'module2':
            # 模块二有两个模板
            mode = template.get('mode', 'text')
            
            if mode == 'dual':
                # 返回两个模板的风格示例
                traditional_prompt = template.get('traditional_prompt', '')
                vision_prompt = template.get('vision_extraction_prompt', '')
                
                # 风格配置
                style_configs = [
                    {'name': '真实照片风格', 'suffix': '真实照片风格，保持原貌'},
                    {'name': '卡通可爱风格', 'suffix': '卡通可爱Q版风格，色彩明亮'},
                    {'name': '素描线稿风格', 'suffix': '黑白素描线稿'},
                    {'name': '动漫风格', 'suffix': '日式动漫风格'},
                    {'name': '水彩风格', 'suffix': '柔和水彩画风格'}
                ]
                
                # 为每种风格返回风格后缀
                for style_config in style_configs:
                    final_prompt_examples.append({
                        'style_name': style_config['name'],
                        'final_prompt': f"风格要求：{style_config['suffix']}"
                    })
            else:
                # 兼容旧的单模板模式
                base_prompt = template.get('raw_prompt', '')
                
                style_configs = [
                    {'name': '真实照片风格', 'suffix': '真实照片风格，保持原貌'},
                    {'name': '卡通可爱风格', 'suffix': '卡通可爱Q版风格，色彩明亮'},
                    {'name': '素描线稿风格', 'suffix': '黑白素描线稿'},
                    {'name': '动漫风格', 'suffix': '日式动漫风格'},
                    {'name': '水彩风格', 'suffix': '柔和水彩画风格'}
                ]
                
                for style_config in style_configs:
                    final_prompt_examples.append({
                        'style_name': style_config['name'],
                        'final_prompt': f"风格要求：{style_config['suffix']}"
                    })
        
        return jsonify({
            'success': True, 
            'template': template,
            'final_prompt_examples': final_prompt_examples
        })
        
    except Exception as e:
        current_app.logger.error(f'获取模块模板失败: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@module_template_bp.route('/api/formal-lesson/module-template', methods=['POST'])
@login_required
def save_module_template():
    """保存指定课程的指定模块模板"""
    try:
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({'success': False, 'error': '仅教师和管理员可修改模板'})
        
        data = request.json
        lesson_key = data.get('lesson_key')
        module_key = data.get('module_key')
        mode = data.get('mode', 'text')
        
        if not lesson_key or not module_key:
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 根据模块类型准备不同的数据结构
        template_data = {}
        
        if module_key == 'module2':
            # 模块二：双模板模式
            traditional_prompt = data.get('traditional_prompt', '').strip()
            vision_extraction_prompt = data.get('vision_extraction_prompt', '').strip()
            
            if not traditional_prompt:
                return jsonify({'success': False, 'error': '通用提示词不能为空'})
            if not vision_extraction_prompt:
                return jsonify({'success': False, 'error': 'AI提取特征提示词不能为空'})
            
            template_data = {
                'mode': 'dual',
                'traditional_prompt': traditional_prompt,
                'vision_extraction_prompt': vision_extraction_prompt
            }
        else:
            # 模块一和模块三：传统模式
            encouragement = data.get('encouragement', '').strip()
            aspects = data.get('aspects', [])
            raw_prompt = data.get('raw_prompt', '').strip()
            
            # 验证：只有模块三才强制要求鼓励语和评价维度
            if module_key == 'module3':
                if mode == 'structured':
                    if not encouragement:
                        return jsonify({'success': False, 'error': '鼓励语不能为空'})
                    if not aspects or not all(a.strip() for a in aspects):
                        return jsonify({'success': False, 'error': '评价维度不能为空'})
                elif mode == 'text':
                    if not raw_prompt:
                        return jsonify({'success': False, 'error': '纯文字提示词不能为空'})
            else:
                # 模块一：只验证raw_prompt（纯文字模式）
                if mode == 'text' and not raw_prompt:
                    return jsonify({'success': False, 'error': '纯文字提示词不能为空'})
            
            template_data = {
                'encouragement': encouragement,
                'aspects': [a.strip() for a in aspects if a.strip()],
                'mode': mode,
                'raw_prompt': raw_prompt
            }
        
        # 初始化教师的模块模板字典（如果为空）
        # 重要：创建新的字典副本，确保SQLAlchemy能检测到变化
        if not current_user.module_templates:
            module_templates_copy = {}
            current_app.logger.info(f"初始化 {current_user.username} 的 module_templates")
        else:
            # 深拷贝现有数据
            import copy
            module_templates_copy = copy.deepcopy(current_user.module_templates)
            current_app.logger.info(f"复制 {current_user.username} 的现有 module_templates")
        
        # 确保课程key存在
        if lesson_key not in module_templates_copy:
            module_templates_copy[lesson_key] = {}
            current_app.logger.info(f"为 {current_user.username} 创建课程 {lesson_key} 的模板字典")
        
        # 更新该课程的该模块模板
        module_templates_copy[lesson_key][module_key] = template_data
        
        # 重新赋值整个对象（这样SQLAlchemy才能检测到变化）
        current_user.module_templates = module_templates_copy
        
        current_app.logger.info(f"📝 准备保存模板数据:")
        current_app.logger.info(f"  用户: {current_user.username} (ID: {current_user.id})")
        current_app.logger.info(f"  课程: {lesson_key}")
        current_app.logger.info(f"  模块: {module_key}")
        current_app.logger.info(f"  模式: {mode}")
        current_app.logger.info(f"  提示词长度: {len(raw_prompt)} 字符")
        
        # 标记字段已修改（SQLAlchemy需要明确知道JSON字段已更改）
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(current_user, 'module_templates')
        
        db.session.commit()
        
        # 验证保存
        db.session.refresh(current_user)
        saved_template = current_user.module_templates.get(lesson_key, {}).get(module_key)
        if saved_template:
            current_app.logger.info(f"✅ 验证成功：模板已保存到数据库")
            current_app.logger.info(f"  保存的提示词: {saved_template.get('raw_prompt', '')[:100]}...")
        else:
            current_app.logger.error(f"❌ 验证失败：数据库中未找到保存的模板")
        
        return jsonify({'success': True, 'message': '模板保存成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'保存模块模板失败: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@module_template_bp.route('/api/formal-lesson/module-template/reset', methods=['POST'])
@login_required
def reset_module_template():
    """重置指定课程的指定模块模板为默认值"""
    try:
        if current_user.role not in ['teacher', 'admin']:
            return jsonify({'success': False, 'error': '仅教师和管理员可重置模板'})
        
        data = request.json
        lesson_key = data.get('lesson_key')
        module_key = data.get('module_key')
        
        if not lesson_key or not module_key:
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 删除自定义模板
        if current_user.module_templates and lesson_key in current_user.module_templates:
            if module_key in current_user.module_templates[lesson_key]:
                del current_user.module_templates[lesson_key][module_key]
                
                # 如果该课程下没有其他模块了，删除课程key
                if not current_user.module_templates[lesson_key]:
                    del current_user.module_templates[lesson_key]
                
                # 标记字段已修改
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(current_user, 'module_templates')
                
                db.session.commit()
        
        # 返回默认模板
        default_templates = get_default_module_templates()
        default_template = default_templates.get(module_key, {
            'encouragement': '',
            'aspects': [],
            'mode': 'text',
            'raw_prompt': ''
        })
        
        current_app.logger.info(f"✅ 教师 {current_user.username} 重置了课程 {lesson_key} 的模块 {module_key} 模板")
        return jsonify({
            'success': True, 
            'message': '模板已重置为默认值',
            'template': default_template
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'重置模块模板失败: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})
