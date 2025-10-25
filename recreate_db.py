#!/usr/bin/env python3
"""
重建数据库并创建测试数据
"""

from app import app
from models import db, User, Artwork
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def recreate_database():
    """重新创建数据库和测试数据"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")
        
        # 创建测试用户
        test_user = User.query.filter_by(username='why').first()
        if not test_user:
            test_user = User(
                username='why',
                nickname='小画家',
                age=12,
                parent_email='parent@example.com',
                password='123456'
            )
            test_user.is_verified = True
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ 创建测试用户: {test_user.username}")
        else:
            print(f"✅ 用户已存在: {test_user.username}")
        
        # 创建一些测试作品
        import os
        
        # 检查是否有已存在的作品文件
        upload_dir = 'uploads'
        for i in range(3):
            artwork = Artwork(
                session_id=str(uuid.uuid4()),
                title=f'测试作品 {i+1}',
                user_id=test_user.id
            )
            artwork.description = f'这是第 {i+1} 个测试作品'
            artwork.status = 'completed'
            artwork.created_at = datetime.utcnow()
            artwork.is_featured = (i == 0)  # 第一个作品设为推荐
            artwork.is_public = (i == 0)
            artwork.vote_count = i * 5
            db.session.add(artwork)
            
            db.session.commit()
            print("✅ 创建测试作品数据")
        
        print("🎉 数据库重建完成！")
        print(f"🔗 登录信息：用户名=why, 密码=123456")

if __name__ == '__main__':
    recreate_database()