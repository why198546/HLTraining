"""API子模块 - 整合所有API蓝图"""
from flask import Blueprint

from .artwork import artwork_api_bp
from .canvas import canvas_api_bp
from .generation import generation_api_bp
from .session import session_api_bp
from .utils import utils_api_bp

# 创建主API蓝图
api_bp = Blueprint('api', __name__)

# 注册子蓝图
api_bp.register_blueprint(canvas_api_bp, url_prefix='/canvas')
api_bp.register_blueprint(artwork_api_bp, url_prefix='')
api_bp.register_blueprint(generation_api_bp, url_prefix='')
api_bp.register_blueprint(utils_api_bp, url_prefix='')
api_bp.register_blueprint(session_api_bp, url_prefix='')

__all__ = ['api_bp']
