"""
打印图片记录模型
"""
from datetime import datetime
from auth.models import db

class PrintedImage(db.Model):
    """打印图片记录 - 记录用户打印过的图片"""
    __tablename__ = 'printed_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_key = db.Column(db.String(100), nullable=False, index=True)  # 课程标识
    image_url = db.Column(db.String(500), nullable=False)  # 图片URL
    printed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<PrintedImage {self.id}: {self.image_url[:50]}... by user {self.user_id}>'
    
    @staticmethod
    def mark_as_printed(user_id, lesson_key, image_url):
        """标记图片为已打印"""
        # 检查是否已存在记录
        existing = PrintedImage.query.filter_by(
            user_id=user_id,
            lesson_key=lesson_key,
            image_url=image_url
        ).first()
        
        if not existing:
            printed_img = PrintedImage(
                user_id=user_id,
                lesson_key=lesson_key,
                image_url=image_url
            )
            db.session.add(printed_img)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_printed_images(user_id, lesson_key, date_filter=None):
        """获取用户在某课程打印过的图片列表"""
        query = PrintedImage.query.filter_by(
            user_id=user_id,
            lesson_key=lesson_key
        )
        
        # 如果指定日期，只返回当天的
        if date_filter:
            query = query.filter(
                db.func.date(PrintedImage.printed_at) == date_filter
            )
        
        return query.all()
    
    @staticmethod
    def is_printed(user_id, lesson_key, image_url):
        """检查图片是否已被打印过"""
        return PrintedImage.query.filter_by(
            user_id=user_id,
            lesson_key=lesson_key,
            image_url=image_url
        ).first() is not None
