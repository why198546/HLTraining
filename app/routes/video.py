"""视频生成相关路由"""
from flask import Blueprint, render_template, request

video_bp = Blueprint('video', __name__)


@video_bp.route('/')
def video():
    """视频生成页面"""
    session_id = request.args.get('session_id', '')
    image_url = request.args.get('image_url', '')
    return render_template('video.html', session_id=session_id, image_url=image_url)
