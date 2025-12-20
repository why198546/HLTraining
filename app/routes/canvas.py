"""画布相关路由"""
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

canvas_bp = Blueprint('canvas', __name__)


@canvas_bp.route('/')
@login_required
def canvas():
    """手绘画布页面"""
    return render_template('canvas_sketch.html')


@canvas_bp.route('/infinite')
@canvas_bp.route('/-infinite')  # 兼容旧的URL格式
@login_required
def canvas_infinite():
    """AI画布页面（无限画布版本）"""
    return render_template('canvas_infinite.html')
