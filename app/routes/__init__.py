"""路由模块"""
from .main import main_bp
from .canvas import canvas_bp
from .create import create_bp
from .gallery import gallery_bp
from .video import video_bp
from .model3d import model3d_bp
from .api import api_bp
from .static_files import static_files_bp

__all__ = [
    'main_bp',
    'canvas_bp',
    'create_bp',
    'gallery_bp',
    'video_bp',
    'model3d_bp',
    'api_bp',
    'static_files_bp',
]
