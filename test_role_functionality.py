#!/usr/bin/env python3
"""
测试角色功能的完整性
验证注册、编辑资料、年龄验证等功能
"""

from app import app
from models import db, User
from forms import KidRegistrationForm, ProfileUpdateForm
import unittest

def test_role_functionality():
    """测试角色功能"""
    print("🧪 开始测试角色功能...")
    
    with app.app_context():
        # 测试1: 验证现有用户的角色字段
        print("\n1️⃣ 测试现有用户角色...")
        user = User.query.filter_by(username='why').first()
        if user:
            print(f"   用户 {user.username} 的角色: {getattr(user, 'role', 'None')}")
            if not hasattr(user, 'role') or not user.role:
                user.role = 'student'
                db.session.commit()
                print("   ✅ 已设置默认角色为 student")
            else:
                print("   ✅ 角色字段正常")
        
        # 测试2: 验证表单的角色选择和年龄验证
        print("\n2️⃣ 测试表单验证...")
        
        # 测试学生角色的年龄范围
        with app.test_request_context('/auth/register', method='POST'):
            form_data = {
                'username': 'test_student',
                'nickname': '测试学生',
                'role': 'student',
                'age': 15,  # 学生有效年龄
                'parent_email': 'parent@test.com',
                'password': 'test123',
                'password_confirm': 'test123',
                'color_preference': 'vibrant',
                'csrf_token': 'test'
            }
            
            form = KidRegistrationForm(data=form_data, csrf_enabled=False)
            if form.validate():
                print("   ✅ 学生角色年龄验证通过")
            else:
                print(f"   ❌ 学生角色验证失败: {form.errors}")
        
        # 测试老师角色的年龄范围
        with app.test_request_context('/auth/register', method='POST'):
            form_data = {
                'username': 'test_teacher',
                'nickname': '测试老师',
                'role': 'teacher',
                'age': 30,  # 老师有效年龄
                'parent_email': 'teacher@test.com',
                'password': 'test123',
                'password_confirm': 'test123',
                'color_preference': 'vibrant',
                'csrf_token': 'test'
            }
            
            form = KidRegistrationForm(data=form_data, csrf_enabled=False)
            if form.validate():
                print("   ✅ 老师角色年龄验证通过")
            else:
                print(f"   ❌ 老师角色验证失败: {form.errors}")
        
        # 测试年龄超出范围的情况
        with app.test_request_context('/auth/register', method='POST'):
            form_data = {
                'username': 'test_invalid',
                'nickname': '测试无效',
                'role': 'student',
                'age': 30,  # 学生无效年龄
                'parent_email': 'invalid@test.com',
                'password': 'test123',
                'password_confirm': 'test123',
                'color_preference': 'vibrant',
                'csrf_token': 'test'
            }
            
            form = KidRegistrationForm(data=form_data, csrf_enabled=False)
            if not form.validate() and 'age' in form.errors:
                print("   ✅ 年龄超出范围验证正常")
            else:
                print("   ❌ 年龄验证有问题")
        
        # 测试3: 验证ProfileUpdateForm
        print("\n3️⃣ 测试资料更新表单...")
        with app.test_request_context('/auth/profile', method='POST'):
            form_data = {
                'nickname': '更新昵称',
                'role': 'teacher',
                'age': 25,
                'color_preference': 'warm',
                'bio': '测试简介',
                'csrf_token': 'test'
            }
            
            form = ProfileUpdateForm(data=form_data, csrf_enabled=False)
            if form.validate():
                print("   ✅ 资料更新表单验证通过")
            else:
                print(f"   ❌ 资料更新表单验证失败: {form.errors}")
        
        print("\n🎉 角色功能测试完成!")

if __name__ == '__main__':
    test_role_functionality()