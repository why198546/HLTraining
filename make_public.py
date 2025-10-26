#!/usr/bin/env python3
"""
将现有作品设为公开状态
"""

import sys
import os
sys.path.append('.')

from app import app
from models import db, Artwork, User

def make_artworks_public():
    """将所有作品设为公开"""
    with app.app_context():
        print("🔧 将现有作品设为公开状态...")
        
        # 获取所有非公开作品
        private_artworks = Artwork.query.filter_by(is_public=False).all()
        print(f"📊 找到 {len(private_artworks)} 个非公开作品")
        
        # 设为公开
        for artwork in private_artworks:
            artwork.is_public = True
            print(f"✅ 设为公开: {artwork.title} (ID: {artwork.id})")
        
        # 提交更改
        db.session.commit()
        print("💾 更改已保存到数据库")
        
        # 验证结果
        public_count = Artwork.query.filter_by(is_public=True).count()
        print(f"🌐 现在有 {public_count} 个公开作品")

if __name__ == '__main__':
    make_artworks_public()