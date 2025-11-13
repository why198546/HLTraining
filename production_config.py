"""
生产环境配置
用于HLTraining项目的生产环境部署
"""
import os
from datetime import timedelta

class ProductionConfig:
    """生产环境配置类"""
    
    # 基础配置
    ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # 密钥配置（必须从环境变量读取）
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY环境变量未设置！请在.env文件中配置")
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/artworks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生产环境不输出SQL日志
    SQLALCHEMY_POOL_SIZE = 10  # 连接池大小
    SQLALCHEMY_POOL_TIMEOUT = 30  # 连接超时
    SQLALCHEMY_POOL_RECYCLE = 3600  # 连接回收时间（1小时）
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'glb', 'obj'}
    
    # 会话配置
    SESSION_COOKIE_SECURE = True  # 仅通过HTTPS传输
    SESSION_COOKIE_HTTPONLY = True  # 防止XSS攻击
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF保护
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # 会话有效期1小时
    
    # API密钥配置
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    NANO_BANANA_API_KEY = os.environ.get('NANO_BANANA_API_KEY')
    HUNYUAN3D_API_KEY = os.environ.get('HUNYUAN3D_API_KEY')
    
    # Notion集成配置
    NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/hltraining.log')
    
    # 安全头配置
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # CORS配置（如果需要）
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        import os
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('creation_sessions', exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('instance', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # 配置日志
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # 文件日志
            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10
            )
            file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
            file_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            ))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
            app.logger.info('HLTraining生产环境启动')


class DevelopmentConfig:
    """开发环境配置类"""
    
    ENV = 'development'
    DEBUG = True
    TESTING = False
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/artworks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 开发环境输出SQL日志
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    SESSION_COOKIE_SECURE = False  # 开发环境可以使用HTTP
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # API密钥
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    NANO_BANANA_API_KEY = os.environ.get('NANO_BANANA_API_KEY')
    HUNYUAN3D_API_KEY = os.environ.get('HUNYUAN3D_API_KEY')
    NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
    
    LOG_LEVEL = 'DEBUG'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
