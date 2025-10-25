#!/usr/bin/env python3
"""
简单测试角色功能核心逻辑
"""

from app import app
from models import db, User
from forms import AgeValidator
from wtforms import Form, IntegerField, SelectField
from wtforms.validators import DataRequired

class SimpleTestForm(Form):
    """简单测试表单，不涉及CSRF"""
    role = SelectField('角色', choices=[
        ('student', '学生'),
        ('teacher', '老师'),
        ('parent', '家长')
    ])
    age = IntegerField('年龄', validators=[DataRequired(), AgeValidator()])

def test_age_validator():
    """测试年龄验证器"""
    print("🧪 测试年龄验证器...")
    
    # 测试学生年龄
    form_data = {'role': 'student', 'age': 15}
    form = SimpleTestForm(data=form_data)
    if form.validate():
        print("   ✅ 学生年龄15岁验证通过")
    else:
        print(f"   ❌ 学生年龄验证失败: {form.errors}")
    
    # 测试学生超龄
    form_data = {'role': 'student', 'age': 30}
    form = SimpleTestForm(data=form_data)
    if not form.validate() and 'age' in form.errors:
        print("   ✅ 学生超龄验证正确阻止")
    else:
        print(f"   ❌ 学生超龄验证有问题")
    
    # 测试老师年龄
    form_data = {'role': 'teacher', 'age': 35}
    form = SimpleTestForm(data=form_data)
    if form.validate():
        print("   ✅ 老师年龄35岁验证通过")
    else:
        print(f"   ❌ 老师年龄验证失败: {form.errors}")
    
    # 测试老师低龄
    form_data = {'role': 'teacher', 'age': 15}
    form = SimpleTestForm(data=form_data)
    if not form.validate() and 'age' in form.errors:
        print("   ✅ 老师低龄验证正确阻止")
    else:
        print(f"   ❌ 老师低龄验证有问题")

def test_user_role():
    """测试用户角色字段"""
    print("\n🧪 测试用户角色字段...")
    
    with app.app_context():
        user = User.query.filter_by(username='why').first()
        if user:
            print(f"   用户 {user.username} 的当前角色: {user.role}")
            
            # 测试角色更新
            old_role = user.role
            user.role = 'teacher'
            db.session.commit()
            print(f"   角色从 {old_role} 更新为 {user.role}")
            
            # 恢复原角色
            user.role = old_role
            db.session.commit()
            print(f"   角色恢复为 {user.role}")
            print("   ✅ 角色字段操作正常")
        else:
            print("   ❌ 找不到测试用户")

if __name__ == '__main__':
    test_age_validator()
    test_user_role()
    print("\n🎉 核心功能测试完成!")