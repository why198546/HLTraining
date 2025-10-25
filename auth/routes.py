"""
用户认证路由
处理注册、登录、验证等功能
"""

from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import random
import string
from models import db

from auth import auth_bp
from models import db, User, ParentVerification, CreationSession
from forms import KidRegistrationForm, KidLoginForm, ParentVerificationForm
from utils.email_service import send_verification_email


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """儿童用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = KidRegistrationForm()
    
    if form.validate_on_submit():
        # 创建新用户
        user = User(
            username=form.username.data,
            nickname=form.nickname.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            parent_email=form.parent_email.data,
            password=form.password.data,
            contact_phone=form.contact_phone.data,
            mailing_address=form.mailing_address.data
        )
        user.role = form.role.data
        user.color_preference = form.color_preference.data
        
        db.session.add(user)
        db.session.commit()
        
        # 发送家长验证邮件
        send_parent_verification(user)
        
        flash('注册成功！请查看家长邮箱完成验证后即可登录。', 'success')
        return redirect(url_for('auth.verification_pending', user_id=user.id))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = KidLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_verified:
                flash('账户尚未通过家长验证，请联系家长完成验证。', 'warning')
                return redirect(url_for('auth.verification_pending', user_id=user.id))
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # 记录登录日志
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.nickname}！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    flash(f'再见，{current_user.nickname}！', 'info')
    logout_user()
    return redirect(url_for('index'))


@auth_bp.route('/verification-pending/<int:user_id>')
def verification_pending(user_id):
    """等待家长验证页面"""
    user = User.query.get_or_404(user_id)
    return render_template('auth/verification_pending.html', user=user)


@auth_bp.route('/parent-verify/<verification_token>', methods=['GET', 'POST'])
def parent_verify(verification_token):
    """家长验证页面"""
    user = User.query.filter_by(verification_token=verification_token).first()
    if not user:
        flash('验证链接无效或已过期', 'error')
        return redirect(url_for('index'))
    
    if user.is_verified:
        flash('账户已经通过验证', 'info')
        return redirect(url_for('index'))
    
    form = ParentVerificationForm()
    
    if form.validate_on_submit():
        # 查找验证记录
        verification = ParentVerification.query.filter_by(
            user_id=user.id,
            verification_code=form.verification_code.data,
            is_verified=False
        ).first()
        
        if verification and not verification.is_expired():
            # 验证成功
            verification.verify()
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            
            flash('验证成功！孩子现在可以正常使用账户了。', 'success')
            return render_template('auth/verification_success.html', user=user)
        else:
            flash('验证码错误或已过期，请重新发送验证邮件', 'error')
    
    return render_template('auth/parent_verify.html', form=form, user=user)


@auth_bp.route('/resend-verification/<int:user_id>')
def resend_verification(user_id):
    """重新发送验证邮件"""
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        flash('账户已经通过验证', 'info')
        return redirect(url_for('index'))
    
    # 检查是否在短时间内重复发送
    recent_verification = ParentVerification.query.filter_by(
        user_id=user.id
    ).order_by(ParentVerification.created_at.desc()).first()
    
    if recent_verification and (datetime.utcnow() - recent_verification.created_at).seconds < 60:
        flash('验证邮件发送过于频繁，请稍后再试', 'warning')
        return redirect(url_for('auth.verification_pending', user_id=user_id))
    
    send_parent_verification(user)
    flash('验证邮件已重新发送，请查看家长邮箱', 'success')
    return redirect(url_for('auth.verification_pending', user_id=user_id))


def send_parent_verification(user):
    """发送家长验证邮件"""
    # 生成6位验证码
    verification_code = ''.join(random.choices(string.digits, k=6))
    
    # 创建验证记录
    verification = ParentVerification(
        user_id=user.id,
        parent_email=user.parent_email,
        verification_code=verification_code,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.session.add(verification)
    db.session.commit()
    
    # 发送邮件
    verification_url = url_for('auth.parent_verify', 
                             verification_token=user.verification_token, 
                             _external=True)
    
    try:
        send_verification_email(
            to_email=user.parent_email,
            child_name=user.nickname,
            verification_code=verification_code,
            verification_url=verification_url
        )
        current_app.logger.info(f"验证邮件已发送到 {user.parent_email}")
    except Exception as e:
        current_app.logger.error(f"发送验证邮件失败: {str(e)}")
        flash('发送验证邮件失败，请稍后重试', 'error')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户个人中心"""
    print("DEBUG: Profile function called")
    from models import Artwork, CreationSession
    from datetime import datetime
    from forms import ProfileUpdateForm, PrivacySettingsForm
    
    # 创建表单实例
    form = ProfileUpdateForm()
    privacy_form = PrivacySettingsForm()
    print(f"DEBUG: Form created: {form}")
    print(f"DEBUG: Privacy form created: {privacy_form}")
    
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        print(f"DEBUG: Form type: {form_type}")
        print(f"DEBUG: Form data: {request.form}")
        print(f"DEBUG: Form validation result: {form.validate_on_submit()}")
        if not form.validate_on_submit():
            print(f"DEBUG: Form errors: {form.errors}")
        
        if form_type == 'profile' and form.validate_on_submit():
            print("DEBUG: Processing profile update")
            # 处理个人资料更新
            old_nickname = current_user.nickname
            old_role = current_user.role
            current_user.nickname = form.nickname.data
            current_user.role = form.role.data
            current_user.birth_date = form.birth_date.data
            current_user.gender = form.gender.data
            current_user.contact_phone = form.contact_phone.data
            current_user.mailing_address = form.mailing_address.data
            current_user.color_preference = form.color_preference.data
            # bio字段暂时不保存，因为User模型中没有bio字段
            print(f"DEBUG: Updating nickname from '{old_nickname}' to '{form.nickname.data}'")
            print(f"DEBUG: Updating role from '{old_role}' to '{form.role.data}'")
            
            try:
                db.session.commit()
                # 刷新当前用户对象，确保会话中的信息是最新的
                db.session.refresh(current_user)
                flash('资料更新成功！', 'success')
                print(f"DEBUG: Profile updated successfully. New nickname: {current_user.nickname}")
            except Exception as e:
                db.session.rollback()
                flash('更新失败，请重试', 'error')
                print(f"DEBUG: Profile update error: {e}")
            
            return redirect(url_for('auth.profile'))
            
        elif form_type == 'privacy' and privacy_form.validate_on_submit():
            # 处理隐私设置更新
            if hasattr(current_user, 'privacy_settings') and current_user.privacy_settings:
                privacy_settings = current_user.privacy_settings
            else:
                privacy_settings = {}
            
            privacy_settings.update({
                'show_in_gallery': privacy_form.show_in_gallery.data,
                'show_age': privacy_form.show_age.data,
                'allow_parent_reports': privacy_form.allow_parent_reports.data
            })
            
            current_user.privacy_settings = privacy_settings
            
            try:
                db.session.commit()
                flash('隐私设置更新成功！', 'success')
            except Exception as e:
                db.session.rollback()
                flash('隐私设置更新失败，请重试', 'error')
            
            return redirect(url_for('auth.profile'))
    
    # 为表单设置当前值
    if request.method == 'GET':
        form.nickname.data = current_user.nickname
        form.role.data = getattr(current_user, 'role', 'student')  # 默认为学生
        form.birth_date.data = getattr(current_user, 'birth_date', None)
        form.gender.data = getattr(current_user, 'gender', '')
        form.contact_phone.data = getattr(current_user, 'contact_phone', '')
        form.mailing_address.data = getattr(current_user, 'mailing_address', '')
        form.bio.data = ''  # 暂时设为空，因为User模型中没有bio字段
        form.color_preference.data = current_user.color_preference
        
        # 设置隐私表单的当前值
        if hasattr(current_user, 'privacy_settings') and current_user.privacy_settings:
            privacy_settings = current_user.privacy_settings
            privacy_form.show_in_gallery.data = privacy_settings.get('show_in_gallery', True)
            privacy_form.show_age.data = privacy_settings.get('show_age', False)
            privacy_form.allow_parent_reports.data = privacy_settings.get('allow_parent_reports', True)
        else:
            # 使用默认值
            privacy_form.show_in_gallery.data = True
            privacy_form.show_age.data = False
            privacy_form.allow_parent_reports.data = True
    
    # 获取用户统计数据
    artwork_count = current_user.get_artwork_count()
    total_time = current_user.get_total_creation_time()
    
    # 计算加入天数
    if current_user.created_at:
        days_joined = (datetime.utcnow() - current_user.created_at).days
    else:
        days_joined = 0
    
    # 计算创作会话数
    session_count = CreationSession.query.filter_by(user_id=current_user.id).count()
    
    # 获取最近的作品
    recent_artworks = Artwork.query.filter_by(user_id=current_user.id).order_by(
        Artwork.created_at.desc()
    ).limit(6).all()
    
    return render_template('auth/profile.html', 
                         form=form,
                         privacy_form=privacy_form,
                         user=current_user,
                         artwork_count=artwork_count,
                         total_time=total_time,
                         recent_artworks=recent_artworks,
                         days_joined=days_joined,
                         session_count=session_count)


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    from forms import ProfileUpdateForm
    
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.color_preference = form.color_preference.data
        
        try:
            db.session.commit()
            # 刷新当前用户对象，确保会话中的信息是最新的
            db.session.refresh(current_user)
            flash('个人资料更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')
            print(f"DEBUG: Edit profile error: {e}")
        
        return redirect(url_for('auth.profile'))
    
    # 预填充表单
    form.nickname.data = current_user.nickname
    form.color_preference.data = current_user.color_preference
    
    return render_template('auth/edit_profile.html', form=form)


@auth_bp.route('/my-artworks')
@login_required
def my_artworks():
    """我的作品页面"""
    from models import Artwork
    from sqlalchemy import func
    
    page = request.args.get('page', 1, type=int)
    pagination = Artwork.query.filter_by(user_id=current_user.id).order_by(
        Artwork.created_at.desc()
    ).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # 计算统计信息
    total_likes = db.session.query(func.sum(Artwork.vote_count)).filter_by(user_id=current_user.id).scalar() or 0
    total_views = db.session.query(func.sum(Artwork.view_count)).filter_by(user_id=current_user.id).scalar() or 0
    
    # 按类型统计作品数量（基于是否有相应文件）
    total_artworks = Artwork.query.filter_by(user_id=current_user.id).count()
    public_artworks = Artwork.query.filter_by(user_id=current_user.id, is_public=True).count()
    featured_artworks = Artwork.query.filter_by(user_id=current_user.id, is_featured=True).count()
    
    return render_template('auth/my_artworks.html', 
                         artworks=pagination, 
                         pagination=pagination,
                         total_likes=total_likes,
                         total_views=total_views,
                         total_artworks=total_artworks,
                         public_artworks=public_artworks,
                         featured_artworks=featured_artworks)


@auth_bp.route('/privacy-settings', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    """隐私设置"""
    from forms import PrivacySettingsForm
    
    form = PrivacySettingsForm()
    
    if form.validate_on_submit():
        # 更新隐私设置
        privacy_settings = {
            'show_in_gallery': form.show_in_gallery.data,
            'allow_sharing': form.allow_sharing.data,
            'receive_notifications': form.receive_notifications.data
        }
        current_user.privacy_settings = privacy_settings
        db.session.commit()
        
        flash('隐私设置已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    # 预填充表单
    if current_user.privacy_settings:
        form.show_in_gallery.data = current_user.privacy_settings.get('show_in_gallery', True)
        form.allow_sharing.data = current_user.privacy_settings.get('allow_sharing', True)
        form.receive_notifications.data = current_user.privacy_settings.get('receive_notifications', True)
    
    return render_template('auth/privacy_settings.html', form=form)


@auth_bp.route('/parent-dashboard/<verification_token>')
def parent_dashboard(verification_token):
    """家长监护面板"""
    user = User.query.filter_by(verification_token=verification_token).first()
    if not user:
        flash('访问链接无效', 'error')
        return redirect(url_for('index'))
    
    # 获取孩子的活动统计
    stats = {
        'total_artworks': user.get_artwork_count(),
        'total_time': user.get_total_creation_time(),
        'last_login': user.last_login,
        'account_created': user.created_at
    }
    
    # 获取最近的创作活动
    from models import CreationSession, Artwork
    from datetime import datetime, timedelta
    recent_sessions = CreationSession.query.filter_by(user_id=user.id).order_by(
        CreationSession.started_at.desc()
    ).limit(10).all()
    
    # 获取孩子的作品（不是分页对象，而是简单的列表）
    child_artworks = Artwork.query.filter_by(user_id=user.id).order_by(
        Artwork.created_at.desc()
    ).all()
    
    # 计算使用趋势（简单的计算：比较最近7天和前7天的活动）
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    recent_week_count = CreationSession.query.filter_by(user_id=user.id).filter(
        CreationSession.started_at >= week_ago
    ).count()
    
    previous_week_count = CreationSession.query.filter_by(user_id=user.id).filter(
        CreationSession.started_at >= two_weeks_ago,
        CreationSession.started_at < week_ago
    ).count()
    
    # 计算趋势
    usage_trend = 0
    if previous_week_count > 0:
        usage_trend = recent_week_count - previous_week_count
    elif recent_week_count > 0:
        usage_trend = 1
    
    # 生成每日使用数据（过去7天）
    daily_usage_data = []
    for i in range(7):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        day_count = CreationSession.query.filter_by(user_id=user.id).filter(
            CreationSession.started_at >= day_start,
            CreationSession.started_at <= day_end
        ).count()
        
        daily_usage_data.append({
            'date': day.strftime('%m-%d'),
            'count': day_count
        })
    
    # 反转列表以显示从最早到最新
    daily_usage_data.reverse()
    
    return render_template('auth/parent_dashboard.html', 
                         child=user, 
                         stats=stats,
                         recent_sessions=recent_sessions,
                         child_artworks=child_artworks,
                         usage_trend=usage_trend,
                         daily_usage_data=daily_usage_data)