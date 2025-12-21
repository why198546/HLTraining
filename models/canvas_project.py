"""Canvas项目数据库模型"""
from datetime import datetime

from auth.models import db


class CanvasProject(db.Model):
    """画布项目模型"""
    __tablename__ = 'canvas_projects'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 项目基本信息
    title = db.Column(db.String(200), nullable=False, default='未命名项目')
    project_type = db.Column(db.String(20), nullable=False)  # 'sketch' 或 'infinite'
    description = db.Column(db.Text)
    
    # 项目数据
    thumbnail = db.Column(db.Text)  # Base64编码的缩略图
    canvas_data = db.Column(db.Text)  # JSON字符串存储画布数据
    width = db.Column(db.Integer, default=512)
    height = db.Column(db.Integer, default=512)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_opened_at = db.Column(db.DateTime)
    
    # 关系
    user = db.relationship('User', backref=db.backref('canvas_projects', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'project_type': self.project_type,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_opened_at': self.last_opened_at.isoformat() if self.last_opened_at else None,
        }
    
    def __repr__(self):
        return f'<CanvasProject {self.id}: {self.title}>'
