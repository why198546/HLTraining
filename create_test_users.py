"""
创建测试用户脚本
快速创建10个测试账户用于功能测试
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from auth.models import User, db


def create_test_users():
    """创建10个测试用户"""
    app = create_app()
    
    with app.app_context():
        try:
            # 定义测试用户数据
            test_users = [
                {
                    'username': 'student1',
                    'nickname': '小明',
                    'password': '123456',
                    'parent_email': 'parent1@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': True
                },
                {
                    'username': 'student2',
                    'nickname': '小红',
                    'password': '123456',
                    'parent_email': 'parent2@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': True
                },
                {
                    'username': 'student3',
                    'nickname': '小刚',
                    'password': '123456',
                    'parent_email': 'parent3@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': False
                },
                {
                    'username': 'student4',
                    'nickname': '小美',
                    'password': '123456',
                    'parent_email': 'parent4@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': True
                },
                {
                    'username': 'student5',
                    'nickname': '小华',
                    'password': '123456',
                    'parent_email': 'parent5@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': False
                },
                {
                    'username': 'student6',
                    'nickname': '小芳',
                    'password': '123456',
                    'parent_email': 'parent6@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': True
                },
                {
                    'username': 'student7',
                    'nickname': '小强',
                    'password': '123456',
                    'parent_email': 'parent7@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': True
                },
                {
                    'username': 'student8',
                    'nickname': '小丽',
                    'password': '123456',
                    'parent_email': 'parent8@test.com',
                    'role': 'student',
                    'is_verified': True,
                    'is_enrolled': False
                },
                {
                    'username': 'teacher1',
                    'nickname': '王老师',
                    'password': '123456',
                    'parent_email': 'teacher1@test.com',
                    'role': 'teacher',
                    'is_verified': True,
                    'is_enrolled': False
                },
                {
                    'username': 'teacher2',
                    'nickname': '李老师',
                    'password': '123456',
                    'parent_email': 'teacher2@test.com',
                    'role': 'teacher',
                    'is_verified': True,
                    'is_enrolled': False
                }
            ]
            
            created_count = 0
            skipped_count = 0
            
            for user_data in test_users:
                # 检查用户是否已存在
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user:
                    print(f"⚠️  用户 {user_data['username']} 已存在，跳过")
                    skipped_count += 1
                    continue
                
                # 创建新用户
                user = User(
                    username=user_data['username'],
                    nickname=user_data['nickname'],
                    parent_email=user_data['parent_email'],
                    password=user_data['password']
                )
                user.role = user_data['role']
                user.is_verified = user_data['is_verified']
                user.is_enrolled = user_data['is_enrolled']
                user.image_token_remaining = 50  # 默认50个令牌
                
                db.session.add(user)
                created_count += 1
                print(f"✓ 创建用户: {user_data['username']} ({user_data['nickname']}) - {user_data['role']}")
            
            db.session.commit()
            
            print(f"\n{'='*50}")
            print(f"✅ 测试用户创建完成！")
            print(f"   新创建: {created_count} 个用户")
            print(f"   已存在: {skipped_count} 个用户")
            print(f"{'='*50}")
            print("\n📋 测试账户列表：")
            print(f"{'用户名':<12} {'密码':<10} {'角色':<10} {'昵称':<10} {'报名状态'}")
            print("-" * 60)
            for user_data in test_users:
                enrolled = '已报名' if user_data['is_enrolled'] else '未报名'
                print(f"{user_data['username']:<12} 123456     {user_data['role']:<10} {user_data['nickname']:<10} {enrolled}")
            print("\n提示：所有用户密码都是 123456")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = create_test_users()
    sys.exit(0 if success else 1)
