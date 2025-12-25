"""
权限和Token管理中间件
- 每日token自动赠送
- 试用期检查
"""

from datetime import date
from functools import wraps

from flask import flash, redirect, request, session, url_for
from flask_login import current_user

from auth.models import db


def grant_daily_tokens_if_needed():
    """
    在每次请求时检查是否需要赠送今日token
    此函数应该在请求处理之前调用（before_request）
    """
    if current_user.is_authenticated:
        # 检查并赠送每日token
        if current_user.grant_daily_tokens():
            db.session.commit()
            flash(f'🎁 今日token已到账！您获得了 {current_user.daily_token_amount} 个token', 'success')


def check_visitor_trial_period():
    """
    检查游客试用期是否过期
    如果过期且试图访问需要token的功能，则重定向到升级页面
    """
    if current_user.is_authenticated and current_user.role == 'visitor':
        if current_user.is_trial_expired():
            # 在特定路由才提示（避免每个页面都提示）
            if request.endpoint and any(keyword in request.endpoint for keyword in ['create', 'canvas', 'gallery']):
                flash('⏰ 您的试用期已结束，请扫描课程二维码升级账户以继续使用', 'warning')
                # 可以选择重定向到升级引导页
                # return redirect(url_for('auth.upgrade_guide'))


def init_middleware(app):
    """
    初始化中间件
    注册到Flask应用的before_request钩子
    """
    
    @app.before_request
    def before_request():
        """每个请求前执行"""
        # 静态文件不需要检查
        if request.endpoint and 'static' in request.endpoint:
            return
        
        # 赠送每日token
        grant_daily_tokens_if_needed()
        
        # 检查试用期
        check_visitor_trial_period()
