"""
用户管理系统的数据库模型
支持儿童用户注册、作品管理和家长监护功能
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型 - 专为10-14岁儿童设计"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(50), nullable=False)  # 儿童友好的昵称
    
    # 基本信息
    birth_date = db.Column(db.Date, nullable=False)  # 出生年月日
    gender = db.Column(db.String(10), nullable=False)  # 性别：male/female/other
    contact_phone = db.Column(db.String(20))  # 联系电话
    mailing_address = db.Column(db.Text)  # 邮寄地址（用于3D模型邮寄）
    
    parent_email = db.Column(db.String(120), nullable=False)  # 家长邮箱（必须）
    avatar_url = db.Column(db.String(200), default='default_avatar.png')
    
    # 安全相关
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # 家长邮箱验证状态
    verification_token = db.Column(db.String(100), unique=True)
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 用户设置
    role = db.Column(db.String(20), default='student')  # 角色：teacher/parent/student
    color_preference = db.Column(db.String(20), default='vibrant')  # 色彩偏好
    privacy_settings = db.Column(db.JSON)  # 隐私设置JSON
    
    # 关联关系
    artworks = db.relationship('Artwork', backref='author', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('CreationSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, nickname, birth_date, gender, parent_email, password, contact_phone=None, mailing_address=None):
        self.username = username
        self.nickname = nickname
        self.birth_date = birth_date
        self.gender = gender
        self.contact_phone = contact_phone
        self.mailing_address = mailing_address
        self.parent_email = parent_email
        self.set_password(password)
        self.verification_token = str(uuid.uuid4())
        self.privacy_settings = {
            'show_in_gallery': True,
            'allow_sharing': True,
            'parental_controls': True
        }
    
    def get_age(self):
        """根据出生日期动态计算年龄"""
        if not self.birth_date:
            return None
        
        today = date.today()
        age = today.year - self.birth_date.year
        
        # 如果今年的生日还没到，年龄减1
        if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
            age -= 1
            
        return age
    
    @property
    def age(self):
        """年龄属性，便于模板使用"""
        return self.get_age()
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Flask-Login要求的方法"""
        return str(self.id)
    
    def is_active(self):
        """账户是否激活（需要家长验证）"""
        return self.is_verified
    
    def get_artwork_count(self):
        """获取作品数量"""
        return len(self.artworks)
    
    def get_total_creation_time(self):
        """获取总创作时间（分钟）"""
        total_seconds = sum([session.duration_seconds or 0 for session in self.sessions])
        return total_seconds // 60
    
    def to_dict(self):
        """转换为字典（用于API返回）"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'age': self.get_age(),
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'contact_phone': self.contact_phone,
            'mailing_address': self.mailing_address,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'artwork_count': self.get_artwork_count(),
            'total_creation_time': self.get_total_creation_time(),
            'created_at': self.created_at.isoformat(),
            'color_preference': self.color_preference
        }


class Artwork(db.Model):
    """艺术作品模型"""
    __tablename__ = 'artworks'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 文件路径
    original_sketch = db.Column(db.String(200))  # 原始简笔画
    colored_image = db.Column(db.String(200))   # AI上色结果
    figurine_image = db.Column(db.String(200))  # 手办风格图片
    model_3d = db.Column(db.String(200))        # 3D模型文件
    video_file = db.Column(db.String(200))      # 生成的视频
    
    # 创作参数
    style_type = db.Column(db.String(50))       # 风格类型
    color_preference = db.Column(db.String(20)) # 色彩偏好
    expert_mode = db.Column(db.Boolean, default=False)  # 是否使用Expert模式
    prompt_text = db.Column(db.Text)            # Expert模式的提示词
    
    # 视频相关
    video_prompt = db.Column(db.Text)           # 视频生成提示词
    video_aspect_ratio = db.Column(db.String(10))  # 16:9 或 9:16
    video_padding_mode = db.Column(db.String(20))  # black, blur, ai
    
    # 状态和时间
    status = db.Column(db.String(20), default='draft')  # draft, completed, shared
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用户关联
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 公开展示设置
    is_featured = db.Column(db.Boolean, default=False)  # 是否为用户推荐作品
    is_public = db.Column(db.Boolean, default=False)    # 是否公开展示
    featured_at = db.Column(db.DateTime)                # 设为推荐的时间
    
    # 统计数据
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    vote_count = db.Column(db.Integer, default=0)       # 投票数
    
    # 关联关系
    votes = db.relationship('ArtworkVote', backref='artwork', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, session_id, title, user_id):
        self.session_id = session_id
        self.title = title
        self.user_id = user_id
    
    def get_file_urls(self):
        """获取所有文件的URL"""
        base_url = f"/static/creation_sessions/{self.session_id}/"
        return {
            'original_sketch': f"{base_url}{self.original_sketch}" if self.original_sketch else None,
            'colored_image': f"{base_url}{self.colored_image}" if self.colored_image else None,
            'figurine_image': f"{base_url}{self.figurine_image}" if self.figurine_image else None,
            'model_3d': f"{base_url}{self.model_3d}" if self.model_3d else None,
            'video_file': f"{base_url}{self.video_file}" if self.video_file else None
        }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'description': self.description,
            'style_type': self.style_type,
            'color_preference': self.color_preference,
            'expert_mode': self.expert_mode,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'view_count': self.view_count,
            'like_count': self.like_count,
            'file_urls': self.get_file_urls(),
            'author': {
                'nickname': self.author.nickname,
                'avatar_url': self.author.avatar_url
            } if self.author else None
        }


class CreationSession(db.Model):
    """创作会话模型 - 记录用户的创作活动"""
    __tablename__ = 'creation_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 会话数据
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # 活动记录
    actions_log = db.Column(db.JSON)  # 存储用户操作日志
    
    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.user_id = user_id
        self.actions_log = []
    
    def add_action(self, action_type, description, metadata=None):
        """添加用户操作记录"""
        action = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': action_type,
            'description': description,
            'metadata': metadata or {}
        }
        if self.actions_log is None:
            self.actions_log = []
        self.actions_log.append(action)
    
    def end_session(self):
        """结束会话"""
        self.ended_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())


class ParentVerification(db.Model):
    """家长验证记录"""
    __tablename__ = 'parent_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_email = db.Column(db.String(120), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)  # 6位验证码
    is_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # 关联关系
    user = db.relationship('User', backref='parent_verifications')
    
    def __init__(self, user_id, parent_email, verification_code, expires_at):
        self.user_id = user_id
        self.parent_email = parent_email
        self.verification_code = verification_code
        self.expires_at = expires_at


class ArtworkVote(db.Model):
    """作品投票模型"""
    __tablename__ = 'artwork_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vote_type = db.Column(db.String(10), default='like')  # like, love, wow, cool
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    voter = db.relationship('User', backref='artwork_votes')
    
    # 确保同一用户对同一作品只能投一票
    __table_args__ = (db.UniqueConstraint('artwork_id', 'voter_id', name='unique_vote'),)
    
    def __init__(self, artwork_id, voter_id, vote_type='like'):
        self.artwork_id = artwork_id
        self.voter_id = voter_id
        self.vote_type = vote_type
    
    def is_expired(self):
        """验证码是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def verify(self):
        """验证成功"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()