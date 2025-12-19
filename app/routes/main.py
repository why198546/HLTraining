"""主页和通用路由"""
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')


@main_bp.route('/sunguo-class')
@login_required
def sunguo_class():
    """松果课堂导航页"""
    return render_template('sunguo_class.html')


@main_bp.route('/sunguo-class/<lesson_key>')
@login_required
def sunguo_lesson(lesson_key):
    """松果课堂单节课/综合练习页面"""
    lessons = {
        'character': {
            'title': '第 1 节课：人物',
            'desc': '从五官、发型、衣着等要素开始，组合出清晰的人物描述。',
            'section': 'character'
        },
        'action': {
            'title': '第 2 节课：动作',
            'desc': '学会用动词描述姿势与状态，让画面更生动。',
            'section': 'action'
        },
        'scene': {
            'title': '第 3 节课：场景',
            'desc': '选择环境与地点，给人物一个"发生故事"的舞台。',
            'section': 'scene'
        },
        'practice': {
            'title': '综合练习',
            'desc': '把人物 + 动作 + 场景组合成一句完整提示词，挑战更复杂的画面。',
            'section': 'mix'
        }
    }

    lesson = lessons.get(lesson_key)
    if not lesson:
        return "Not Found", 404

    return render_template('sunguo_lesson.html', lesson_key=lesson_key, lesson=lesson)


@main_bp.route('/tutorial')
def tutorial():
    """教程页面"""
    return render_template('tutorial.html')


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
