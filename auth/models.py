"""
用户管理系统的数据库模型
支持儿童用户注册、作品管理和家长监护功能
"""

import os
import uuid
from datetime import date, datetime, timedelta

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

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
    
    # 权限管理
    image_token_remaining = db.Column(db.Integer, default=50)  # 剩余图片生成令牌，新用户默认50张
    is_enrolled = db.Column(db.Boolean, default=False)  # 是否已报名上课
    
    # 游客系统（新增）
    daily_token_amount = db.Column(db.Integer, default=0)  # 每日赠送token数量（游客10，正式学生30）
    trial_end_date = db.Column(db.DateTime, nullable=True)  # 游客试用结束日期
    last_token_grant_date = db.Column(db.Date, nullable=True)  # 上次赠送token日期
    course_type = db.Column(db.String(50), nullable=True)  # 课程类型（trial_course/formal_course）
    
    # 关联关系
    artworks = db.relationship('Artwork', backref='author', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('CreationSession', backref='user', lazy=True, cascade='all, delete-orphan')
    course_progress = db.relationship('CourseProgress', foreign_keys='CourseProgress.user_id', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, nickname, parent_email, password, birth_date=None, gender=None, contact_phone=None, mailing_address=None, role='visitor'):
        self.username = username
        self.nickname = nickname
        self.birth_date = birth_date
        self.gender = gender
        self.contact_phone = contact_phone
        self.mailing_address = mailing_address
        self.parent_email = parent_email
        self.role = role
        self.set_password(password)
        self.verification_token = str(uuid.uuid4())
        self.privacy_settings = {
            'show_in_gallery': True,
            'show_age': False,
            'allow_parent_reports': True
        }
        
        # 根据角色设置初始token和权限
        if role == 'visitor':
            self.daily_token_amount = 10
            self.image_token_remaining = 10  # 游客初始10个token
            self.trial_end_date = datetime.utcnow() + timedelta(days=7)  # 7天试用期
            self.last_token_grant_date = date.today()  # 注册当天已赠送
        elif role == 'student':
            self.daily_token_amount = 0  # 未报名学生不自动赠送
            self.image_token_remaining = 0
        elif role == 'teacher':
            self.daily_token_amount = 0  # 教师无限token，不需要自动赠送
            self.image_token_remaining = 999999  # 教师token设为极大值
        elif role == 'admin':
            self.daily_token_amount = 0
            self.image_token_remaining = 999999
    
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
    
    # ========== 游客系统相关方法 ==========
    
    def is_trial_expired(self):
        """检查游客试用期是否已过期"""
        if self.role != 'visitor' or not self.trial_end_date:
            return False
        return datetime.utcnow() > self.trial_end_date
    
    def get_trial_days_left(self):
        """获取试用期剩余天数"""
        if self.role != 'visitor' or not self.trial_end_date:
            return None
        days_left = (self.trial_end_date - datetime.utcnow()).days
        return max(0, days_left)
    
    def can_use_3d_model(self):
        """检查是否可以使用3D建模功能"""
        # 只有正式学生、教师、管理员可以使用
        return self.role in ['teacher', 'admin'] or (self.role == 'student' and self.is_enrolled)
    
    def can_use_video_generation(self):
        """检查是否可以使用视频生成功能"""
        # 只有正式学生、教师、管理员可以使用
        return self.role in ['teacher', 'admin'] or (self.role == 'student' and self.is_enrolled)
    
    def grant_daily_tokens(self):
        """赠送每日token"""
        today = date.today()
        
        # 如果今天已经赠送过，不重复赠送
        if self.last_token_grant_date == today:
            return False
        
        granted = False
        tokens_amount = 0
        
        # 游客检查试用期
        if self.role == 'visitor':
            if self.is_trial_expired():
                return False
            tokens_amount = self.daily_token_amount
            self.image_token_remaining += tokens_amount
            self.last_token_grant_date = today
            granted = True
        
        # 正式学生每日赠送
        elif self.role == 'student' and self.is_enrolled and self.daily_token_amount > 0:
            tokens_amount = self.daily_token_amount
            self.image_token_remaining += tokens_amount
            self.last_token_grant_date = today
            granted = True
        
        # 记录日志
        if granted and tokens_amount > 0:
            log = TokenGrantLog(
                user_id=self.id,
                grant_type='daily_grant',
                tokens_granted=tokens_amount,
                description=f'每日自动赠送 {tokens_amount} 松果币'
            )
            db.session.add(log)
        
        return granted
    
    def upgrade_to_trial_student(self, additional_tokens=50, course_id=None, course_name=None):
        """升级为体验课学生（扫描体验课二维码）"""
        if self.role == 'visitor':
            self.role = 'student'
        self.is_enrolled = False
        self.course_type = 'trial_course'
        self.image_token_remaining += additional_tokens
        self.trial_end_date = None  # 清除试用期限制
        self.daily_token_amount = 0  # 体验课学生不自动赠送token
        
        # 记录日志
        log = TokenGrantLog(
            user_id=self.id,
            grant_type='qr_scan_trial',
            tokens_granted=additional_tokens,
            description=f'扫描体验课二维码获得 {additional_tokens} 松果币',
            related_id=course_id,
            related_info=course_name
        )
        db.session.add(log)
        db.session.commit()
    
    def upgrade_to_formal_student(self, course_id=None, course_name=None):
        """升级为正式学生（扫描正式课程二维码）"""
        self.role = 'student'
        self.is_enrolled = True
        self.course_type = 'formal_course'
        self.daily_token_amount = 30  # 每天赠送30个token
        self.trial_end_date = None  # 清除试用期限制
        self.last_token_grant_date = date.today()
        
        # 记录日志（正式课解锁每日30个token）
        log = TokenGrantLog(
            user_id=self.id,
            grant_type='qr_scan_formal',
            tokens_granted=0,  # 正式课不直接赠送，而是解锁每日30个
            description=f'扫描正式课二维码，解锁每日 {self.daily_token_amount} 松果币',
            related_id=course_id,
            related_info=course_name
        )
        db.session.add(log)
        db.session.commit()
    
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
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 项目信息
    title = db.Column(db.String(200), default='未命名项目')
    project_type = db.Column(db.String(20), default='infinite')  # 'sketch' 或 'infinite'
    description = db.Column(db.Text)
    thumbnail = db.Column(db.String(500))  # 项目缩略图
    
    # 画布尺寸
    width = db.Column(db.Integer, default=512)
    height = db.Column(db.Integer, default=512)
    
    # 画布数据
    canvas_data = db.Column(db.JSON)  # 存储画布中的所有图片及其位置、尺寸
    chat_history = db.Column(db.JSON)  # 存储对话历史
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    last_opened_at = db.Column(db.DateTime)  # 最后打开时间
    
    # 统计信息
    image_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 关联用户
    user = db.relationship('User', backref='canvas_projects')
    
    def __init__(self, project_id, user_id, title='未命名项目', project_type='infinite', **kwargs):
        self.project_id = project_id
        self.user_id = user_id
        self.title = title
        self.project_type = project_type
        self.canvas_data = kwargs.get('canvas_data', {'images': []})
        self.chat_history = kwargs.get('chat_history', [])
        self.image_count = kwargs.get('image_count', 0)
        self.width = kwargs.get('width', 512)
        self.height = kwargs.get('height', 512)
        self.thumbnail = kwargs.get('thumbnail')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'project_type': self.project_type,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'width': self.width,
            'height': self.height,
            'canvas_data': self.canvas_data,
            'chat_history': self.chat_history,
            'image_count': self.image_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'last_opened_at': self.last_opened_at.isoformat() if self.last_opened_at else None,
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


class CourseProgress(db.Model):
    """课程进度模型 - 追踪学生的课程学习进度"""
    __tablename__ = 'course_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)  # 课程编号（1, 2, 3...）
    lesson_key = db.Column(db.String(50), nullable=False)  # 课程标识（如 'lesson1', 'lesson2'）
    
    # 进度状态
    is_completed = db.Column(db.Boolean, default=False)  # 是否完成
    is_confirmed = db.Column(db.Boolean, default=False)  # 老师是否确认
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 确认老师的ID
    confirmed_at = db.Column(db.DateTime, nullable=True)  # 确认时间
    
    # 学习记录
    started_at = db.Column(db.DateTime, default=datetime.utcnow)  # 开始时间
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间
    notes = db.Column(db.Text, nullable=True)  # 老师备注
    
    # 创建唯一约束：每个学生的每节课只有一条记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_number', name='unique_user_lesson'),
    )
    
    # 关联关系
    confirming_teacher = db.relationship('User', foreign_keys=[confirmed_by])
    
    def __init__(self, user_id, lesson_number, lesson_key):
        self.user_id = user_id
        self.lesson_number = lesson_number
        self.lesson_key = lesson_key
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_number': self.lesson_number,
            'lesson_key': self.lesson_key,
            'is_completed': self.is_completed,
            'is_confirmed': self.is_confirmed,
            'confirmed_by': self.confirmed_by,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes
        }


class Course(db.Model):
    """课程二维码模型 - 存储生成的课程二维码信息"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(100), unique=True, nullable=False, index=True)  # UUID唯一代码
    course_name = db.Column(db.String(100), nullable=False)  # 课程名称
    course_key = db.Column(db.String(50), nullable=True)  # 课程key（来自courses.py配置）
    course_type = db.Column(db.String(50), nullable=False)  # 课程类型：trial_course/formal_course
    
    # 创建者信息
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 创建者ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    # 使用限制
    max_uses = db.Column(db.Integer, nullable=True)  # 最大使用次数（None表示无限制）
    current_uses = db.Column(db.Integer, default=0)  # 当前使用次数
    expires_at = db.Column(db.DateTime, nullable=True)  # 过期时间（None表示永久有效）
    
    # 奖励信息
    tokens_reward = db.Column(db.Integer, default=0)  # 扫码赠送的松果币数量
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    qr_image_path = db.Column(db.String(200))  # 二维码图片路径
    
    # 统计信息
    description = db.Column(db.Text)  # 课程描述
    
    # 关联关系
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_courses')
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, course_code, course_name, course_type, created_by, course_key=None, 
                 max_uses=None, expires_at=None, description=None, tokens_reward=0):
        self.course_code = course_code
        self.course_name = course_name
        self.course_key = course_key
        self.course_type = course_type
        self.created_by = created_by
        self.max_uses = max_uses
        self.expires_at = expires_at
        self.description = description
        self.tokens_reward = tokens_reward
    
    def is_valid(self):
        """检查课程二维码是否有效"""
        # 检查是否激活
        if not self.is_active:
            return False, '该二维码已被停用'
        
        # 检查是否过期
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, '该二维码已过期'
        
        # 检查使用次数
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, '该二维码使用次数已达上限'
        
        return True, '有效'
    
    def increment_usage(self):
        """增加使用次数"""
        self.current_uses += 1
        db.session.commit()
    
    def get_usage_stats(self):
        """获取使用统计"""
        return {
            'total_enrollments': len(self.enrollments),
            'current_uses': self.current_uses,
            'max_uses': self.max_uses if self.max_uses else '无限制',
            'remaining_uses': (self.max_uses - self.current_uses) if self.max_uses else '无限制',
            'is_expired': self.expires_at and datetime.utcnow() > self.expires_at if self.expires_at else False,
            'expires_at': self.expires_at.strftime('%Y-%m-%d %H:%M') if self.expires_at else '永久有效'
        }
    
    def to_dict(self):
        """转换为字典"""
        valid, msg = self.is_valid()
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'course_key': self.course_key,
            'course_type': self.course_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'max_uses': self.max_uses,
            'current_uses': self.current_uses,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_valid': valid,
            'validation_message': msg,
            'qr_image_path': self.qr_image_path,
            'description': self.description,
            'tokens_reward': self.tokens_reward
        }


class CourseEnrollment(db.Model):
    """课程报名记录 - 记录学生扫描二维码的历史"""
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # 课程ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 学生ID
    
    # 扫描信息
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)  # 扫描时间
    ip_address = db.Column(db.String(50))  # 扫描时的IP地址
    user_agent = db.Column(db.String(500))  # 扫描时的浏览器信息
    
    # 升级结果
    previous_role = db.Column(db.String(20))  # 扫描前的角色
    new_role = db.Column(db.String(20))  # 扫描后的角色
    tokens_granted = db.Column(db.Integer, default=0)  # 赠送的token数量
    
    # 关联关系
    student = db.relationship('User', foreign_keys=[user_id], backref='enrollments')
    
    def __init__(self, course_id, user_id, previous_role, new_role, tokens_granted=0, 
                 ip_address=None, user_agent=None):
        self.course_id = course_id
        self.user_id = user_id
        self.previous_role = previous_role
        self.new_role = new_role
        self.tokens_granted = tokens_granted
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'scanned_at': self.scanned_at.isoformat(),
            'previous_role': self.previous_role,
            'new_role': self.new_role,
            'tokens_granted': self.tokens_granted,
            'ip_address': self.ip_address
        }


class TokenUsageLog(db.Model):
    """松果币消耗记录"""
    __tablename__ = 'token_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    usage_type = db.Column(db.String(20), nullable=False)  # 'image' 或 'video'
    tokens_used = db.Column(db.Integer, nullable=False)  # 消耗的松果币数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    description = db.Column(db.String(200))  # 描述信息
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('token_usage_logs', lazy=True))
    
    def __repr__(self):
        return f'<TokenUsageLog {self.user_id} {self.usage_type} -{self.tokens_used}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'nickname': self.user.nickname if self.user else None,
            'usage_type': self.usage_type,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat(),
            'description': self.description
        }


class TokenGrantLog(db.Model):
    """松果币获得记录"""
    __tablename__ = 'token_grant_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    grant_type = db.Column(db.String(30), nullable=False)  # 获得类型
    # grant_type 取值：
    # - 'daily_grant': 每日自动赠送
    # - 'qr_scan_trial': 二维码扫描（体验课）
    # - 'qr_scan_formal': 二维码扫描（正式课）
    # - 'admin_manual': 管理员手动增加
    # - 'teacher_manual': 教师手动增加
    # - 'purchase': 购买获得（预留）
    # - 'activity_reward': 活动奖励（预留）
    # - 'refund': 退款补偿（预留）
    
    tokens_granted = db.Column(db.Integer, nullable=False)  # 获得的松果币数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    description = db.Column(db.String(200))  # 描述信息
    
    # 操作者信息（如果是管理员或教师手动添加）
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    operator_name = db.Column(db.String(50))  # 操作者姓名
    
    # 关联信息（如二维码ID、订单ID等）
    related_id = db.Column(db.Integer, nullable=True)  # 关联ID（如course_id）
    related_info = db.Column(db.String(200))  # 关联信息（如课程名称）
    
    # 关联关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('token_grant_logs', lazy=True))
    operator = db.relationship('User', foreign_keys=[operator_id])
    
    def __repr__(self):
        return f'<TokenGrantLog {self.user_id} {self.grant_type} +{self.tokens_granted}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'nickname': self.user.nickname if self.user else None,
            'grant_type': self.grant_type,
            'grant_type_display': self.get_grant_type_display(),
            'tokens_granted': self.tokens_granted,
            'created_at': self.created_at.isoformat(),
            'description': self.description,
            'operator_id': self.operator_id,
            'operator_name': self.operator_name,
            'related_info': self.related_info
        }
    
    def get_grant_type_display(self):
        """获取grant_type的中文显示"""
        return self.get_grant_type_display_static(self.grant_type)
    
    @staticmethod
    def get_grant_type_display_static(grant_type):
        """获取grant_type的中文显示（静态方法）"""
        type_map = {
            'daily_grant': '每日赠送',
            'qr_scan_trial': '二维码扫描（体验课）',
            'qr_scan_formal': '二维码扫描（正式课）',
            'admin_manual': '管理员手动增加',
            'teacher_manual': '教师手动增加',
            'purchase': '购买获得',
            'activity_reward': '活动奖励',
            'refund': '退款补偿'
        }
        return type_map.get(grant_type, grant_type)
