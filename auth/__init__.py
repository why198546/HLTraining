"""
用户认证蓝图的初始化文件
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 导入路由（必须在创建蓝图之后）
from auth import routes
