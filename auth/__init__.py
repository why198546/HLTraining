"""
用户认证蓝图的初始化文件
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')