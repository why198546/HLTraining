#!/usr/bin/env python3
"""
测试数据库中的作品数据
"""

import sys
import os
sys.path.append('.')

from app import app
from models import db, Artwork, User

def test_artworks():
    """测试作品数据"""
    with app.app_context():
        print("🔍 检查数据库中的作品...")
        
        # 获取所有作品
        all_artworks = Artwork.query.all()
        print(f"📊 总共有 {len(all_artworks)} 个作品")
        
        # 获取公开作品
        public_artworks = Artwork.query.filter_by(is_public=True).all()
        print(f"🌐 公开作品: {len(public_artworks)} 个")
        
        # 显示每个作品的详细信息
        for artwork in all_artworks:
            print(f"\n📝 作品ID: {artwork.id}")
            print(f"   标题: {artwork.title}")
            print(f"   会话ID: {artwork.session_id}")
            print(f"   作者: {artwork.author.nickname if artwork.author else '未知'}")
            print(f"   创建时间: {artwork.created_at}")
            print(f"   是否公开: {artwork.is_public}")
            print(f"   状态: {artwork.status}")
            
            # 文件信息
            file_urls = artwork.get_file_urls()
            print(f"   图片文件: {file_urls.get('colored_image', '无')}")
            print(f"   3D模型: {file_urls.get('model_3d', '无')}")

if __name__ == '__main__':
    test_artworks()