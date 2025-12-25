"""
管理员后台路由
- 管理所有教师和学生
- 系统统计
"""

from datetime import date, datetime

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from auth.models import Artwork, User, db
from auth.permissions import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """管理员仪表盘"""
    # 统计数据
    total_users = User.query.count()
    visitors = User.query.filter_by(role='visitor').count()
    students = User.query.filter_by(role='student').count()
    teachers = User.query.filter_by(role='teacher').count()
    admins = User.query.filter_by(role='admin').count()
    
    # 正式学生数量
    enrolled_students = User.query.filter_by(role='student', is_enrolled=True).count()
    
    # 作品统计
    total_artworks = Artwork.query.count()
    
    # 今日活跃用户（今天登录过的）
    today = date.today()
    active_today = User.query.filter(
        db.func.date(User.last_login) == today
    ).count()
    
    stats = {
        'total_users': total_users,
        'visitors': visitors,
        'students': students,
        'enrolled_students': enrolled_students,
        'teachers': teachers,
        'admins': admins,
        'total_artworks': total_artworks,
        'active_today': active_today
    }
    
    # 最近注册的用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)


@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    """教师管理页面"""
    teachers = User.query.filter_by(role='teacher').order_by(User.created_at.desc()).all()
    # 获取可以提升为教师的用户（非教师、非管理员）
    promotable_users = User.query.filter(
        User.role.in_(['visitor', 'student'])
    ).order_by(User.created_at.desc()).all()
    return render_template('admin/teachers.html', teachers=teachers, promotable_users=promotable_users)


@admin_bp.route('/teacher/create', methods=['POST'])
@login_required
@admin_required
def create_teacher():
    """创建新教师账户"""
    username = request.form.get('username')
    nickname = request.form.get('nickname')
    parent_email = request.form.get('parent_email')
    password = request.form.get('password')
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 创建教师账户
    teacher = User(
        username=username,
        nickname=nickname,
        parent_email=parent_email,
        password=password,
        role='teacher'
    )
    teacher.is_verified = True  # 教师账户自动验证
    
    db.session.add(teacher)
    db.session.commit()
    
    flash(f'成功创建教师账户：{nickname}', 'success')
    return jsonify({'success': True, 'teacher_id': teacher.id})


@admin_bp.route('/teacher/promote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def promote_to_teacher(user_id):
    """将现有用户提升为教师"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'teacher':
        return jsonify({'error': '该用户已经是教师'}), 400
    
    if user.role == 'admin':
        return jsonify({'error': '不能修改管理员角色'}), 400
    
    old_role = user.role
    user.role = 'teacher'
    user.is_verified = True
    user.image_token_remaining = 999999  # 教师无限Token
    user.daily_token_amount = 0
    
    db.session.commit()
    
    flash(f'成功将 {user.nickname} 从 {old_role} 提升为教师', 'success')
    return jsonify({'success': True})


@admin_bp.route('/teacher/<int:teacher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_teacher(teacher_id):
    """删除教师账户"""
    teacher = User.query.get_or_404(teacher_id)
    
    if teacher.role != 'teacher':
        return jsonify({'error': '只能删除教师账户'}), 400
    
    db.session.delete(teacher)
    db.session.commit()
    
    flash(f'已删除教师账户：{teacher.nickname}', 'success')
    return jsonify({'success': True})


@admin_bp.route('/students')
@login_required
@admin_required
def students():
    """学生管理页面"""
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # 正式学生（is_enrolled=True）
    formal_students = User.query.filter_by(role='student', is_enrolled=True).order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 体验学生（is_enrolled=False）
    trial_students = User.query.filter_by(role='student', is_enrolled=False).order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 意向学员（游客）
    prospects = User.query.filter_by(role='visitor').order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/students.html', 
                          formal_students=formal_students, 
                          trial_students=trial_students, 
                          prospects=prospects)


@admin_bp.route('/user/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """修改用户角色"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    is_enrolled = request.form.get('is_enrolled')  # 是否为正式学生
    
    if new_role not in ['visitor', 'student', 'teacher', 'admin']:
        return jsonify({'error': '无效的角色'}), 400
    
    old_role = user.role
    user.role = new_role
    
    # 设置is_enrolled（正式学生）
    if is_enrolled == 'true':
        user.is_enrolled = True
    
    # 根据新角色调整权限
    if new_role == 'teacher' or new_role == 'admin':
        user.image_token_remaining = 999999
        user.daily_token_amount = 0
    elif new_role == 'visitor':
        user.daily_token_amount = 10
        user.is_enrolled = False  # 意向学员不是正式的
    elif new_role == 'student' and not user.is_enrolled:
        # 体验学生
        user.daily_token_amount = 0  # 体验学生不每日赠送
    
    db.session.commit()
    
    flash(f'已将 {user.nickname} 的角色从 {old_role} 改为 {new_role}', 'success')
    return jsonify({'success': True})


@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """管理员重置单个用户密码"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    # 设置新密码
    user.password = new_password
    db.session.commit()
    
    flash(f'已重置 {user.nickname} 的密码', 'success')
    return jsonify({'success': True, 'message': f'用户 {user.nickname} 的密码已重置'})


@admin_bp.route('/users/batch-reset-password', methods=['POST'])
@login_required
@admin_required
def batch_reset_password():
    """批量重置用户密码"""
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    new_password = data.get('new_password')
    
    if not user_ids:
        return jsonify({'error': '未选择用户'}), 400
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': '密码长度至少6位'}), 400
    
    # 批量修改密码
    success_count = 0
    failed_users = []
    
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            if user.role == 'admin' and user.id != current_user.id:
                failed_users.append(f'{user.nickname}(不能修改其他管理员)')
                continue
            user.password = new_password
            success_count += 1
        else:
            failed_users.append(f'ID:{user_id}(用户不存在)')
    
    db.session.commit()
    
    result = {
        'success': True,
        'success_count': success_count,
        'total': len(user_ids),
        'message': f'成功重置 {success_count} 个用户的密码'
    }
    
    if failed_users:
        result['failed'] = failed_users
        result['message'] += f'，{len(failed_users)} 个失败'
    
    flash(result['message'], 'success' if not failed_users else 'warning')
    return jsonify(result)


@admin_bp.route('/system-settings')
@login_required
@admin_required
def system_settings():
    """系统设置页面"""
    return render_template('admin/settings.html')
