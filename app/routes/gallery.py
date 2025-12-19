"""作品集相关路由"""
from flask import Blueprint, render_template
from sqlalchemy import desc

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/')
def gallery():
    """公共作品展示页面"""
    try:
        from auth.models import Artwork, User
        
        # 获取所有公开的推荐作品
        featured_artworks = Artwork.query.filter_by(
            is_public=True, 
            is_featured=True
        ).join(User).order_by(desc(Artwork.featured_at)).all()
        
        return render_template('gallery.html', artworks=featured_artworks)
        
    except Exception as e:
        print(f"❌ 加载作品展示失败: {str(e)}")
        return render_template('gallery.html', artworks=[])
