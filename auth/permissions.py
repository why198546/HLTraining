"""
权限管理装饰器
提供用于路由保护的装饰器函数
"""

from functools import wraps

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user

from auth.models import CourseProgress


def teacher_required(f):
    """
    要求用户必须是老师角色
    用于视频生成等需要老师权限的功能
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'teacher':
            flash('此功能仅限老师使用', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def image_token_required(f):
    """
    检查用户是否还有图片生成令牌
    如果没有令牌，返回错误信息
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        # 检查令牌余额
        if current_user.image_token_remaining <= 0:
            if request.is_json:
                return jsonify({
                    'error': '图片生成令牌已用完',
                    'message': '⚠️ 您的图片生成令牌已用完！\n\n您当前剩余令牌：0\n请联系老师充值后继续使用。',
                    'remaining': 0
                }), 403
            flash('⚠️ 图片生成令牌已用完！您当前剩余令牌：0，请联系老师充值后继续使用。', 'error')
            return redirect(url_for('auth.profile'))
        
        return f(*args, **kwargs)
    return decorated_function


def enrolled_required(f):
    """
    要求用户必须已报名上课
    用于访问课堂内容
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        # 老师可以访问所有课程
        if current_user.role == 'teacher':
            return f(*args, **kwargs)
        
        if not current_user.is_enrolled:
            flash('请先报名上课才能访问课堂内容', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def lesson_access_required(lesson_number):
    """
    检查学生是否有权限访问指定课程
    规则：
    - 第一节课：报名后即可访问
    - 后续课程：需要前一节课老师确认完成
    - 老师：可以访问所有课程
    
    Args:
        lesson_number: 课程编号（1, 2, 3...）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 老师可以访问所有课程
            if current_user.role == 'teacher':
                return f(*args, **kwargs)
            
            # 检查是否报名
            if not current_user.is_enrolled:
                flash('请先报名上课才能访问课堂内容', 'error')
                return redirect(url_for('main.index'))
            
            # 第一节课，报名后即可访问
            if lesson_number == 1:
                return f(*args, **kwargs)
            
            # 后续课程，检查前一节课是否已被老师确认
            previous_lesson = CourseProgress.query.filter_by(
                user_id=current_user.id,
                lesson_number=lesson_number - 1
            ).first()
            
            if not previous_lesson or not previous_lesson.is_confirmed:
                flash(f'请先完成第{lesson_number-1}节课并等待老师确认后才能访问第{lesson_number}节课', 'error')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def consume_image_token(user):
    """
    消耗一个图片生成令牌
    
    Args:
        user: User对象
    
    Returns:
        bool: 是否成功消耗令牌
    """
    from auth.models import db
    
    if user.image_token_remaining > 0:
        user.image_token_remaining -= 1
        db.session.commit()
        return True
    return False


def add_image_tokens(user, amount):
    """
    为用户添加图片生成令牌（老师操作）
    
    Args:
        user: User对象
        amount: 要添加的令牌数量
    """
    from auth.models import db
    
    user.image_token_remaining += amount
    db.session.commit()


def can_use_3d_model(f):
    """
    检查用户是否可以使用3D建模功能
    只有正式学生、教师、管理员可以使用
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.can_use_3d_model():
            if request.is_json:
                return jsonify({
                    'error': '权限不足',
                    'message': '🔒 3D建模功能仅对正式学生开放\n\n请扫描正式课程二维码升级账户'
                }), 403
            flash('🔒 3D建模功能仅对正式学生开放，请扫描正式课程二维码升级账户', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def can_use_video_generation(f):
    """
    检查用户是否可以使用视频生成功能
    只有正式学生、教师、管理员可以使用
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.can_use_video_generation():
            if request.is_json:
                return jsonify({
                    'error': '权限不足',
                    'message': '🔒 视频生成功能仅对正式学生开放\n\n请扫描正式课程二维码升级账户'
                }), 403
            flash('🔒 视频生成功能仅对正式学生开放，请扫描正式课程二维码升级账户', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    要求用户必须是管理员角色
    用于管理员后台功能
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('此功能仅限管理员使用', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function
