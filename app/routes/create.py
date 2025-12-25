"""创作相关路由 - 重构为三个独立页面"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

create_bp = Blueprint('create', __name__)

@create_bp.route('/')
@login_required
def create():
    """创作主入口 - 重定向到图片创作"""
    return redirect(url_for('create.create_image'))

@create_bp.route('/image')
@login_required
def create_image():
    """第1步：2D图片创作（上传线稿、AI上色、快速调整）"""
    session_id = request.args.get('session_id')
    return render_template('create_image.html', session_id=session_id)

@create_bp.route('/3d')
@login_required
def create_3d():
    """第2步：3D模型生成（可独立使用或基于2D图片）"""
    session_id = request.args.get('session_id')
    
    # 如果有session_id，验证所有权
    if session_id:
        from auth.models import Artwork
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            flash('未找到对应的作品', 'error')
            return redirect(url_for('create.create_image'))
        return render_template('create_3d.html', session_id=session_id, artwork=artwork)
    
    # 没有session_id时，教师和管理员可以直接访问
    if current_user.role in ['teacher', 'admin']:
        return render_template('create_3d.html', session_id=None, artwork=None)
    
    # 普通学生必须先生成图片
    flash('请先创作2D图片，再生成3D模型', 'info')
    return redirect(url_for('create.create_image'))

@create_bp.route('/video')
@login_required
def create_video():
    """第3步：视频生成（可独立使用或基于2D图片）"""
    session_id = request.args.get('session_id')
    
    # 如果有session_id，验证所有权
    if session_id:
        from auth.models import Artwork
        artwork = Artwork.query.filter_by(session_id=session_id).first()
        if not artwork or artwork.user_id != current_user.id:
            flash('未找到对应的作品', 'error')
            return redirect(url_for('create.create_image'))
        return render_template('create_video.html', session_id=session_id, artwork=artwork)
    
    # 没有session_id时，教师和管理员可以直接访问
    if current_user.role in ['teacher', 'admin']:
        return render_template('create_video.html', session_id=None, artwork=None)
    
    # 普通学生必须先生成图片
    flash('请先创作2D图片，再生成视频', 'info')
    return redirect(url_for('create.create_image'))

@create_bp.route('/edit/<int:artwork_id>')
@login_required
def edit_artwork(artwork_id):
    """编辑作品页面"""
    from auth.models import Artwork

    # 获取作品并检查权限
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 确保只有作品所有者可以编辑
    if artwork.user_id != current_user.id:
        flash('您没有权限编辑这个作品', 'error')
        return redirect(url_for('auth.my_artworks'))
    
    # 获取文件URLs
    file_urls = artwork.get_file_urls()
    
    # 渲染编辑页面，传递作品数据和文件URLs
    return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)

@create_bp.route('/edit/<int:artwork_id>', methods=['POST'])
@login_required
def update_artwork(artwork_id):
    """更新作品信息"""
    from auth.models import Artwork, db

    # 获取作品并检查权限
    artwork = Artwork.query.get_or_404(artwork_id)
    
    if artwork.user_id != current_user.id:
        flash('您没有权限编辑这个作品', 'error')
        return redirect(url_for('auth.my_artworks'))
    
    # 获取表单数据
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    is_public = request.form.get('is_public') == 'on'
    
    # 验证数据
    if not title:
        flash('作品标题不能为空', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    if len(title) > 100:
        flash('作品标题最多100个字符', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    if len(description) > 500:
        flash('作品描述最多500个字符', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    # 更新作品信息
    artwork.title = title
    artwork.description = description if description else None
    artwork.is_public = is_public
    
    try:
        db.session.commit()
        flash('作品信息已更新！', 'success')
        return redirect(url_for('auth.my_artworks'))
    except Exception as e:
        db.session.rollback()
        print(f"Update artwork error: {e}")
        flash('更新失败，请重试', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
