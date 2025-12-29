"""
二维码系统路由
- 生成课程二维码（教师/管理员）
- 扫描二维码升级账户（学生）
"""

import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, send_file, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.course_config.courses import get_course, get_courses_for_qr
from auth.models import Course, CourseEnrollment, User, db
from auth.permissions import admin_required, teacher_required

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')


@qr_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_qrcode():
    """
    生成课程二维码页面
    只有教师和管理员可以访问
    """
    if current_user.role not in ['teacher', 'admin']:
        flash('此功能仅限教师和管理员使用', 'error')
        return redirect(url_for('main.index'))
    
    # 从统一配置获取课程列表
    lessons = get_courses_for_qr()
    
    if request.method == 'POST':
        course_type = request.form.get('course_type')  # 'trial_course' 或 'formal_course'
        course_key = request.form.get('course_name')  # 课程key（从下拉框选择）
        max_uses = request.form.get('max_uses')  # 最大使用次数
        expires_days = request.form.get('expires_days')  # 有效天数
        description = request.form.get('description', '')  # 课程描述
        
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
            'qr_url': f'/static/qrcodes/{qr_filename}',
            'scan_url': scan_url,
            'course_code': course_code,
            'course_type': course_type,
            'course_name': course_name,
            'max_uses': max_uses_int if max_uses_int else '无限制',
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else '永久有效'
        })
    
    return render_template('qr/generate.html', lessons=lessons)


@qr_bp.route('/scan/<code>')
@login_required
def scan(code):
    """
    扫描二维码升级账户
    根据课程类型自动升级用户权限
    """
    # 从数据库查找课程
    course = Course.query.filter_by(course_code=code).first()
    
    if not course:
        flash('❌ 无效的课程二维码', 'error')
        return redirect(url_for('main.index'))
    
    # 检查课程是否有效
    is_valid, message = course.is_valid()
    if not is_valid:
        flash(f'❌ {message}', 'error')
        return redirect(url_for('main.index'))
    
    # 检查用户是否已经扫描过此课程
    existing_enrollment = CourseEnrollment.query.filter_by(
        course_id=course.id,
        user_id=current_user.id
    ).first()
    
    if existing_enrollment:
        flash('⚠️ 您已经扫描过此课程二维码，无法重复使用', 'warning')
        return redirect(url_for('auth.profile'))
    
    # 记录扫描前的状态
    previous_role = current_user.role
    tokens_granted = 0
    
    # 升级用户权限
    if course.course_type == 'trial_course':
        # 体验课：赠送50 token
        tokens_granted = 50
        current_user.upgrade_to_trial_student(
            additional_tokens=tokens_granted,
            course_id=course.id,
            course_name=course.course_name
        )
        flash('🎉 恭喜！您已成功报名体验课，获得50个token！', 'success')
        flash('💡 提示：体验课学生暂不支持3D建模和视频生成功能', 'info')
        
    elif course.course_type == 'formal_course':
        # 正式课程：升级为正式学生
        current_user.upgrade_to_formal_student(
            course_id=course.id,
            course_name=course.course_name
        )
        flash('🎉 恭喜！您已升级为正式学生！', 'success')
        flash('✨ 您现在可以使用3D建模和视频生成功能，并且每天自动获得30个token！', 'success')
    
    # 记录报名信息
    enrollment = CourseEnrollment(
        course_id=course.id,
        user_id=current_user.id,
        previous_role=previous_role,
        new_role=current_user.role,
        tokens_granted=tokens_granted,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(enrollment)
    
    # 增加课程使用次数
    course.increment_usage()
    
    return redirect(url_for('auth.profile'))


@qr_bp.route('/list')
@login_required
def list_qrcodes():
    """
    查看已生成的所有二维码
    只有教师和管理员可以访问
    """
    if current_user.role not in ['teacher', 'admin']:
        flash('此功能仅限教师和管理员使用', 'error')
        return redirect(url_for('main.index'))
    
    # 从数据库获取所有课程（按创建时间倒序）
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
            'is_valid': valid,
            'validation_message': msg,
            'is_active': course.is_active,
            'stats': stats,
            'description': course.description or '无描述',
            'enrollments_count': len(course.enrollments)
        })
    
    return render_template('qr/list.html', courses=courses_data)


@qr_bp.route('/download/<filename>')
@login_required
def download_qrcode(filename):
    """
    下载二维码图片
    """
    if current_user.role not in ['teacher', 'admin']:
        flash('此功能仅限教师和管理员使用', 'error')
        return redirect(url_for('main.index'))
    
    qr_path = os.path.join('static/qrcodes', secure_filename(filename))
    if not os.path.exists(qr_path):
        flash('二维码不存在', 'error')
        return redirect(url_for('qr.list_qrcodes'))
    
    return send_file(qr_path, as_attachment=True)

@qr_bp.route('/sunguo-lesson', methods=['POST'])
@login_required
def generate_sunguo_lesson_qrcode():
    """
    生成松果课堂课程二维码
    仅教师和管理员可用
    支持：最大使用次数、有效期、赠送松果币
    """
    if current_user.role not in ['teacher', 'admin']:
        return jsonify({'error': '此功能仅限教师和管理员使用'}), 403
    
    data = request.get_json()
    lesson_key = data.get('lesson_key')
    lesson_title = data.get('lesson_title')
    max_uses = data.get('max_uses')
    expires_days = data.get('expires_days')
    tokens_reward = data.get('tokens_reward', 0)
    
    if not lesson_key or not lesson_title:
        return jsonify({'error': '课程信息不完整'}), 400
    
    # 处理使用次数限制
    max_uses_int = None
    if max_uses and str(max_uses).strip():
        try:
            max_uses_int = int(max_uses)
            if max_uses_int <= 0:
                return jsonify({'error': '使用次数必须大于0'}), 400
        except ValueError:
            return jsonify({'error': '使用次数必须是数字'}), 400
    
    # 处理过期时间
    expires_at = None
    if expires_days and str(expires_days).strip():
        try:
            days = int(expires_days)
            if days <= 0:
                return jsonify({'error': '有效天数必须大于0'}), 400
            expires_at = datetime.utcnow() + timedelta(days=days)
        except ValueError:
            return jsonify({'error': '有效天数必须是数字'}), 400
    
    # 处理赠送松果币
    tokens_reward_int = 0
    if tokens_reward and str(tokens_reward).strip():
        try:
            tokens_reward_int = int(tokens_reward)
            if tokens_reward_int < 0:
                return jsonify({'error': '赠送松果币数量不能为负'}), 400
        except ValueError:
            return jsonify({'error': '赠送松果币数量必须是数字'}), 400
    
    # 生成唯一的课程代码
    course_code = str(uuid.uuid4())
    
    # 生成扫描URL
    scan_url = url_for('qr.scan_sunguo_lesson', code=course_code, _external=True)
    
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
    qr_filename = f'sunguo_{lesson_key}_{course_code}.png'
    qr_path = os.path.join(qr_dir, qr_filename)
    img.save(qr_path)
    
    # 在数据库中记录二维码信息
    course = Course(
        course_code=course_code,
        course_name=lesson_title,
        course_key=lesson_key,
        course_type='trial_course',
        created_by=current_user.id,
        max_uses=max_uses_int,
        expires_at=expires_at,
        tokens_reward=tokens_reward_int,
        description=data.get('description', '')
    )
    course.qr_image_path = qr_path
    db.session.add(course)
    db.session.commit()
    
    # 生成可下载链接
    download_url = url_for('qr.download_qrcode', filename=qr_filename)
    
    # 构建有效期信息字符串
    validity_info = '永久有效'
    if expires_at:
        validity_info = f"有效期至 {expires_at.strftime('%Y年%m月%d日')}"
    
    return jsonify({
        'success': True,
        'qr_code_url': f'/static/qrcodes/{qr_filename}',
        'download_url': download_url,
        'lesson_key': lesson_key,
        'lesson_title': lesson_title,
        'max_uses': max_uses_int,
        'expires_at': expires_at.isoformat() if expires_at else None,
        'validity_info': validity_info,
        'tokens_reward': tokens_reward_int
    })


@qr_bp.route('/scan-sunguo/<code>')
def scan_sunguo_lesson(code):
    """
    扫描松果课堂课程二维码
    如果用户已登录，自动赠送松果币
    显示课程信息和跳转选项
    """
    # 查找二维码对应的课程
    course = Course.query.filter_by(course_code=code).first()
    
    if not course:
        flash('二维码不存在或已失效', 'error')
        return redirect(url_for('main.index'))
    
    # 检查二维码是否有效
    valid, msg = course.is_valid()
    
    reward_info = {
        'success': False,
        'message': '未登录',
        'tokens_added': 0
    }
    
    # 如果用户已登录，处理赠送松果币
    if current_user.is_authenticated:
        # 1. 身份验证：检查是否为正式报名的学生
        from auth.models import CourseEnrollment
        
        # 根据课程类型判断领取资格
        can_claim = False
        identity_message = ''
        
        if course.course_type == 'trial_course':
            # 试用课程：游客和学生都可以领取
            can_claim = True
        elif course.course_type == 'formal_course':
            # 正式课程：仅正式报名学生可以领取
            if current_user.role == 'student' and current_user.is_enrolled:
                can_claim = True
                identity_message = f'正式学生 {current_user.nickname}'
            elif current_user.role == 'teacher' or current_user.role == 'admin':
                can_claim = True
                identity_message = f'教师 {current_user.nickname}'
            else:
                identity_message = f'{current_user.nickname}（未报名）'
        
        # 2. 检查是否已经扫过此二维码
        existing = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        if existing:
            reward_info['message'] = '您已扫过此二维码'
            reward_info['tokens_added'] = 0
        elif not can_claim:
            reward_info['message'] = '仅正式报名学生可领取本课程奖励。请先报名课程'
            reward_info['tokens_added'] = 0
        elif valid:
            # 赠送松果币（使用新的带过期时间的方法）
            if course.tokens_reward > 0:
                current_user.add_temporary_tokens(
                    amount=course.tokens_reward,
                    source=f'sunguo_qrcode_{course.id}',
                    expire_days=30
                )
            
            # 创建课程选修记录
            enrollment = CourseEnrollment(
                user_id=current_user.id,
                course_id=course.id,
                enrolled_at=datetime.utcnow()
            )
            course.increment_usage()
            db.session.add(enrollment)
            db.session.commit()
            
            reward_info['success'] = True
            reward_info['message'] = '松果币已赠送！'
            reward_info['tokens_added'] = course.tokens_reward
        else:
            reward_info['message'] = msg
        
        # 记录用户身份信息用于前端显示
        reward_info['user_identity'] = identity_message
    else:
        reward_info['user_identity'] = ''
    
    return render_template('qr/sunguo_lesson_qr.html', 
                         code=code,
                         course=course,
                         valid=valid,
                         validity_msg=msg,
                         reward_info=reward_info,
                         user_identity=reward_info.get('user_identity', ''))