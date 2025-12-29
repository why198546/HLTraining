"""
管理员后台路由
- 管理所有教师和学生
- 系统统计
"""

from datetime import date, datetime, timedelta

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import func

from auth.models import Artwork, User, db, TokenUsageLog, Course, CourseEnrollment, MonthlyTokenGrant, TokenExpiry, TokenGrantLog
from auth.permissions import admin_required
from app.course_config.courses import get_course, get_courses_for_qr
import uuid
import qrcode
import os

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
    
    # 游客
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
        user.is_enrolled = False  # 游客不是正式的
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


@admin_bp.route('/user/<int:user_id>/add-tokens', methods=['POST'])
@login_required
@admin_required
def add_user_tokens(user_id):
    """给用户增加松果币"""
    from auth.models import TokenGrantLog
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'success': False, 'message': '请输入有效的松果币数量'}), 400
    
    user = User.query.get_or_404(user_id)
    old_amount = user.image_token_remaining
    user.image_token_remaining += int(amount)
    
    # 记录日志
    log = TokenGrantLog(
        user_id=user.id,
        grant_type='admin_manual',
        tokens_granted=int(amount),
        description=f'管理员手动增加 {int(amount)} 松果币',
        operator_id=current_user.id,
        operator_name=current_user.nickname
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'成功为 {user.nickname} 增加 {int(amount)} 松果币',
        'old_amount': old_amount,
        'new_amount': user.image_token_remaining
    })


@admin_bp.route('/user/<int:user_id>/detail', methods=['GET'])
@login_required
@admin_required
def get_user_detail(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'role': user.role,
            'parent_email': user.parent_email,
            'image_token_remaining': user.image_token_remaining,
            'daily_token_amount': user.daily_token_amount,
            'is_enrolled': user.is_enrolled,
            'trial_end_date': user.trial_end_date.strftime('%Y-%m-%d') if user.trial_end_date else None,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'birth_date': user.birth_date.strftime('%Y-%m-%d') if user.birth_date else None,
            'age': user.get_age() if user.birth_date else None,
            'gender': user.gender,
            'contact_phone': user.contact_phone,
            'mailing_address': user.mailing_address
        }
    })


@admin_bp.route('/token-usage')
@login_required
@admin_required
def token_usage():
    """松果币消耗监控页面"""
    return render_template('admin/token_usage.html')


@admin_bp.route('/token-usage/stats')
@login_required
@admin_required
def token_usage_stats():
    """获取松果币消耗统计数据"""
    period = request.args.get('period', 'day')  # day, week, month, year
    user_id = request.args.get('user_id', type=int)
    
    # 计算时间范围
    now = datetime.utcnow()
    if period == 'day':
        start_date = now - timedelta(days=7)  # 最近7天
        date_format = '%Y-%m-%d'
    elif period == 'week':
        start_date = now - timedelta(weeks=12)  # 最近12周
        date_format = '%Y-W%W'
    elif period == 'month':
        start_date = now - timedelta(days=365)  # 最近12个月
        date_format = '%Y-%m'
    else:  # year
        start_date = now - timedelta(days=365*3)  # 最近3年
        date_format = '%Y'
    
    # 构建查询
    query = TokenUsageLog.query.filter(TokenUsageLog.created_at >= start_date)
    if user_id:
        query = query.filter(TokenUsageLog.user_id == user_id)
    
    # 按时间和类型分组统计
    if period == 'day':
        stats = db.session.query(
            func.date(TokenUsageLog.created_at).label('date'),
            TokenUsageLog.usage_type,
            TokenUsageLog.user_id,
            func.sum(TokenUsageLog.tokens_used).label('total_tokens')
        ).filter(
            TokenUsageLog.created_at >= start_date
        )
        if user_id:
            stats = stats.filter(TokenUsageLog.user_id == user_id)
        stats = stats.group_by(
            func.date(TokenUsageLog.created_at),
            TokenUsageLog.usage_type,
            TokenUsageLog.user_id
        ).all()
        
        # 格式化为前端需要的格式
        trend_data = []
        for stat in stats:
            trend_data.append({
                'date': stat.date.strftime('%Y-%m-%d'),
                'usage_type': stat.usage_type,
                'user_id': stat.user_id,
                'total_tokens': stat.total_tokens
            })
            
    else:
        # 其他时间段类似处理
        stats = db.session.query(
            func.strftime(date_format, TokenUsageLog.created_at).label('period'),
            TokenUsageLog.usage_type,
            TokenUsageLog.user_id,
            func.sum(TokenUsageLog.tokens_used).label('total_tokens')
        ).filter(
            TokenUsageLog.created_at >= start_date
        )
        if user_id:
            stats = stats.filter(TokenUsageLog.user_id == user_id)
        stats = stats.group_by(
            func.strftime(date_format, TokenUsageLog.created_at),
            TokenUsageLog.usage_type,
            TokenUsageLog.user_id
        ).all()
        
        # 格式化为前端需要的格式
        trend_data = []
        for stat in stats:
            trend_data.append({
                'date': stat.period,
                'usage_type': stat.usage_type,
                'user_id': stat.user_id,
                'total_tokens': stat.total_tokens
            })
    
    # 计算类型分布（总计）
    type_stats = db.session.query(
        TokenUsageLog.usage_type,
        func.sum(TokenUsageLog.tokens_used).label('total_tokens')
    ).filter(
        TokenUsageLog.created_at >= start_date
    )
    if user_id:
        type_stats = type_stats.filter(TokenUsageLog.user_id == user_id)
    type_stats = type_stats.group_by(TokenUsageLog.usage_type).all()
    
    type_distribution = [
        {'usage_type': ts.usage_type, 'total_tokens': ts.total_tokens}
        for ts in type_stats
    ]
    
    # 获取用户排行
    top_users_query = db.session.query(
        TokenUsageLog.user_id,
        User.username,
        User.nickname,
        func.sum(TokenUsageLog.tokens_used).label('total_tokens')
    ).join(User).filter(
        TokenUsageLog.created_at >= start_date
    )
    if not user_id:  # 只有在不指定用户时才显示排行
        top_users_query = top_users_query.group_by(
            TokenUsageLog.user_id,
            User.username,
            User.nickname
        ).order_by(
            func.sum(TokenUsageLog.tokens_used).desc()
        ).limit(10)
    
    top_users = top_users_query.all()
    
    return jsonify({
        'success': True,
        'period': period,
        'trend_data': trend_data,
        'type_distribution': type_distribution,
        'top_users': [{
            'user_id': u.user_id,
            'username': u.username,
            'nickname': u.nickname,
            'total_tokens': u.total_tokens
        } for u in top_users]
    })


@admin_bp.route('/token-grant/stats')
@login_required
@admin_required
def token_grant_stats():
    """获取松果币生成统计数据"""
    try:
        from auth.models import TokenGrantLog
        
        period = request.args.get('period', 'day')  # day, week, month, year
        user_id = request.args.get('user_id', type=int)
        
        # 计算时间范围
        now = datetime.utcnow()
        if period == 'day':
            start_date = now - timedelta(days=30)  # 最近30天
            date_format = '%Y-%m-%d'
        elif period == 'week':
            start_date = now - timedelta(weeks=12)  # 最近12周
            date_format = '%Y-W%W'
        elif period == 'month':
            start_date = now - timedelta(days=365)  # 最近12个月
            date_format = '%Y-%m'
        else:  # year
            start_date = now - timedelta(days=365*3)  # 最近3年
            date_format = '%Y'
        
        # 构建查询
        query = TokenGrantLog.query.filter(TokenGrantLog.created_at >= start_date)
        if user_id:
            query = query.filter(TokenGrantLog.user_id == user_id)
        
        # 按时间和来源分组统计
        if period == 'day':
            stats = db.session.query(
                func.date(TokenGrantLog.created_at).label('date'),
                TokenGrantLog.grant_type,
                func.sum(TokenGrantLog.tokens_granted).label('total_tokens'),
                func.count(TokenGrantLog.id).label('grant_count')
            ).filter(
                TokenGrantLog.created_at >= start_date
            )
            if user_id:
                stats = stats.filter(TokenGrantLog.user_id == user_id)
            stats = stats.group_by(
                func.date(TokenGrantLog.created_at),
                TokenGrantLog.grant_type
            ).all()
            
            # 格式化为前端需要的格式
            trend_data = []
            for stat in stats:
                # func.date() 返回的是字符串，不需要再调用strftime
                date_str = stat.date if isinstance(stat.date, str) else stat.date.strftime('%Y-%m-%d')
                trend_data.append({
                    'date': date_str,
                    'grant_type': stat.grant_type,
                    'grant_type_display': TokenGrantLog.get_grant_type_display_static(stat.grant_type),
                    'total_tokens': stat.total_tokens,
                    'grant_count': stat.grant_count
                })
                
        else:
            # 其他时间段类似处理
            stats = db.session.query(
                func.strftime(date_format, TokenGrantLog.created_at).label('period'),
                TokenGrantLog.grant_type,
                func.sum(TokenGrantLog.tokens_granted).label('total_tokens'),
                func.count(TokenGrantLog.id).label('grant_count')
            ).filter(
                TokenGrantLog.created_at >= start_date
            )
            if user_id:
                stats = stats.filter(TokenGrantLog.user_id == user_id)
            stats = stats.group_by(
                func.strftime(date_format, TokenGrantLog.created_at),
                TokenGrantLog.grant_type
            ).all()
            
            # 格式化为前端需要的格式
            trend_data = []
            for stat in stats:
                trend_data.append({
                    'date': stat.period,
                    'grant_type': stat.grant_type,
                    'grant_type_display': TokenGrantLog.get_grant_type_display_static(stat.grant_type),
                    'total_tokens': stat.total_tokens,
                    'grant_count': stat.grant_count
                })
        
        # 计算来源分布（总计）
        source_stats = db.session.query(
            TokenGrantLog.grant_type,
            func.sum(TokenGrantLog.tokens_granted).label('total_tokens'),
            func.count(TokenGrantLog.id).label('grant_count')
        ).filter(
            TokenGrantLog.created_at >= start_date
        )
        if user_id:
            source_stats = source_stats.filter(TokenGrantLog.user_id == user_id)
        source_stats = source_stats.group_by(TokenGrantLog.grant_type).all()
        
        source_distribution = [
            {
                'grant_type': ss.grant_type, 
                'grant_type_display': TokenGrantLog.get_grant_type_display_static(ss.grant_type),
                'total_tokens': ss.total_tokens,
                'grant_count': ss.grant_count
            }
            for ss in source_stats
        ]
        
        # 获取总体统计 - 修复distinct count问题
        total_granted = db.session.query(
            func.sum(TokenGrantLog.tokens_granted)
        ).filter(TokenGrantLog.created_at >= start_date)
        if user_id:
            total_granted = total_granted.filter(TokenGrantLog.user_id == user_id)
        total_granted = total_granted.scalar() or 0
        
        total_count = db.session.query(
            func.count(TokenGrantLog.id)
        ).filter(TokenGrantLog.created_at >= start_date)
        if user_id:
            total_count = total_count.filter(TokenGrantLog.user_id == user_id)
        total_count = total_count.scalar() or 0
        
        # 获取不重复的用户数
        user_ids_query = db.session.query(
            TokenGrantLog.user_id.distinct()
        ).filter(TokenGrantLog.created_at >= start_date)
        if user_id:
            user_ids_query = user_ids_query.filter(TokenGrantLog.user_id == user_id)
        user_count = user_ids_query.count()
        
        # 获取最近记录
        recent_grants = TokenGrantLog.query.filter(
            TokenGrantLog.created_at >= start_date
        )
        if user_id:
            recent_grants = recent_grants.filter(TokenGrantLog.user_id == user_id)
        recent_grants = recent_grants.order_by(TokenGrantLog.created_at.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'period': period,
            'total_stats': {
                'total_granted': int(total_granted),
                'total_count': int(total_count),
                'user_count': int(user_count)
            },
            'trend_data': trend_data,
            'source_distribution': source_distribution,
            'recent_grants': [grant.to_dict() for grant in recent_grants]
        })
    except Exception as e:
        print(f"Error in token_grant_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/system-settings')
@login_required
@admin_required
def system_settings():
    """系统设置页面"""
    return render_template('admin/settings.html')


# ==================== 二维码管理 ====================

@admin_bp.route('/qrcodes')
@login_required
@admin_required
def qrcodes():
    """二维码管理页面"""
    # 获取所有二维码（按创建时间倒序）
    courses = Course.query.order_by(Course.created_at.desc()).all()
    
    # 准备课程数据
    courses_data = []
    for course in courses:
        valid, msg = course.is_valid()
        stats = course.get_usage_stats()
        
        courses_data.append({
            'id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'course_type': '体验课' if course.course_type == 'trial_course' else '正式课程',
            'course_type_raw': course.course_type,
            'qr_url': course.qr_image_path,
            'scan_url': url_for('qr.scan', code=course.course_code, _external=True),
            'created_at': course.created_at.strftime('%Y-%m-%d %H:%M'),
            'created_by': course.creator.nickname if course.creator else '未知',
            'created_by_id': course.created_by,
            'is_valid': valid,
            'validation_message': msg,
            'is_active': course.is_active,
            'stats': stats,
            'description': course.description or '无描述',
            'enrollments_count': len(course.enrollments),
            'expires_at': course.expires_at.strftime('%Y-%m-%d %H:%M') if course.expires_at else None,
            'max_uses': course.max_uses,
            'current_uses': course.current_uses
        })
    
    # 获取课程配置用于生成新二维码
    lessons = get_courses_for_qr()
    
    return render_template('admin/qrcodes.html', courses=courses_data, lessons=lessons)


@admin_bp.route('/qrcode/generate', methods=['POST'])
@login_required
@admin_required
def generate_qrcode():
    """生成二维码"""
    course_type = request.form.get('course_type')
    course_key = request.form.get('course_name')
    max_uses = request.form.get('max_uses')
    expires_days = request.form.get('expires_days')
    description = request.form.get('description', '')
    
    if course_type not in ['trial_course', 'formal_course']:
        return jsonify({'error': '课程类型无效'}), 400
    
    # 获取课程信息
    course_info = get_course(course_key)
    if not course_info:
        return jsonify({'error': '课程不存在'}), 400
    
    course_name = course_info.get('title', '未命名课程')
    
    # 处理使用次数限制
    max_uses_int = None
    if max_uses and max_uses.strip():
        try:
            max_uses_int = int(max_uses)
            if max_uses_int <= 0:
                return jsonify({'error': '使用次数必须大于0'}), 400
        except ValueError:
            return jsonify({'error': '使用次数必须是数字'}), 400
    
    # 处理过期时间
    expires_at = None
    if expires_days and expires_days.strip():
        try:
            days = int(expires_days)
            if days <= 0:
                return jsonify({'error': '有效天数必须大于0'}), 400
            expires_at = datetime.utcnow() + timedelta(days=days)
        except ValueError:
            return jsonify({'error': '有效天数必须是数字'}), 400
    
    # 生成唯一的课程代码
    course_code = str(uuid.uuid4())
    
    # 生成扫描URL
    scan_url = url_for('qr.scan', code=course_code, _external=True)
    
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(scan_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存二维码图片
    qr_dir = 'static/qrcodes'
    os.makedirs(qr_dir, exist_ok=True)
    qr_filename = f'{course_type}_{course_code}.png'
    qr_path = os.path.join(qr_dir, qr_filename)
    img.save(qr_path)
    
    # 保存课程信息到数据库
    new_course = Course(
        course_code=course_code,
        course_name=course_name,
        course_key=course_key,
        course_type=course_type,
        created_by=current_user.id,
        max_uses=max_uses_int,
        expires_at=expires_at,
        description=description
    )
    new_course.qr_image_path = f'/static/qrcodes/{qr_filename}'
    
    db.session.add(new_course)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '二维码生成成功',
        'qr_url': f'/static/qrcodes/{qr_filename}',
        'scan_url': scan_url,
        'course_code': course_code
    })


@admin_bp.route('/qrcode/<int:qr_id>/extend', methods=['POST'])
@login_required
@admin_required
def extend_qrcode(qr_id):
    """延长二维码有效期"""
    course = Course.query.get_or_404(qr_id)
    
    extend_days = request.json.get('days')
    if not extend_days or extend_days <= 0:
        return jsonify({'error': '延长天数必须大于0'}), 400
    
    # 如果原本没有过期时间，从当前时间开始计算
    if not course.expires_at:
        course.expires_at = datetime.utcnow()
    
    # 如果已经过期，从当前时间开始延长；否则从原过期时间延长
    if course.expires_at < datetime.utcnow():
        course.expires_at = datetime.utcnow() + timedelta(days=extend_days)
    else:
        course.expires_at = course.expires_at + timedelta(days=extend_days)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'已延长{extend_days}天',
        'new_expires_at': course.expires_at.strftime('%Y-%m-%d %H:%M')
    })


@admin_bp.route('/qrcode/<int:qr_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_qrcode(qr_id):
    """使二维码失效"""
    course = Course.query.get_or_404(qr_id)
    course.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '二维码已失效'
    })


@admin_bp.route('/qrcode/<int:qr_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_qrcode(qr_id):
    """重新激活二维码"""
    course = Course.query.get_or_404(qr_id)
    course.is_active = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '二维码已激活'
    })


@admin_bp.route('/qrcode/<int:qr_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_qrcode(qr_id):
    """删除二维码"""
    course = Course.query.get_or_404(qr_id)
    
    # 删除二维码图片文件
    if course.qr_image_path:
        qr_path = course.qr_image_path.lstrip('/')
        if os.path.exists(qr_path):
            os.remove(qr_path)
    
    # 删除数据库记录（会级联删除相关的报名记录）
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '二维码已删除'
    })


@admin_bp.route('/qrcode/<int:qr_id>/enrollments')
@login_required
@admin_required
def qrcode_enrollments(qr_id):
    """查看二维码的使用记录"""
    course = Course.query.get_or_404(qr_id)
    
    enrollments = []
    for enrollment in course.enrollments:
        enrollments.append({
            'id': enrollment.id,
            'user': enrollment.user.nickname,
            'username': enrollment.user.username,
            'previous_role': enrollment.previous_role,
            'new_role': enrollment.new_role,
            'tokens_granted': enrollment.tokens_granted,
            'enrolled_at': enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': enrollment.ip_address
        })
    
    return jsonify({
        'success': True,
        'course_name': course.course_name,
        'enrollments': enrollments
    })


@admin_bp.route('/token-recharge-stats')
@login_required
@admin_required
def token_recharge_stats():
    """松果币充值统计页面"""
    return render_template('admin/token_recharge_stats.html')


@admin_bp.route('/token-recharge-stats/data')
@login_required
@admin_required
def get_token_recharge_stats():
    """获取松果币充值统计数据"""
    period = request.args.get('period', 'month')  # month, year
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    now = datetime.utcnow()
    
    # 确定统计时间范围
    if period == 'month':
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    else:  # year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    
    # 1. 获取本期月度充值统计（仅教师和管理员）
    if period == 'month':
        monthly_grants = MonthlyTokenGrant.query.filter(
            MonthlyTokenGrant.grant_year == year,
            MonthlyTokenGrant.grant_month == month
        ).all()
    else:
        monthly_grants = MonthlyTokenGrant.query.filter(
            MonthlyTokenGrant.grant_year == year
        ).all()
    
    monthly_grant_data = []
    total_monthly = 0
    for grant in monthly_grants:
        user = grant.user
        monthly_grant_data.append({
            'id': grant.id,
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'role': user.role,
            'tokens_amount': grant.tokens_amount,
            'granted_at': grant.granted_at.isoformat(),
            'year_month': f'{grant.grant_year}-{grant.grant_month:02d}'
        })
        total_monthly += grant.tokens_amount
    
    # 2. 获取过期币统计
    expired_records = TokenExpiry.query.filter(
        TokenExpiry.created_at >= start_date,
        TokenExpiry.created_at < end_date,
        TokenExpiry.is_expired == True
    ).all()
    
    expired_data = []
    total_expired = 0
    for expiry in expired_records:
        user = expiry.user
        expired_data.append({
            'id': expiry.id,
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'tokens_amount': expiry.tokens_amount,
            'grant_source': expiry.grant_source,
            'expire_date': expiry.expire_date.isoformat(),
            'expired_at': expiry.expired_at.isoformat() if expiry.expired_at else None,
            'created_at': expiry.created_at.isoformat()
        })
        total_expired += expiry.tokens_amount
    
    # 3. 获取待过期币（未失效）
    pending_expiry = TokenExpiry.query.filter(
        TokenExpiry.is_expired == False,
        TokenExpiry.expire_date <= now + timedelta(days=7)
    ).all()
    
    pending_data = []
    for expiry in pending_expiry:
        user = expiry.user
        days_left = (expiry.expire_date - now).days
        pending_data.append({
            'id': expiry.id,
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'tokens_amount': expiry.tokens_amount,
            'expire_date': expiry.expire_date.isoformat(),
            'days_left': max(0, days_left),
            'created_at': expiry.created_at.isoformat()
        })
    
    # 4. 统计各角色的充值情况
    role_stats = {}
    for grant in monthly_grants:
        role = grant.user.role
        if role not in role_stats:
            role_stats[role] = {'count': 0, 'total': 0}
        role_stats[role]['count'] += 1
        role_stats[role]['total'] += grant.tokens_amount
    
    # 5. 获取充值趋势（按日期）
    if period == 'month':
        trend_data = db.session.query(
            func.date(MonthlyTokenGrant.granted_at).label('date'),
            func.count(MonthlyTokenGrant.id).label('count'),
            func.sum(MonthlyTokenGrant.tokens_amount).label('total')
        ).filter(
            MonthlyTokenGrant.granted_at >= start_date,
            MonthlyTokenGrant.granted_at < end_date
        ).group_by(func.date(MonthlyTokenGrant.granted_at)).all()
    else:
        trend_data = db.session.query(
            func.strftime('%Y-%m', MonthlyTokenGrant.granted_at).label('date'),
            func.count(MonthlyTokenGrant.id).label('count'),
            func.sum(MonthlyTokenGrant.tokens_amount).label('total')
        ).filter(
            MonthlyTokenGrant.granted_at >= start_date,
            MonthlyTokenGrant.granted_at < end_date
        ).group_by(func.strftime('%Y-%m', MonthlyTokenGrant.granted_at)).all()
    
    trend_list = []
    for td in trend_data:
        trend_list.append({
            'date': td.date.isoformat() if hasattr(td.date, 'isoformat') else str(td.date),
            'count': td.count,
            'total': td.total
        })
    
    # 6. 获取二维码赠送币统计
    qr_grants = TokenGrantLog.query.filter(
        TokenGrantLog.grant_type == 'sunguo_qrcode',
        TokenGrantLog.created_at >= start_date,
        TokenGrantLog.created_at < end_date
    ).all()
    
    qr_grant_data = []
    total_qr = 0
    for grant in qr_grants:
        user = grant.user
        qr_grant_data.append({
            'id': grant.id,
            'user_id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'tokens': grant.tokens_granted,
            'source': grant.related_info,
            'created_at': grant.created_at.isoformat()
        })
        total_qr += grant.tokens_granted
    
    return jsonify({
        'period': period,
        'year': year,
        'month': month if period == 'month' else None,
        'monthly_grants': {
            'data': monthly_grant_data,
            'count': len(monthly_grants),
            'total': total_monthly
        },
        'expired_records': {
            'data': expired_data,
            'count': len(expired_records),
            'total': total_expired
        },
        'pending_expiry': {
            'data': pending_data,
            'count': len(pending_data)
        },
        'role_stats': role_stats,
        'trend': trend_list,
        'qr_grants': {
            'data': qr_grant_data[:50],  # 最近50条
            'count': len(qr_grants),
            'total': total_qr
        }
    })


@admin_bp.route('/token-recharge-stats/export')
@login_required
@admin_required
def export_token_recharge_stats():
    """导出充值统计数据（CSV格式）"""
    import csv
    from io import StringIO
    from flask import send_file
    
    period = request.args.get('period', 'month')
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # 确定统计时间范围
    if period == 'month':
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    
    # 获取月度充值数据
    monthly_grants = MonthlyTokenGrant.query.filter(
        MonthlyTokenGrant.granted_at >= start_date,
        MonthlyTokenGrant.granted_at < end_date
    ).all()
    
    # 创建CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['用户名', '昵称', '角色', '充值金额', '充值时间'])
    
    for grant in monthly_grants:
        writer.writerow([
            grant.user.username,
            grant.user.nickname,
            grant.user.role,
            grant.tokens_amount,
            grant.granted_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Disposition': f'attachment;filename=token_recharge_{year}_{month:02d}.csv',
        'Content-Type': 'text/csv'
    }
