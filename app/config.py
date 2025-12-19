"""应用配置"""
import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """应用配置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "instance", "hltraining.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件配置
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@hltraining.com')
