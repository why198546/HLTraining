#!/usr/bin/env python3
"""
用户管理系统测试脚本
测试注册、登录、数据库操作等功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Artwork, CreationSession, ParentVerification
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def test_database_creation():
    """测试数据库创建"""
    print("🔍 测试数据库创建...")
    with app.app_context():
        try:
            # 删除所有表并重新创建
            db.drop_all()
            db.create_all()
            print("✅ 数据库表创建成功")
            return True
        except Exception as e:
            print(f"❌ 数据库创建失败: {e}")
            return False

def test_user_creation():
    """测试用户创建"""
    print("\n🔍 测试用户创建...")
    with app.app_context():
        try:
            # 创建测试用户
            test_user = User(
                username='test_kid',
                nickname='小测试',
                age=12,
                parent_email='parent@example.com',
                password='password123'
            )
            test_user.is_verified = True  # 设置为已验证状态
            
            db.session.add(test_user)
            db.session.commit()
            
            # 验证用户是否创建成功
            user = User.query.filter_by(username='test_kid').first()
            if user:
                print(f"✅ 用户创建成功: {user.nickname} (ID: {user.id})")
                return user
            else:
                print("❌ 用户创建失败")
                return None
        except Exception as e:
            print(f"❌ 用户创建错误: {e}")
            return None

def test_artwork_creation(user):
    """测试作品创建"""
    print("\n🔍 测试作品创建...")
    with app.app_context():
        try:
            # 创建创作会话
            session = CreationSession(
                session_id=str(uuid.uuid4()),
                user_id=user.id
            )
            db.session.add(session)
            db.session.flush()  # 获取session的ID
            
            # 创建测试作品
            artwork = Artwork(
                session_id=session.session_id,
                title='测试作品',
                user_id=user.id
            )
            # 设置其他属性
            artwork.description = '这是一个测试作品'
            artwork.original_sketch = 'test_sketch.jpg'
            artwork.colored_image = 'test_colored.jpg'
            artwork.style_type = 'cartoon'
            artwork.color_preference = 'vibrant'
            artwork.status = 'completed'
            
            db.session.add(artwork)
            db.session.commit()
            
            print(f"✅ 作品创建成功: {artwork.title} (ID: {artwork.id})")
            return artwork
        except Exception as e:
            print(f"❌ 作品创建错误: {e}")
            return None

def test_parent_verification(user):
    """测试家长验证"""
    print("\n🔍 测试家长验证...")
    with app.app_context():
        try:
            from datetime import timedelta
            # 创建验证记录
            expires_at = datetime.now() + timedelta(hours=24)
            verification = ParentVerification(
                user_id=user.id,
                parent_email=user.parent_email,
                verification_code='123456',
                expires_at=expires_at
            )
            
            db.session.add(verification)
            db.session.commit()
            
            print(f"✅ 家长验证记录创建成功: {verification.verification_code}")
            return verification
        except Exception as e:
            print(f"❌ 家长验证创建错误: {e}")
            return None

def test_user_authentication():
    """测试用户认证"""
    print("\n🔍 测试用户认证...")
    with app.app_context():
        try:
            user = User.query.filter_by(username='test_kid').first()
            if user and user.check_password('password123'):
                print("✅ 用户密码验证成功")
                return True
            else:
                print("❌ 用户密码验证失败")
                return False
        except Exception as e:
            print(f"❌ 用户认证错误: {e}")
            return False

def test_database_relationships():
    """测试数据库关系"""
    print("\n🔍 测试数据库关系...")
    with app.app_context():
        try:
            user = User.query.filter_by(username='test_kid').first()
            if user:
                # 测试用户-作品关系
                artworks = user.artworks
                sessions = user.sessions
                verifications = user.parent_verifications
                
                print(f"✅ 用户关系测试成功:")
                print(f"   - 作品数量: {len(artworks)}")
                print(f"   - 会话数量: {len(sessions)}")
                print(f"   - 验证记录: {len(verifications)}")
                return True
            else:
                print("❌ 找不到测试用户")
                return False
        except Exception as e:
            print(f"❌ 数据库关系测试错误: {e}")
            return False

def cleanup_test_data():
    """清理测试数据"""
    print("\n🧹 清理测试数据...")
    with app.app_context():
        try:
            # 删除测试用户及相关数据
            user = User.query.filter_by(username='test_kid').first()
            if user:
                # 删除相关的作品、会话、验证记录
                Artwork.query.filter_by(user_id=user.id).delete()
                CreationSession.query.filter_by(user_id=user.id).delete()
                ParentVerification.query.filter_by(user_id=user.id).delete()
                
                # 删除用户
                db.session.delete(user)
                db.session.commit()
                
                print("✅ 测试数据清理完成")
            else:
                print("ℹ️ 没有找到需要清理的测试数据")
        except Exception as e:
            print(f"❌ 清理测试数据错误: {e}")

def main():
    """主测试函数"""
    print("🚀 开始用户管理系统测试")
    print("=" * 50)
    
    # 执行测试
    tests_passed = 0
    total_tests = 6
    
    # 1. 测试数据库创建
    if test_database_creation():
        tests_passed += 1
    
    # 2. 测试用户创建
    user = test_user_creation()
    if user:
        tests_passed += 1
        
        # 3. 测试作品创建
        artwork = test_artwork_creation(user)
        if artwork:
            tests_passed += 1
        
        # 4. 测试家长验证
        verification = test_parent_verification(user)
        if verification:
            tests_passed += 1
        
        # 5. 测试用户认证
        if test_user_authentication():
            tests_passed += 1
        
        # 6. 测试数据库关系
        if test_database_relationships():
            tests_passed += 1
    
    # 清理测试数据
    cleanup_test_data()
    
    # 测试结果
    print("\n" + "=" * 50)
    print(f"🏁 测试完成!")
    print(f"✅ 通过测试: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！用户管理系统工作正常。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查系统配置。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)