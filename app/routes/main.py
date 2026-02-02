"""主页和通用路由"""
import os

from flask import Blueprint, render_template, send_from_directory
from flask_login import login_required

from app.course_config.courses import get_all_courses, get_course, get_formal_courses

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')


@main_bp.route('/favicon.ico')
def favicon():
    """favicon图标"""
    # 使用SVG emoji作为favicon
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <text y="0.9em" font-size="90">🎨</text>
    </svg>''', 200, {'Content-Type': 'image/svg+xml'}


@main_bp.route('/sunguo-class')
@login_required
def sunguo_class():
    """松果课堂导航页"""
    return render_template('sunguo_class.html')


@main_bp.route('/sunguo-trial-courses')
@login_required
def sunguo_trial_courses():
    """松果体验课列表页"""
    return render_template('sunguo_trial_courses.html')


@main_bp.route('/sunguo-formal-courses')
@login_required
def sunguo_formal_courses():
    """松果正式课程列表页"""
    courses = get_formal_courses()
    # 按order排序
    sorted_courses = dict(sorted(courses.items(), key=lambda x: x[1].get('order', 999)))
    return render_template('sunguo_formal_courses.html', courses=sorted_courses)


@main_bp.route('/sunguo-formal/<lesson_key>')
@login_required
def sunguo_formal_lesson(lesson_key):
    """松果正式课程单节课页面"""
    lesson = get_course(lesson_key)
    if not lesson or lesson.get('type') != 'formal':
        return "Not Found", 404
    return render_template('sunguo_formal_lesson.html', lesson_key=lesson_key, lesson=lesson)


@main_bp.route('/sunguo-class/<lesson_key>')
@login_required
def sunguo_lesson(lesson_key):
    """松果课堂单节课/综合练习页面（体验课）"""
    lesson = get_course(lesson_key)
    if not lesson:
        return "Not Found", 404

    # 体验课程使用原模板
    if lesson.get('type') == 'trial':
        return render_template('sunguo_lesson.html', lesson_key=lesson_key, lesson=lesson)
    
    # 如果是正式课程，重定向到正式课程路由
    return "Please use /sunguo-formal/<lesson_key> for formal courses", 404


@main_bp.route('/sunguo-action-chooser')
@login_required
def sunguo_action_chooser():
    """松果课堂第 2 节课 - 动作方案选择页"""
    return render_template('sunguo_lesson_action_chooser.html')


@main_bp.route('/sunguo-action-v1')
@login_required
def sunguo_lesson_action_v1():
    """松果课堂第 2 节课 - 绘图板方案"""
    return render_template('sunguo_lesson_action_v1_canvas.html')


@main_bp.route('/sunguo-action-v2')
@login_required
def sunguo_lesson_action_v2():
    """松果课堂第 2 节课 - 拖拽编辑方案（增强版）"""
    return render_template('sunguo_lesson_action_v2_puppet_enhanced.html')


@main_bp.route('/tutorial')
def tutorial():
    """教程页面"""
    return render_template('tutorial.html')


@main_bp.route('/songuo-coin-demo')
def songuo_coin_demo():
    """松果币图标展示页面"""
    return render_template('songuo_coin_demo.html')


@main_bp.route('/test')
def test():
    """测试页面"""
    return render_template('test.html')


@main_bp.route('/debug')
def debug():
    """调试页面"""
    return render_template('debug.html')


@main_bp.route('/test-controls')
def test_controls():
    """测试控制页面"""
    return render_template('test_controls.html')


@main_bp.route('/simple-test')
def simple_test():
    """简单测试页面"""
    return render_template('simple_test.html')


@main_bp.route('/test-3d')
def test_3d():
    """3D测试页面"""
    return render_template('test_3d.html')


@main_bp.route('/gpu-test')
def gpu_test():
    """GPU加速测试页面"""
    return render_template('gpu_test.html')


@main_bp.route('/test-model')
def test_model():
    """测试3D模型展示"""
    return render_template('test_model.html')


@main_bp.route('/test-privacy-toggles')
def test_privacy_toggles():
    """隐私开关测试"""
    return render_template('test_privacy_toggles.html')


@main_bp.route('/test-content-indicators')
def test_content_indicators():
    """内容指示器测试"""
    return render_template('test_content_indicators.html')
