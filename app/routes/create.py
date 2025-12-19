"""创作相关路由"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

create_bp = Blueprint('create', __name__)

@create_bp.route('/')
@login_required
def create():
    """创作页面"""
    return render_template('create.html')

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
