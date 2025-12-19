"""画布相关路由"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import uuid

canvas_bp = Blueprint('canvas', __name__)


@canvas_bp.route('/')
@login_required
def canvas():
    """AI画布页面（原版）"""
    return render_template('canvas.html')


@canvas_bp.route('/infinite')
@canvas_bp.route('/-infinite')  # 兼容旧的URL格式
@login_required
def canvas_infinite():
    """AI画布页面（无限画布版本）"""
    return render_template('canvas_infinite.html')
