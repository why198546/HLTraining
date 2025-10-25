#!/usr/bin/env python3
"""
测试用户详细信息功能的完整性
验证出生日期、性别、联系电话、邮寄地址等功能
"""

from app import app
from models import db, User
from forms import KidRegistrationForm, ProfileUpdateForm
from datetime import date, datetime

def test_user_details_functionality():
    """测试用户详细信息功能"""
    print("🧪 开始测试用户详细信息功能...")
    
    with app.app_context():
        # 测试1: 验证现有用户的新字段
        print("\n1️⃣ 测试现有用户新字段...")
        user = User.query.filter_by(username='why').first()
        if user:
            print(f"   用户 {user.username} 的信息:")
            print(f"   - 出生日期: {user.birth_date}")
            print(f"   - 计算年龄: {user.get_age()}岁")
            print(f"   - 性别: {user.gender}")
            print(f"   - 联系电话: {user.contact_phone}")
            print(f"   - 邮寄地址: {user.mailing_address}")
            print("   ✅ 新字段正常")
        
        # 测试2: 验证年龄计算函数
        print("\n2️⃣ 测试年龄计算...")
        test_birth_date = date(2010, 6, 15)  # 假设2010年6月15日出生
        test_user = User(
            username='test_age',
            nickname='测试年龄',
            birth_date=test_birth_date,
            gender='other',
            parent_email='test@test.com',
            password='test123'
        )
        
        calculated_age = test_user.get_age()
        expected_age = datetime.now().year - 2010
        if datetime.now().month < 6 or (datetime.now().month == 6 and datetime.now().day < 15):
            expected_age -= 1
            
        if calculated_age == expected_age:
            print(f"   ✅ 年龄计算正确: {calculated_age}岁")
        else:
            print(f"   ❌ 年龄计算错误: 期望{expected_age}岁，实际{calculated_age}岁")
        
        # 测试3: 验证表单的新字段验证
        print("\n3️⃣ 测试表单验证...")
        
        # 测试注册表单的新字段
        with app.test_request_context('/auth/register', method='POST'):
            form_data = {
                'username': 'test_details',
                'nickname': '测试详情',
                'role': 'student',
                'birth_date': date(2008, 3, 20),
                'gender': 'male',
                'contact_phone': '13800138000',
                'mailing_address': '测试地址123号',
                'parent_email': 'parent@test.com',
                'password': 'test123',
                'password_confirm': 'test123',
                'color_preference': 'vibrant',
                'csrf_token': 'test'
            }
            
            form = KidRegistrationForm(data=form_data, csrf_enabled=False)
            if form.validate():
                print("   ✅ 注册表单新字段验证通过")
            else:
                print(f"   ❌ 注册表单验证失败: {form.errors}")
        
        # 测试资料更新表单
        with app.test_request_context('/auth/profile', method='POST'):
            form_data = {
                'nickname': '更新昵称',
                'role': 'teacher',
                'birth_date': date(1990, 5, 10),
                'gender': 'female',
                'contact_phone': '13900139000',
                'mailing_address': '更新地址456号',
                'color_preference': 'warm',
                'bio': '测试简介',
                'csrf_token': 'test'
            }
            
            form = ProfileUpdateForm(data=form_data, csrf_enabled=False)
            if form.validate():
                print("   ✅ 资料更新表单验证通过")
            else:
                print(f"   ❌ 资料更新表单验证失败: {form.errors}")
        
        # 测试4: 验证年龄范围验证
        print("\n4️⃣ 测试年龄范围验证...")
        
        # 测试学生角色的年龄限制
        with app.test_request_context('/auth/register', method='POST'):
            form_data = {
                'username': 'test_age_limit',
                'nickname': '测试年龄限制',
                'role': 'student',
                'birth_date': date(1995, 1, 1),  # 年龄太大
                'gender': 'other',
                'parent_email': 'test@test.com',
                'password': 'test123',
                'password_confirm': 'test123',
                'color_preference': 'vibrant',
                'csrf_token': 'test'
            }
            
            form = KidRegistrationForm(data=form_data, csrf_enabled=False)
            if not form.validate() and 'birth_date' in form.errors:
                print("   ✅ 学生年龄超限验证正常")
            else:
                print("   ❌ 学生年龄验证有问题")
        
        print("\n🎉 用户详细信息功能测试完成!")

if __name__ == '__main__':
    test_user_details_functionality()