#!/usr/bin/env python3
"""
验证数据库中的作品数据
"""

import sys
sys.path.append('.')

from app import app
from models import db, Artwork, User

def verify_artworks():
    """验证数据库中的作品数据"""
    with app.app_context():
        print("🔍 验证数据库中的作品...")
        
        # 查询所有作品
        artworks = Artwork.query.order_by(Artwork.created_at.desc()).all()
        
        print(f"📊 总作品数: {len(artworks)}")
        print()
        
        for i, artwork in enumerate(artworks, 1):
            user = User.query.get(artwork.user_id)
            print(f"{i}. 【{artwork.title}】")
            print(f"   ID: {artwork.id}")
            print(f"   会话ID: {artwork.session_id}")
            print(f"   创作者: {user.nickname if user else '未知'}")
            print(f"   类型: {artwork.style_type}")
            print(f"   状态: {artwork.status}")
            print(f"   公开: {'是' if artwork.is_public else '否'}")
            print(f"   创建时间: {artwork.created_at}")
            print(f"   彩色图片: {artwork.colored_image}")
            print(f"   3D模型: {artwork.model_3d}")
            print(f"   观看数: {artwork.view_count}")
            print(f"   点赞数: {artwork.vote_count}")
            
            # 获取文件URLs
            file_urls = artwork.get_file_urls()
            print(f"   彩色图片URL: {file_urls.get('colored_image', '无')}")
            print(f"   3D模型URL: {file_urls.get('model_3d', '无')}")
            print()

if __name__ == '__main__':
    verify_artworks()