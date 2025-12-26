#!/usr/bin/env python
"""快速添加用户脚本"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from auth.models import User

def add_user(username, password, nickname=None, parent_email=None):
    """添加用户到数据库"""
    with app.app_context():
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            print(f"❌ 用户 {username} 已存在")
            return False
        
        # 创建新用户
        user = User(
            username=username,
            nickname=nickname or username,
            parent_email=parent_email or f"{username}@example.com",
            password=password
        )
        
        # 默认验证（开发环境）
        user.is_verified = True
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ 用户 {username} 添加成功！")
            print(f"   用户名: {username}")
            print(f"   昵称: {user.nickname}")
            print(f"   邮箱: {user.parent_email}")
            print(f"   验证状态: {'已验证' if user.is_verified else '未验证'}")
            print(f"   创建时间: {user.created_at}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ 添加用户失败: {str(e)}")
            return False

if __name__ == '__main__':
    # 添加用户 why / 162582
    add_user(
        username='why',
        password='162582',
        nickname='Why小朋友',
        parent_email='why@example.com'
    )
