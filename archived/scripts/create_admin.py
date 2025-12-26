"""
创建管理员账户
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_legacy import app
from auth.models import User, db


def create_admin():
    """创建管理员账户"""
    with app.app_context():
        # 检查是否已存在管理员
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("管理员账户已存在！")
            print(f"用户名: {admin.username}")
            print(f"昵称: {admin.nickname}")
            return
        
        # 创建新管理员
        admin = User(
            username='admin',
            nickname='系统管理员',
            parent_email='admin@hltraining.com',
            password='admin123',  # 请修改为更安全的密码
            role='admin'
        )
        admin.is_verified = True
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ 管理员账户创建成功！")
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"昵称: {admin.nickname}")
        print(f"邮箱: {admin.parent_email}")
        print("\n⚠️ 请立即登录并修改密码！")

if __name__ == '__main__':
    create_admin()
