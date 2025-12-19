"""
用户管理系统的数据库模型
支持儿童用户注册、作品管理和家长监护功能
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型 - 专为10-14岁儿童设计"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(50), nullable=False)  # 儿童友好的昵称
    
    # 基本信息
    birth_date = db.Column(db.Date, nullable=True)  # 出生年月日
    gender = db.Column(db.String(10), nullable=True)  # 性别：male/female/other
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
    
    def __init__(self, username, nickname, parent_email, password, birth_date=None, gender=None, contact_phone=None, mailing_address=None):
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
            'show_age': False,
            'allow_parent_reports': True
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
    colored_image = db.Column(db.String(200))   # AI上色结果（主要展示）
    figurine_image = db.Column(db.String(200))  # 手办风格图片
    model_3d = db.Column(db.String(200))        # 3D模型文件
    video_file = db.Column(db.String(200))      # 生成的视频
    
    # 所有版本历史（JSON格式存储文件名列表）
    all_colored_versions = db.Column(db.JSON)   # 所有AI生成的图片版本
    all_adjusted_versions = db.Column(db.JSON)  # 所有调整后的图片版本
    
    # 创作者信息
    artist_name = db.Column(db.String(50))      # 创作者姓名
    artist_age = db.Column(db.Integer)          # 创作者年龄
    category = db.Column(db.String(50))         # 作品分类
    
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
        """生成文件URL，智能检测文件位置"""
        def get_file_url(filename):
            if not filename:
                return None
            
            # 如果文件名已经包含路径，直接使用
            if filename.startswith('/') or filename.startswith('http'):
                return filename
            
            # 优先检查 uploads 目录（新的保存位置）
            uploads_path = f"uploads/{filename}"
            if os.path.exists(uploads_path):
                return f"/uploads/{filename}"
            
            # 检查 static/creation_sessions 目录
            if self.session_id:
                static_path = f"static/creation_sessions/{self.session_id}/{filename}"
                if os.path.exists(static_path):
                    return f"/static/creation_sessions/{self.session_id}/{filename}"
                
                # 检查 creation_sessions 目录
                creation_path = f"creation_sessions/{self.session_id}/{filename}"
                if os.path.exists(creation_path):
                    return f"/creation_sessions/{self.session_id}/{filename}"
            
            # 如果都不存在，尝试 uploads 作为默认路径
            return f"/uploads/{filename}"
        
        return {
            'original_sketch': get_file_url(self.original_sketch),
            'colored_image': get_file_url(self.colored_image),
            'figurine_image': get_file_url(self.figurine_image),
            'model_3d': get_file_url(self.model_3d),
            'video_file': get_file_url(self.video_file)
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
    
    def is_expired(self):
        """检查验证码是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def verify(self):
        """标记为已验证"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()


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


class ArtworkView(db.Model):
    """作品浏览记录模型"""
    __tablename__ = 'artwork_views'
    
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    viewer = db.relationship('User', backref='artwork_views')
    
    # 确保同一用户对同一作品只记录一次浏览
    __table_args__ = (db.UniqueConstraint('artwork_id', 'viewer_id', name='unique_view'),)
    
    def __init__(self, artwork_id, viewer_id):
        self.artwork_id = artwork_id
        self.viewer_id = viewer_id


class Comment(db.Model):
    """作品评论模型 - 支持文字和语音评论"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 评论内容
    content = db.Column(db.Text, nullable=False)  # 文字内容（语音转换后的文字）
    audio_file = db.Column(db.String(200))  # 音频文件路径（可选）
    is_voice_comment = db.Column(db.Boolean, default=False)  # 是否通过语音输入
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 状态
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    
    # 关联关系
    artwork = db.relationship('Artwork', backref=db.backref('comments', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    
    def __init__(self, artwork_id, user_id, content, audio_file=None, is_voice_comment=False):
        self.artwork_id = artwork_id
        self.user_id = user_id
        self.content = content
        self.audio_file = audio_file
        self.is_voice_comment = is_voice_comment
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'artwork_id': self.artwork_id,
            'content': self.content,
            'audio_file': f'/uploads/{self.audio_file}' if self.audio_file else None,
            'is_voice_comment': self.is_voice_comment,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': self.user.id,
                'nickname': self.user.nickname,
                'avatar_url': self.user.avatar_url,
                'age': self.user.get_age()
            }
        }


class CanvasProject(db.Model):
    """画布项目模型 - 存储用户的画布项目"""
    __tablename__ = 'canvas_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 项目信息
    title = db.Column(db.String(200), default='未命名项目')
    description = db.Column(db.Text)
    thumbnail = db.Column(db.String(500))  # 项目缩略图
    
    # 画布数据
    canvas_data = db.Column(db.JSON)  # 存储画布中的所有图片及其位置、尺寸
    chat_history = db.Column(db.JSON)  # 存储对话历史
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 统计信息
    image_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 关联用户
    user = db.relationship('User', backref='canvas_projects')
    
    def __init__(self, project_id, user_id, title='未命名项目'):
        self.project_id = project_id
        self.user_id = user_id
        self.title = title
        self.canvas_data = {'images': []}
        self.chat_history = []
        self.image_count = 0
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'canvas_data': self.canvas_data,
            'chat_history': self.chat_history,
            'image_count': self.image_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }
    
    def update_canvas_data(self, canvas_data):
        """更新画布数据"""
        self.canvas_data = canvas_data
        self.image_count = len(canvas_data.get('images', []))
        self.updated_at = datetime.utcnow()
    
    def add_chat_message(self, role, content, metadata=None):
        """添加对话记录"""
        if self.chat_history is None:
            self.chat_history = []
        message = {
            'timestamp': datetime.utcnow().isoformat(),
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'metadata': metadata or {}
        }
        self.chat_history.append(message)
        self.updated_at = datetime.utcnow()

