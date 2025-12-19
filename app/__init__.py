"""Flask应用工厂"""
import os

from flask import Flask
from flask_login import LoginManager


def create_app():
    """创建并配置Flask应用"""
    from .config import BASE_DIR, Config
    
    app = Flask(__name__, 
                template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))
    app.config.from_object(Config)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化数据库
    from auth.models import User, db
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录才能访问此页面'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 初始化邮件服务
    from utils.email_service import init_mail
    init_mail(app)
    
    # 创建数据库表
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database tables created successfully")
        except Exception as e:
            print(f"[ERROR] Database creation failed: {e}")
    
    # 注册认证蓝图
    from auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # 注册应用路由蓝图
    from .routes import (api_bp, canvas_bp, create_bp, gallery_bp, main_bp,
                         model3d_bp, static_files_bp, video_bp)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(canvas_bp, url_prefix='/canvas')
    app.register_blueprint(create_bp, url_prefix='/create')
    app.register_blueprint(gallery_bp, url_prefix='/gallery')
    app.register_blueprint(video_bp, url_prefix='/video')
    app.register_blueprint(model3d_bp)  # 不加前缀，保持原URL兼容
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(static_files_bp)
    
    return app
