#!/usr/bin/env python3
"""创建测试用户脚本"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_test_user():
    with app.app_context():
        # 检查是否已经有test用户
        existing_user = User.query.filter_by(username='test').first()
        if existing_user:
            print("✅ 测试用户已存在")
            print(f"用户名: {existing_user.username}")
            print(f"用户ID: {existing_user.id}")
            return existing_user
        
        # 创建新的测试用户
        test_user = User(
            username='test',
            nickname='测试用户',
            age=12,
            parent_email='parent@example.com',
            password='test123'
        )
        test_user.is_verified = True  # 直接设置为已验证
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ 创建测试用户成功!")
        print(f"用户名: test")
        print(f"密码: test123")
        print(f"用户ID: {test_user.id}")
        return test_user

if __name__ == "__main__":
    create_test_user()