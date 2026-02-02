"""Flask应用工厂"""
import os
import time
from pathlib import Path

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
    from auth.models import CanvasProject, User, db
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
    
    # 注册二维码蓝图
    from auth.qr_routes import qr_bp
    app.register_blueprint(qr_bp)
    
    # 注册管理员蓝图
    from auth.admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    
    # 初始化中间件（每日token赠送等）
    from auth.middleware import init_middleware
    init_middleware(app)
    
    # 初始化定时任务调度器
    from utils.scheduler import init_scheduler
    init_scheduler(app)
    
    # 注册应用路由蓝图
    from .routes import (canvas_bp, create_bp, gallery_bp, main_bp, model3d_bp,
                         static_files_bp, video_bp)
    from .routes.api import api_bp  # 从api子模块导入
    from .routes.api_create import api_create_bp  # 创作相关API
    from .routes.crop_api import crop_api_bp  # 裁剪API
    from .routes.formal_lesson import formal_lesson_bp  # 正式课程API
    
    app.register_blueprint(main_bp)
    app.register_blueprint(canvas_bp, url_prefix='/canvas')
    app.register_blueprint(create_bp, url_prefix='/create')
    app.register_blueprint(gallery_bp, url_prefix='/gallery')
    app.register_blueprint(video_bp, url_prefix='/video')
    app.register_blueprint(model3d_bp)  # 不加前缀，保持原URL兼容
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_create_bp)  # 创作API（已包含/api前缀）
    app.register_blueprint(crop_api_bp)  # 裁剪API
    app.register_blueprint(formal_lesson_bp)  # 正式课程API（已包含/api前缀）
    app.register_blueprint(static_files_bp)
    
    # 添加自动版本号到模板上下文
    @app.context_processor
    def inject_version():
        """为模板注入静态文件版本号（基于文件修改时间）"""
        def get_static_version(filename):
            """获取静态文件的版本号（基于修改时间戳）"""
            try:
                static_path = Path(app.static_folder) / filename
                if static_path.exists():
                    # 使用文件修改时间戳作为版本号
                    mtime = int(static_path.stat().st_mtime)
                    return str(mtime)
                else:
                    # 文件不存在时使用当前时间戳
                    return str(int(time.time()))
            except Exception:
                # 出错时使用当前时间戳
                return str(int(time.time()))
        
        return dict(static_version=get_static_version)
    
    return app
