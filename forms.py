"""
用户管理系统的表单定义
儿童友好的注册和登录表单
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, BooleanField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError, Optional
from models import User
from datetime import date


class BirthDateValidator:
    """根据角色动态验证出生日期的验证器"""
    def __init__(self, message=None):
        if not message:
            message = '出生日期超出该角色的有效范围'
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            raise ValidationError('请输入出生日期')
            
        role = form.role.data if hasattr(form, 'role') and form.role.data else 'student'
        birth_date = field.data
        today = date.today()
        
        # 计算年龄
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        # 验证出生日期不能是未来
        if birth_date > today:
            raise ValidationError('出生日期不能是未来')
        
        # 根据角色验证年龄范围
        if role == 'student':
            if age < 5 or age > 24:
                raise ValidationError('学生年龄必须在5-24岁之间')
        elif role in ['teacher', 'parent']:
            if age < 20 or age > 80:
                raise ValidationError('老师和家长年龄必须在20-80岁之间')

class KidRegistrationForm(FlaskForm):
    """儿童用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度应在3-20个字符之间')
    ])
    
    nickname = StringField('昵称', validators=[
        DataRequired(message='请输入昵称'),
        Length(min=1, max=50, message='昵称长度应在1-50个字符之间')
    ])
    
    role = SelectField('角色', choices=[
        ('student', '学生'),
        ('teacher', '老师'),
        ('parent', '家长')
    ], default='student')
    
    birth_date = DateField('出生日期', validators=[
        DataRequired(message='请输入出生日期'),
        BirthDateValidator()
    ])
    
    gender = SelectField('性别', choices=[
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    ], validators=[DataRequired(message='请选择性别')])
    
    contact_phone = StringField('联系电话', validators=[
        Optional(),
        Length(max=20, message='电话号码不能超过20个字符')
    ])
    
    mailing_address = TextAreaField('邮寄地址', validators=[
        Optional(),
        Length(max=500, message='地址不能超过500个字符')
    ])
    
    parent_email = StringField('家长邮箱', validators=[
        DataRequired(message='请输入家长邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, max=20, message='密码长度应在6-20个字符之间')
    ])
    
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    
    color_preference = SelectField('喜欢的色彩风格', choices=[
        ('vibrant', '鲜艳色彩'),
        ('pastel', '柔和色彩'),
        ('warm', '温暖色调'),
        ('cool', '冷色调')
    ], default='vibrant')
    
    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('这个用户名已经被使用了，请选择其他用户名')
    
    def validate_parent_email(self, field):
        """验证家长邮箱是否已被其他账户使用"""
        existing_user = User.query.filter_by(parent_email=field.data).first()
        if existing_user:
            raise ValidationError('这个邮箱已经关联了其他账户')


class KidLoginForm(FlaskForm):
    """儿童用户登录表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名')
    ])
    
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    
    remember_me = BooleanField('记住我')


class ParentVerificationForm(FlaskForm):
    """家长验证表单"""
    verification_code = StringField('验证码', validators=[
        DataRequired(message='请输入6位验证码'),
        Length(min=6, max=6, message='验证码为6位数字')
    ])


class ProfileUpdateForm(FlaskForm):
    """个人资料更新表单"""
    nickname = StringField('昵称', validators=[
        DataRequired(message='请输入昵称'),
        Length(min=1, max=50, message='昵称长度应在1-50个字符之间')
    ])
    
    role = SelectField('角色', choices=[
        ('student', '学生'),
        ('teacher', '老师'),
        ('parent', '家长')
    ])
    
    birth_date = DateField('出生日期', validators=[
        DataRequired(message='请输入出生日期'),
        BirthDateValidator()
    ])
    
    gender = SelectField('性别', choices=[
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    ], validators=[DataRequired(message='请选择性别')])
    
    contact_phone = StringField('联系电话', validators=[
        Optional(),
        Length(max=20, message='电话号码不能超过20个字符')
    ])
    
    mailing_address = TextAreaField('邮寄地址', validators=[
        Optional(),
        Length(max=500, message='地址不能超过500个字符')
    ])
    
    color_preference = SelectField('喜欢的色彩风格', choices=[
        ('vibrant', '鲜艳色彩'),
        ('pastel', '柔和色彩'),
        ('warm', '温暖色调'),
        ('cool', '冷色调')
    ])
    
    bio = TextAreaField('自我介绍', validators=[
        Length(max=200, message='自我介绍不能超过200个字符')
    ])


class PasswordChangeForm(FlaskForm):
    """密码修改表单"""
    old_password = PasswordField('当前密码', validators=[
        DataRequired(message='请输入当前密码')
    ])
    
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='请输入新密码'),
        Length(min=6, max=20, message='密码长度应在6-20个字符之间')
    ])
    
    new_password_confirm = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认新密码'),
        EqualTo('new_password', message='两次输入的新密码不一致')
    ])


class ArtworkForm(FlaskForm):
    """作品信息表单"""
    title = StringField('作品标题', validators=[
        DataRequired(message='请输入作品标题'),
        Length(min=1, max=100, message='标题长度应在1-100个字符之间')
    ])
    
    description = TextAreaField('作品描述', validators=[
        Length(max=500, message='描述不能超过500个字符')
    ])
    
    show_in_gallery = BooleanField('在作品展示中公开', default=True)


class PrivacySettingsForm(FlaskForm):
    """隐私设置表单"""
    show_in_gallery = BooleanField('允许在作品展示中显示我的作品', default=True)
    show_age = BooleanField('在作品上显示我的年龄', default=False)
    allow_parent_reports = BooleanField('向家长发送使用报告', default=True)


class ParentVerificationForm(FlaskForm):
    """家长验证表单"""
    verification_code = StringField('验证码', validators=[
        DataRequired(message='请输入验证码'),
        Length(min=6, max=6, message='验证码为6位')
    ])
    
    consent_terms = BooleanField('我已阅读并同意《用户协议》和《隐私政策》', validators=[
        DataRequired(message='请确认您已阅读并同意相关条款')
    ])
    
    consent_age = BooleanField('我确认我的孩子年龄在10-14岁之间', validators=[
        DataRequired(message='请确认孩子年龄符合要求')
    ])
    
    consent_supervision = BooleanField('我同意孩子在我的监督下使用本平台', validators=[
        DataRequired(message='请确认您同意监督孩子使用')
    ])