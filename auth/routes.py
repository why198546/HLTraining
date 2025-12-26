"""
用户认证路由
处理注册、登录、验证等功能
"""

import random
import string
from datetime import datetime, timedelta

from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from auth import auth_bp
from auth.forms import (KidLoginForm, KidRegistrationForm,
                        ParentVerificationForm)
from auth.models import CreationSession, ParentVerification, User, db
from utils.email_service import send_verification_email


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """儿童用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = KidRegistrationForm()
    
    if form.validate_on_submit():
        # 创建新用户
        user = User(
            username=form.username.data,
            nickname=form.nickname.data,
            parent_email=form.parent_email.data,
            password=form.password.data,
            birth_date=form.birth_date.data if form.birth_date.data else None,
            gender=form.gender.data if form.gender.data else None,
            contact_phone=form.contact_phone.data if form.contact_phone.data else None,
            mailing_address=form.mailing_address.data if form.mailing_address.data else None
        )
        user.role = form.role.data
        user.color_preference = form.color_preference.data if form.color_preference.data else 'warm'
        
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
        return redirect(url_for('main.index'))
    
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
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    flash(f'再见，{current_user.nickname}！', 'info')
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/verification-pending/<int:user_id>')
def verification_pending(user_id):
    """等待家长验证页面"""
    user = User.query.get_or_404(user_id)
    return render_template('auth/verification_pending.html', user=user)


@auth_bp.route('/parent-verify/<verification_token>', methods=['GET', 'POST'])
def parent_verify(verification_token):
    """家长验证页面"""
    try:
        user = User.query.filter_by(verification_token=verification_token).first()
        if not user:
            flash('验证链接无效或已过期', 'error')
            return redirect(url_for('main.index'))
        
        if user.is_verified:
            flash('账户已经通过验证', 'info')
            return redirect(url_for('main.index'))
        
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
        elif request.method == 'POST':
            # 表单验证失败，显示具体错误
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{error}', 'error')
        
        return render_template('auth/parent_verify.html', form=form, user=user)
    except Exception as e:
        # 捕获所有异常并记录
        import traceback
        error_msg = f"Error in parent_verify: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # 打印到gunicorn日志
        flash(f'系统错误：{str(e)}', 'error')
        return render_template('auth/parent_verify.html', form=ParentVerificationForm(), user=user if 'user' in locals() else None)


@auth_bp.route('/resend-verification/<int:user_id>')
def resend_verification(user_id):
    """重新发送验证邮件"""
    user = User.query.get_or_404(user_id)
    
    if user.is_verified:
        flash('账户已经通过验证', 'info')
        return redirect(url_for('main.index'))
    
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
    from datetime import datetime

    from auth.forms import PrivacySettingsForm, ProfileUpdateForm
    from auth.models import Artwork, CreationSession

    # 创建表单实例
    form = ProfileUpdateForm()
    privacy_form = PrivacySettingsForm()
    print(f"DEBUG: Form created: {form}")
    print(f"DEBUG: Privacy form created: {privacy_form}")
    
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        print("=" * 50)
        print("DEBUG: POST REQUEST RECEIVED")
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Request path: {request.path}")
        form_type = request.form.get('form_type')
        print(f"DEBUG: Form type: {form_type}")
        print(f"DEBUG: Form data: {dict(request.form)}")
        print("=" * 50)
        
        if form_type == 'profile' and form.validate_on_submit():
            print("DEBUG: Processing profile update")
            # 处理个人资料更新
            old_nickname = current_user.nickname
            current_user.nickname = form.nickname.data
            # 安全措施：禁止用户自己修改角色，角色只能由管理员通过后台修改
            # current_user.role = form.role.data  # 已禁用
            current_user.birth_date = form.birth_date.data
            current_user.gender = form.gender.data
            current_user.contact_phone = form.contact_phone.data
            current_user.mailing_address = form.mailing_address.data
            current_user.color_preference = form.color_preference.data
            # bio字段暂时不保存，因为User模型中没有bio字段
            print(f"DEBUG: Updating nickname from '{old_nickname}' to '{form.nickname.data}'")
            
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
            
        elif form_type == 'privacy':
            print("DEBUG: Processing privacy update")
            # 直接从request.form读取值，因为我们使用了自定义的隐藏input
            show_in_gallery = request.form.get('show_in_gallery', 'n') == 'y'
            show_age = request.form.get('show_age', 'n') == 'y'
            allow_parent_reports = request.form.get('allow_parent_reports', 'y') == 'y'
            
            print(f"DEBUG: Privacy values: show_in_gallery={show_in_gallery}, show_age={show_age}, allow_parent_reports={allow_parent_reports}")
            
            # 处理隐私设置更新 - 创建新字典来触发SQLAlchemy的change tracking
            privacy_settings = {
                'show_in_gallery': show_in_gallery,
                'show_age': show_age,
                'allow_parent_reports': allow_parent_reports
            }
            
            # 直接赋值新字典，确保SQLAlchemy检测到变化
            current_user.privacy_settings = privacy_settings
            
            # 使用flag_modified确保SQLAlchemy知道这个字段已修改
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(current_user, 'privacy_settings')
            
            try:
                db.session.commit()
                print(f"DEBUG: Privacy settings committed successfully: {current_user.privacy_settings}")
                # 如果是AJAX请求，返回JSON响应
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'multipart/form-data':
                    from flask import jsonify
                    return jsonify({'success': True, 'message': '隐私设置更新成功！'})
                flash('隐私设置更新成功！', 'success')
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG: Privacy settings commit error: {e}")
                # 如果是AJAX请求，返回JSON响应
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'multipart/form-data':
                    from flask import jsonify
                    return jsonify({'success': False, 'message': '隐私设置更新失败，请重试'}), 400
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
    from auth.forms import ProfileUpdateForm
    
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
    """我的作品页面 - 支持家长查看孩子作品"""
    from sqlalchemy import func
    from auth.models import Artwork, User
    
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', type=int)
    
    # 确定要查看的用户
    if user_id:
        # 家长查看孩子作品 - 需要验证权限
        target_user = User.query.get_or_404(user_id)
        
        # 检查权限：只有家长可以查看孩子的作品
        if current_user.role != 'parent':
            flash('无权访问', 'error')
            return redirect(url_for('auth.my_artworks'))
        
        # 验证是否是该家长的孩子
        if target_user.parent_id != current_user.id:
            flash('无权访问该用户的作品', 'error')
            return redirect(url_for('auth.parent_dashboard'))
        
        viewing_user = target_user
    else:
        # 查看自己的作品
        viewing_user = current_user
    
    # 获取所有作品（不分页，和gallery保持一致的体验）
    artworks = Artwork.query.filter_by(user_id=viewing_user.id).order_by(
        Artwork.created_at.desc()
    ).all()
    
    # 计算统计信息
    total_likes = db.session.query(func.sum(Artwork.vote_count)).filter_by(user_id=viewing_user.id).scalar() or 0
    total_views = db.session.query(func.sum(Artwork.view_count)).filter_by(user_id=viewing_user.id).scalar() or 0
    
    # 按类型统计作品数量
    total_artworks = len(artworks)
    public_artworks = Artwork.query.filter_by(user_id=viewing_user.id, is_public=True).count()
    featured_artworks = Artwork.query.filter_by(user_id=viewing_user.id, is_featured=True).count()
    
    # 按分类统计（基于文件类型）
    ai_coloring_count = sum(1 for a in artworks if a.colored_image)
    model_3d_count = sum(1 for a in artworks if a.model_3d)
    video_count = sum(1 for a in artworks if a.video_file)
    
    return render_template('auth/my_artworks.html', 
                         artworks=artworks,
                         total_likes=total_likes,
                         total_views=total_views,
                         total_artworks=total_artworks,
                         public_artworks=public_artworks,
                         featured_artworks=featured_artworks,
                         ai_coloring_count=ai_coloring_count,
                         model_3d_count=model_3d_count,
                         video_count=video_count,
                         viewing_user=viewing_user,
                         is_viewing_child=(user_id is not None))


@auth_bp.route('/privacy-settings', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    """隐私设置"""
    from auth.forms import PrivacySettingsForm
    
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
        return redirect(url_for('main.index'))
    
    # 获取孩子的活动统计
    stats = {
        'total_artworks': user.get_artwork_count(),
        'total_time': user.get_total_creation_time(),
        'last_login': user.last_login,
        'account_created': user.created_at
    }
    
    # 获取最近的创作活动
    from datetime import datetime, timedelta

    from auth.models import Artwork, CreationSession
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


@auth_bp.route('/artwork/<int:artwork_id>/update-title', methods=['POST'])
@login_required
def update_artwork_title(artwork_id):
    """更新作品标题"""
    from auth.models import Artwork
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 检查权限：只能编辑自己的作品
    if artwork.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限编辑此作品'}), 403
    
    data = request.get_json()
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({'success': False, 'message': '标题不能为空'}), 400
    
    if len(new_title) > 100:
        return jsonify({'success': False, 'message': '标题不能超过100个字符'}), 400
    
    artwork.title = new_title
    db.session.commit()
    
    return jsonify({'success': True, 'message': '标题已更新', 'new_title': new_title})


@auth_bp.route('/artwork/<int:artwork_id>/generate-model', methods=['POST'])
@login_required
def generate_artwork_model(artwork_id):
    """为作品生成3D模型"""
    from auth.models import Artwork
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 检查权限：只能为自己的作品生成模型
    if artwork.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限操作此作品'}), 403
    
    data = request.get_json()
    image_url = data.get('image_url')
    
    if not image_url:
        return jsonify({'success': False, 'message': '缺少图片URL'}), 400
    
    # TODO: 实现3D模型生成逻辑
    # 这里应该调用Hunyuan3D API生成模型
    # 暂时返回成功消息
    
    return jsonify({
        'success': True, 
        'message': '3D模型生成功能开发中，敬请期待！',
        'status': 'pending'
    })


@auth_bp.route('/artwork/<int:artwork_id>/generate-video', methods=['POST'])
@login_required
def generate_artwork_video(artwork_id):
    """为作品生成视频"""
    from auth.models import Artwork
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 检查权限：只能为自己的作品生成视频
    if artwork.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限操作此作品'}), 403
    
    data = request.get_json()
    image_url = data.get('image_url')
    
    if not image_url:
        return jsonify({'success': False, 'message': '缺少图片URL'}), 400
    
    # TODO: 实现视频生成逻辑
    # 这里应该调用视频生成API
    # 暂时返回成功消息
    
    return jsonify({
        'success': True, 
        'message': '视频生成功能开发中，敬请期待！',
        'status': 'pending'
    })


# ============================================================
# 评论相关路由
# ============================================================

@auth_bp.route('/artwork/<int:artwork_id>/comments', methods=['GET'])
def get_artwork_comments(artwork_id):
    """获取作品的所有评论"""
    from auth.models import Artwork, Comment
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 获取评论，按时间倒序
    comments = Comment.query.filter_by(
        artwork_id=artwork_id,
        is_deleted=False
    ).order_by(Comment.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'comments': [comment.to_dict() for comment in comments],
        'total': len(comments)
    })


@auth_bp.route('/artwork/<int:artwork_id>/comments', methods=['POST'])
@login_required
def create_comment(artwork_id):
    """创建评论"""
    from api.text_punctuation import add_punctuation_to_text
    from auth.models import Artwork, Comment
    
    artwork = Artwork.query.get_or_404(artwork_id)
    
    data = request.get_json()
    content = data.get('content', '').strip()
    audio_file = data.get('audio_file')
    is_voice_comment = data.get('is_voice_comment', False)
    
    if not content:
        return jsonify({'success': False, 'message': '评论内容不能为空'}), 400
    
    if len(content) > 500:
        return jsonify({'success': False, 'message': '评论内容不能超过500字'}), 400
    
    # 如果是语音评论，优化标点符号
    if is_voice_comment:
        try:
            optimized_content = add_punctuation_to_text(content)
            content = optimized_content
            print(f"语音评论标点优化: {data.get('content')[:30]}... -> {content[:30]}...")
        except Exception as e:
            print(f"标点优化失败，使用原文: {str(e)}")
            # 优化失败时使用原文
    
    # 创建评论
    comment = Comment(
        artwork_id=artwork_id,
        user_id=current_user.id,
        content=content,
        audio_file=audio_file,
        is_voice_comment=is_voice_comment
    )


@auth_bp.route('/upload-comment-audio', methods=['POST'])
@login_required
def upload_comment_audio():
    """上传评论音频文件"""
    import os

    from werkzeug.utils import secure_filename
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': '未找到音频文件'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400
    
    # 根据文件类型确定扩展名
    content_type = audio_file.content_type
    if 'webm' in content_type:
        ext = 'webm'
    elif 'ogg' in content_type:
        ext = 'ogg'
    elif 'mp4' in content_type or 'm4a' in content_type:
        ext = 'm4a'
    else:
        ext = 'webm'  # 默认
    
    # 生成唯一文件名
    timestamp = int(datetime.utcnow().timestamp())
    filename = f'comment_audio_{current_user.id}_{timestamp}.{ext}'
    
    # 保存到uploads目录
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    audio_file.save(filepath)
    
    # 验证文件已保存
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '文件保存失败'}), 500
    
    file_size = os.path.getsize(filepath)
    print(f'✅ 音频文件已保存: {filename}, 大小: {file_size} bytes')
    
    return jsonify({
        'success': True,
        'filename': filename,
        'size': file_size
    })


@auth_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """删除评论（软删除）"""
    from auth.models import Comment
    
    comment = Comment.query.get_or_404(comment_id)
    
    # 检查权限：只能删除自己的评论或自己作品的评论
    from auth.models import Artwork
    artwork = Artwork.query.get(comment.artwork_id)
    
    if comment.user_id != current_user.id and artwork.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权限删除此评论'}), 403
    
    # 软删除
    comment.is_deleted = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '评论已删除'
    })


# ============ 教师管理功能 ============

@auth_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """教师管理后台首页"""
    from auth.permissions import teacher_required

    # 检查教师权限
    if current_user.role != 'teacher':
        flash('此功能仅限老师使用', 'error')
        return redirect(url_for('main.index'))
    
    # 获取所有学生
    students = User.query.filter_by(role='student').all()
    
    # 统计信息
    total_students = len(students)
    enrolled_students = sum(1 for s in students if s.is_enrolled)
    
    return render_template('auth/teacher_dashboard.html', 
                         students=students,
                         total_students=total_students,
                         enrolled_students=enrolled_students)


@auth_bp.route('/teacher/students')
@login_required
def teacher_students():
    """学生管理页面"""
    if current_user.role != 'teacher':
        flash('此功能仅限老师使用', 'error')
        return redirect(url_for('main.index'))
    
    students = User.query.filter_by(role='student').order_by(User.created_at.desc()).all()
    return render_template('auth/teacher_students.html', students=students)


@auth_bp.route('/teacher/student/<int:student_id>')
@login_required
def teacher_student_detail(student_id):
    """查看学生详情和课程进度"""
    if current_user.role != 'teacher':
        flash('此功能仅限老师使用', 'error')
        return redirect(url_for('main.index'))
    
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        flash('该用户不是学生', 'error')
        return redirect(url_for('auth.teacher_students'))
    
    # 获取该学生的课程进度
    from auth.models import CourseProgress
    progress_list = CourseProgress.query.filter_by(user_id=student_id).order_by(CourseProgress.lesson_number).all()
    
    return render_template('auth/teacher_student_detail.html', 
                         student=student,
                         progress_list=progress_list)


@auth_bp.route('/teacher/enroll-student/<int:student_id>', methods=['POST'])
@login_required
def enroll_student(student_id):
    """设置学生为已报名状态"""
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': '无权限'}), 403
    
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        return jsonify({'success': False, 'message': '该用户不是学生'}), 400
    
    student.is_enrolled = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{student.nickname} 已报名上课'})


@auth_bp.route('/teacher/add-tokens/<int:student_id>', methods=['POST'])
@login_required
def add_student_tokens(student_id):
    """为学生添加图片生成令牌"""
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': '无权限'}), 403
    
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if amount <= 0 or amount > 1000:
        return jsonify({'success': False, 'message': '令牌数量必须在1-1000之间'}), 400
    
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        return jsonify({'success': False, 'message': '该用户不是学生'}), 400
    
    from auth.permissions import add_image_tokens
    add_image_tokens(
        student, 
        amount,
        operator=current_user,
        description=f'教师 {current_user.nickname} 手动增加 {amount} 松果币'
    )
    
    return jsonify({
        'success': True,
        'message': f'已为 {student.nickname} 添加 {amount} 个图片生成令牌',
        'new_balance': student.image_token_remaining
    })


@auth_bp.route('/teacher/confirm-lesson', methods=['POST'])
@login_required
def confirm_lesson():
    """确认学生完成课程"""
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': '无权限'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    lesson_number = data.get('lesson_number')
    notes = data.get('notes', '')
    
    if not student_id or not lesson_number:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    from auth.models import CourseProgress

    # 查找或创建课程进度记录
    progress = CourseProgress.query.filter_by(
        user_id=student_id,
        lesson_number=lesson_number
    ).first()
    
    if not progress:
        # 创建新的进度记录
        lesson_keys = {1: 'character', 2: 'action', 3: 'scene', 4: 'practice'}
        progress = CourseProgress(
            user_id=student_id,
            lesson_number=lesson_number,
            lesson_key=lesson_keys.get(lesson_number, f'lesson{lesson_number}')
        )
        db.session.add(progress)
    
    # 设置确认状态
    progress.is_completed = True
    progress.is_confirmed = True
    progress.confirmed_by = current_user.id
    progress.confirmed_at = datetime.utcnow()
    progress.completed_at = datetime.utcnow()
    progress.notes = notes
    
    db.session.commit()
    
    student = User.query.get(student_id)
    return jsonify({
        'success': True,
        'message': f'已确认 {student.nickname} 完成第 {lesson_number} 节课'
    })


@auth_bp.route('/teacher/unconfirm-lesson', methods=['POST'])
@login_required
def unconfirm_lesson():
    """取消确认学生课程（如果需要重新学习）"""
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': '无权限'}), 403
    
    data = request.get_json()
    student_id = data.get('student_id')
    lesson_number = data.get('lesson_number')
    
    if not student_id or not lesson_number:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    from auth.models import CourseProgress
    
    progress = CourseProgress.query.filter_by(
        user_id=student_id,
        lesson_number=lesson_number
    ).first()
    
    if not progress:
        return jsonify({'success': False, 'message': '未找到课程进度记录'}), 404
    
    # 取消确认
    progress.is_confirmed = False
    progress.confirmed_by = None
    progress.confirmed_at = None
    progress.notes = None
    
    db.session.commit()
    
    student = User.query.get(student_id)
    return jsonify({
        'success': True,
        'message': f'已取消确认 {student.nickname} 的第 {lesson_number} 节课'
    })