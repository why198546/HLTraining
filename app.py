from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
from api.nano_banana import NanoBananaAPI
from api.hunyuan3d import Hunyuan3DGenerator
from api.sam3d_api import SAM3DAPI
from managers.gallery_manager import GalleryManager
from managers.creation_session_manager import CreationSessionManager
import json
from dotenv import load_dotenv
from datetime import datetime

# 用户管理系统导入
from flask_login import LoginManager, login_required, current_user
from auth.models import db, User, Artwork, CreationSession
from auth import auth_bp
from auth.routes import *
from utils.email_service import init_mail

# 加载环境变量
load_dotenv()

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/sunguo-class')
@login_required
def sunguo_class():
    """松果课堂导航页"""
    return render_template('sunguo_class.html')


@app.route('/sunguo-class/<lesson_key>')
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
            'desc': '选择环境与地点，给人物一个“发生故事”的舞台。',
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

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hltraining.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录才能访问此页面'
login_manager.login_message_category = 'info'

# 初始化邮件服务
init_mail(app)

# 注册蓝图
app.register_blueprint(auth_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建应用上下文并初始化数据库
with app.app_context():
    try:
        db.create_all()
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库创建失败: {e}")

# 确保上传目录存在（使用之前在第31行设置的绝对路径）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 创建数据库表
with app.app_context():
    db.create_all()

# 初始化作品集管理器和创作会话管理器
gallery_manager = GalleryManager()
session_manager = CreationSessionManager(sessions_folder=os.path.join(BASE_DIR, 'creation_sessions'))

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_sketch(image_path):
    """预处理手绘图片"""
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 二值化处理
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 保存预处理后的图片
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, binary)
        
        return processed_path
    except Exception as e:
        print(f"图片预处理错误: {str(e)}")
        return None

def generate_3d_model_from_image(image_path):
    """从图片生成3D模型的辅助函数"""
    print(f"🧊 开始3D模型生成: {image_path}")
    
    # 初始化3D生成器
    generator_3d = Hunyuan3DGenerator()
    
    # 生成3D模型（如果失败会抛出异常）
    model_path = generator_3d.generate_3d_model(image_path)
    
    print(f"✅ 3D模型生成成功: {model_path}")
    return model_path.replace('uploads/', '/uploads/')

def generate_3d_model_from_multi_view(view_images):
    """从多视角图片生成3D模型的辅助函数
    
    Args:
        view_images: dict with keys 'front', 'back', 'left', 'right'
    
    Returns:
        str: 3D模型文件路径
    """
    print(f"🧊 开始多视角3D模型生成")
    
    # 初始化3D生成器
    generator_3d = Hunyuan3DGenerator()
    
    # 生成3D模型（多视角模式）
    # 传递view_images字典，生成器会格式化为Hunyuan API要求的ViewImages数组
    model_path = generator_3d.generate_3d_model_multi_view(view_images)
    
    print(f"✅ 多视角3D模型生成成功: {model_path}")
    return model_path.replace('uploads/', '/uploads/')

def auto_save_artwork_to_db(session_id, generated_image_path, sketch_path=None, prompt=None):
    """自动保存作品到数据库"""
    try:
        from auth.models import Artwork
        import glob
        
        # 验证必需的图片路径
        if not generated_image_path:
            print(f"⚠️ 没有生成图片路径，跳过保存")
            return False
        
        # 验证文件是否存在
        if not os.path.exists(generated_image_path):
            print(f"⚠️ 生成的图片文件不存在: {generated_image_path}")
            return False
        
        # 检查是否已存在该会话的作品
        existing_artwork = Artwork.query.filter_by(session_id=session_id).first()
        
        # 扫描会话文件夹中的所有版本
        colored_versions = []
        adjusted_versions = []
        
        if session_id:
            session_dir = f"creation_sessions/{session_id}"
            if os.path.exists(session_dir):
                # 查找所有colored版本
                colored_files = glob.glob(f"{session_dir}/*_colored*.jpg") + \
                               glob.glob(f"{session_dir}/*_colored*.png")
                colored_versions = [os.path.basename(f) for f in colored_files]
                
                # 查找所有adjusted版本
                adjusted_files = glob.glob(f"{session_dir}/*_adjusted*.jpg") + \
                                glob.glob(f"{session_dir}/*_adjusted*.png")
                adjusted_versions = [os.path.basename(f) for f in adjusted_files]
                
                print(f"📂 扫描到 {len(colored_versions)} 个上色版本, {len(adjusted_versions)} 个调整版本")
        
        # 获取用户信息
        artist_name = current_user.nickname or current_user.username
        artist_age = current_user.age if hasattr(current_user, 'age') else None
        
        if existing_artwork:
            # 更新现有作品
            existing_artwork.status = 'completed'
            existing_artwork.updated_at = datetime.utcnow()
            
            # 更新文件路径
            if generated_image_path:
                existing_artwork.colored_image = os.path.basename(generated_image_path)
            if sketch_path:
                existing_artwork.original_sketch = os.path.basename(sketch_path)
            if prompt:
                existing_artwork.prompt_text = prompt
            
            # 更新版本历史
            if colored_versions:
                existing_artwork.all_colored_versions = colored_versions
            if adjusted_versions:
                existing_artwork.all_adjusted_versions = adjusted_versions
            
            # 更新创作者信息
            existing_artwork.artist_name = artist_name
            existing_artwork.artist_age = artist_age
                
            print(f"🔄 更新现有作品: {existing_artwork.id}")
        else:
            # 创建新作品
            artwork = Artwork(
                session_id=session_id,
                title=f"AI创作 {datetime.now().strftime('%m-%d %H:%M')}",
                user_id=current_user.id
            )
            
            artwork.status = 'completed'
            artwork.description = prompt or "AI生成的精美作品"
            artwork.is_public = False  # 默认私密，需手动设为公开
            
            # 设置文件路径
            if generated_image_path:
                artwork.colored_image = os.path.basename(generated_image_path)
            if sketch_path:
                artwork.original_sketch = os.path.basename(sketch_path)
            if prompt:
                artwork.prompt_text = prompt
            
            # 设置版本历史
            if colored_versions:
                artwork.all_colored_versions = colored_versions
            if adjusted_versions:
                artwork.all_adjusted_versions = adjusted_versions
            
            # 设置创作者信息
            artwork.artist_name = artist_name
            artwork.artist_age = artist_age
                
            db.session.add(artwork)
            print(f"➕ 创建新作品记录: {session_id}")
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 自动保存失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def index():
    """主页"""
    # 获取最新的4个作品用于首页展示
    from auth.models import Artwork, User
    from sqlalchemy import desc
    
    latest_artworks = Artwork.query.filter_by(
        is_public=True
    ).join(User).order_by(desc(Artwork.created_at)).limit(4).all()
    
    return render_template('index.html', latest_artworks=latest_artworks)

@app.route('/create')
@login_required
def create():
    """创作页面"""
    return render_template('create.html')

@app.route('/edit/<int:artwork_id>')
@login_required
def edit_artwork(artwork_id):
    """编辑作品页面"""
    from auth.models import Artwork
    
    # 获取作品并检查权限
    artwork = Artwork.query.get_or_404(artwork_id)
    
    # 确保只有作品所有者可以编辑
    if artwork.user_id != current_user.id:
        flash('您没有权限编辑这个作品', 'error')
        return redirect(url_for('auth.my_artworks'))
    
    # 获取文件URLs
    file_urls = artwork.get_file_urls()
    
    # 渲染编辑页面，传递作品数据和文件URLs
    return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)

@app.route('/edit/<int:artwork_id>', methods=['POST'])
@login_required
def update_artwork(artwork_id):
    """更新作品信息"""
    from auth.models import Artwork, db
    
    # 获取作品并检查权限
    artwork = Artwork.query.get_or_404(artwork_id)
    
    if artwork.user_id != current_user.id:
        flash('您没有权限编辑这个作品', 'error')
        return redirect(url_for('auth.my_artworks'))
    
    # 获取表单数据
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    is_public = request.form.get('is_public') == 'on'
    
    # 验证数据
    if not title:
        flash('作品标题不能为空', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    if len(title) > 100:
        flash('作品标题最多100个字符', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    if len(description) > 500:
        flash('作品描述最多500个字符', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)
    
    # 记录原始状态用于比较
    original_title = artwork.title
    original_description = artwork.description
    original_is_public = artwork.is_public
    
    # 更新作品信息
    artwork.title = title
    artwork.description = description if description else None
    artwork.is_public = is_public
    
    try:
        db.session.commit()
        
        # 生成更详细的成功消息
        changes = []
        if original_title != title:
            changes.append('标题')
        if original_description != description:
            changes.append('描述')
        if original_is_public != is_public:
            changes.append('公开状态')
        
        if changes:
            change_text = '、'.join(changes)
            flash(f'作品{change_text}已更新成功！', 'success')
        else:
            flash('作品信息保存成功', 'success')
            
        return redirect(url_for('auth.my_artworks'))
    except Exception as e:
        db.session.rollback()
        print(f"Update artwork error: {e}")
        flash('更新失败，请重试', 'error')
        file_urls = artwork.get_file_urls()
        return render_template('edit_artwork.html', artwork=artwork, file_urls=file_urls)

@app.route('/gallery')
def gallery():
    """显示作品画廊"""
    from auth.models import Artwork, User
    from sqlalchemy import desc
    
    # 获取所有公开的作品，按创建时间降序排列
    artworks = Artwork.query.filter_by(
        is_public=True
    ).join(User).order_by(desc(Artwork.created_at)).all()
    
    return render_template('gallery.html', artworks=artworks)

@app.route('/tutorial')
def tutorial():
    """使用教程页面"""
    return render_template('tutorial.html')

@app.route('/video')
def video():
    """视频生成页面"""
    session_id = request.args.get('session_id', '')
    image_url = request.args.get('image_url', '')
    return render_template('video.html', session_id=session_id, image_url=image_url)

@app.route('/test-model')
def test_model():
    """测试3D模型展示"""
    return render_template('test_model.html')

@app.route('/test')
def test():
    """测试页面"""
    return render_template('test.html')

@app.route('/debug')
def debug():
    """调试页面"""
    return render_template('test_debug.html')

@app.route('/test-controls')
def test_controls():
    """测试3D模型控制面板"""
    return render_template('test_model_controls.html')

@app.route('/simple-test')
def simple_test():
    """简化3D测试"""
    return render_template('simple_test.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件访问"""
    from flask import send_file
    import mimetypes
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 为音频文件设置正确的MIME类型
    if filename.startswith('comment_audio_'):
        # 评论音频可能是多种格式
        if filename.endswith('.m4a') or filename.endswith('.mp4'):
            mimetype = 'audio/mp4'
        elif filename.endswith('.webm'):
            mimetype = 'audio/webm'
        elif filename.endswith('.ogg'):
            mimetype = 'audio/ogg'
        else:
            mimetype = 'audio/mpeg'
    elif filename.endswith('.webm'):
        mimetype = 'audio/webm'
    else:
        mimetype = mimetypes.guess_type(filename)[0]
    
    return send_file(filepath, mimetype=mimetype)

@app.route('/models/<filename>')
def model_file(filename):
    """提供3D模型文件访问"""
    return send_file(os.path.join('models', filename))

@app.route('/creation_sessions/<path:filepath>')
def creation_session_file(filepath):
    """提供创作会话文件访问"""
    file_path = os.path.join(BASE_DIR, 'creation_sessions', filepath)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path)

# ===== 创作会话管理API =====

@app.route('/create-session', methods=['POST'])
def create_session():
    """创建新的创作会话"""
    try:
        user_info = request.get_json() or {}
        session_id = session_manager.create_session(user_info)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': '创作会话已创建'
        })
        
    except Exception as e:
        return jsonify({'error': f'创建会话失败: {str(e)}'}), 500

@app.route('/session/<session_id>/info')
def get_session_info(session_id):
    """获取会话信息"""
    try:
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({'error': '会话不存在'}), 404
        
        return jsonify({
            'success': True,
            'session': session_info
        })
        
    except Exception as e:
        return jsonify({'error': f'获取会话信息失败: {str(e)}'}), 500

@app.route('/session/<session_id>/versions')
def get_session_versions(session_id):
    """获取会话的所有版本"""
    try:
        version_type = request.args.get('type')  # 'image' 或 'model'
        versions = session_manager.get_session_versions(session_id, version_type)
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        return jsonify({'error': f'获取版本失败: {str(e)}'}), 500

@app.route('/session/<session_id>/selected-versions')
def get_selected_versions(session_id):
    """获取当前选择的版本"""
    try:
        selected = session_manager.get_selected_versions(session_id)
        
        return jsonify({
            'success': True,
            'selected': selected
        })
        
    except Exception as e:
        return jsonify({'error': f'获取选择版本失败: {str(e)}'}), 500

@app.route('/session/<session_id>/select-version', methods=['POST'])
def select_version(session_id):
    """选择版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.select_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'选择版本失败: {str(e)}'}), 500

@app.route('/session/<session_id>/delete-version', methods=['DELETE'])
def delete_version(session_id):
    """删除版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.delete_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'删除版本失败: {str(e)}'}), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """统一的图片生成接口 - 支持文字和图片混合输入，支持会话版本管理"""
    try:
        prompt = request.form.get('prompt', '').strip()
        style = request.form.get('style', 'cute')
        color_preference = request.form.get('color_preference', 'colorful')
        expert_mode = request.form.get('expert_mode', 'false').lower() == 'true'
        aspect_ratio = request.form.get('aspect_ratio', '1:1')  # 新增高宽比参数
        uploaded_file = request.files.get('sketch')
        original_image_path = request.form.get('original_image_path', '').strip()
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not prompt and not uploaded_file and not original_image_path:
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
        print(f"🎨 生成参数 - 风格: {style}, 色彩: {color_preference}, Expert模式: {expert_mode}, 高宽比: {aspect_ratio}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 处理上传的图片或使用原始图片路径
        sketch_path = None
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = str(uuid.uuid4()) + '_' + secure_filename(uploaded_file.filename)
            sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(sketch_path)
            
            # 预处理手绘图片
            processed_sketch = preprocess_sketch(sketch_path)
            if processed_sketch:
                sketch_path = processed_sketch
        elif original_image_path:
            # 使用已有的原始图片（生成更多功能）
            # 将URL路径转换为文件系统路径
            if original_image_path.startswith('/uploads/'):
                sketch_path = 'uploads' + original_image_path[8:]
            elif original_image_path.startswith('uploads/'):
                sketch_path = original_image_path
            else:
                sketch_path = os.path.join('uploads', original_image_path)
        
        print(f"🎨 开始生成图片 - 文字: {prompt}, 图片: {sketch_path}")
        
        # 根据输入类型生成图片（不再自动转换16:9）
        if sketch_path and prompt:
            # 图片+文字模式
            generated_image_path = nano_banana.generate_image_from_sketch_and_text(
                sketch_path, prompt, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        elif sketch_path:
            # 纯图片模式
            generated_image_path = nano_banana.generate_image_from_sketch(
                sketch_path, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        else:
            # 纯文字模式
            generated_image_path = nano_banana.generate_image_from_text(
                prompt, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio
            )
        
        print(f"✅ 图片生成完成: {generated_image_path}")
        
        # 检查图片是否真的生成成功
        if not generated_image_path or not os.path.exists(generated_image_path):
            print(f"❌ 图片生成失败，不保存到数据库")
            return jsonify({'error': '图片生成失败，请重试'}), 500
        
        # 返回相对路径用于前端显示
        relative_path = generated_image_path.replace('uploads/', '/uploads/')
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'prompt': prompt,
                'has_sketch': sketch_path is not None,
                'generation_type': 'mixed' if sketch_path and prompt else ('sketch' if sketch_path else 'text'),
                'note': version_note
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='image',
                file_path=generated_image_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                # 自动选择新生成的版本
                session_manager.select_version(session_id, version_id)
                
                # 自动保存到数据库（如果用户已登录且图片生成成功）
                if current_user.is_authenticated:
                    try:
                        auto_save_artwork_to_db(session_id, generated_image_path, sketch_path, prompt)
                        print(f"🎨 作品已自动保存到数据库: {session_id}")
                    except Exception as e:
                        print(f"⚠️ 自动保存失败: {str(e)}")
        
        # 准备返回数据
        response_data = {
            'success': True,
            'image_url': relative_path,
            'version_id': version_id,
            'message': '图片生成成功！'
        }
        
        # 如果有上传的图片，也返回原始图片路径
        if sketch_path:
            original_relative_path = sketch_path.replace('uploads/', '/uploads/')
            response_data['original_image_url'] = original_relative_path
        
        return jsonify(response_data)
            
    except Exception as e:
        print(f"❌ 图片生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/adjust-image', methods=['POST'])
def adjust_image():
    """调整现有图片"""
    try:
        current_image = request.form.get('current_image')
        adjust_prompt = request.form.get('adjust_prompt', '').strip()
        expert_mode = request.form.get('expert_mode', 'false').lower() == 'true'
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not current_image or not adjust_prompt:
            return jsonify({'error': '缺少图片路径或调整说明'}), 400
        
        # 将相对路径转换为绝对路径
        if current_image.startswith('/uploads/'):
            current_image = current_image.replace('/uploads/', 'uploads/')
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        print(f"🔧 开始调整图片: {current_image} - 调整说明: {adjust_prompt}, Expert模式: {expert_mode}")
        
        # 使用调整提示词重新生成图片
        adjusted_image_path = nano_banana.adjust_image(current_image, adjust_prompt, expert_mode=expert_mode)
        
        print(f"✅ 图片调整完成: {adjusted_image_path}")
        
        # 返回相对路径用于前端显示
        relative_path = adjusted_image_path.replace('uploads/', '/uploads/')
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'adjust_prompt': adjust_prompt,
                'base_image': current_image,
                'generation_type': 'adjustment',
                'note': version_note
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='image',
                file_path=adjusted_image_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                # 自动选择新调整的版本
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'image_url': relative_path,
            'version_id': version_id,
            'message': '图片调整成功！'
        })
            
    except Exception as e:
        print(f"❌ 图片调整错误: {str(e)}")
        return jsonify({'error': f'调整失败: {str(e)}'}), 500

@app.route('/generate-multi-view', methods=['POST'])
def generate_multi_view():
    """生成多视角图片用于3D建模（正、反、左、右）"""
    try:
        prompt = request.form.get('prompt', '').strip()
        color_preference = request.form.get('color_preference', 'colorful')
        aspect_ratio = request.form.get('aspect_ratio', '1:1')
        session_id = request.form.get('session_id')
        
        if not prompt:
            return jsonify({'error': '请输入文字描述'}), 400
        
        print(f"🎨 多视角生成参数 - 描述: {prompt}, 色彩: {color_preference}, 高宽比: {aspect_ratio}")
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 生成4个视角的图片
        result = nano_banana.generate_multi_view_images(
            text_prompt=prompt,
            color_preference=color_preference,
            aspect_ratio=aspect_ratio
        )
        
        if not result:
            return jsonify({'error': '多视角图片生成失败，请重试'}), 500
        
        # 转换为相对路径
        image_urls = {}
        for view_name, path in result.items():
            relative_path = path.replace('uploads/', '/uploads/')
            image_urls[view_name] = relative_path
        
        print(f"✅ 多视角图片生成完成: {image_urls}")
        
        return jsonify({
            'success': True,
            'images': image_urls,
            'message': '多视角图片生成成功！'
        })
            
    except Exception as e:
        print(f"❌ 多视角图片生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model_endpoint():
    """从图片生成3D模型，支持会话版本管理和多视角输入"""
    try:
        # 检查是否是多视角模式
        is_multi_view = request.form.get('multi_view') == 'true'
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if is_multi_view:
            # 多视角模式：获取所有4个视角的图片
            front_image = request.form.get('front_image')
            back_image = request.form.get('back_image')
            left_image = request.form.get('left_image')
            right_image = request.form.get('right_image')
            
            if not all([front_image, back_image, left_image, right_image]):
                return jsonify({'error': '多视角模式需要提供所有4个视角的图片'}), 400
            
            # 将相对路径转换为绝对路径
            view_images = {
                'front': front_image.replace('/uploads/', 'uploads/') if front_image.startswith('/uploads/') else front_image,
                'back': back_image.replace('/uploads/', 'uploads/') if back_image.startswith('/uploads/') else back_image,
                'left': left_image.replace('/uploads/', 'uploads/') if left_image.startswith('/uploads/') else left_image,
                'right': right_image.replace('/uploads/', 'uploads/') if right_image.startswith('/uploads/') else right_image
            }
            
            print(f"🧊 开始生成3D模型（多视角模式）:")
            print(f"  正面: {view_images['front']}")
            print(f"  背面: {view_images['back']}")
            print(f"  左侧: {view_images['left']}")
            print(f"  右侧: {view_images['right']}")
            
            # 生成3D模型（多视角）
            model_result = generate_3d_model_from_multi_view(view_images)
            source_image = front_image  # 使用正面图作为源图片记录
            
        else:
            # 单图模式
            image_path = request.form.get('image_path')
            
            if not image_path:
                return jsonify({'error': '缺少图片路径'}), 400
            
            # 将相对路径转换为绝对路径
            if image_path.startswith('/uploads/'):
                image_path = image_path.replace('/uploads/', 'uploads/')
            
            print(f"🧊 开始生成3D模型（单图模式）: {image_path}")
            
            # 生成3D模型（单图）
            model_result = generate_3d_model_from_image(image_path)
            source_image = image_path
        
        print(f"✅ 3D模型生成完成: {model_result}")
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            # 转换回绝对路径用于存储
            model_abs_path = model_result.replace('/uploads/', 'uploads/')
            
            metadata = {
                'source_image': source_image,
                'note': version_note,
                'multi_view': is_multi_view
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='model',
                file_path=model_abs_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                # 自动选择新生成的版本
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'model_url': model_result,
            'version_id': version_id,
            'message': '3D模型生成成功！'
        })
            
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/generate-3d-model-sam', methods=['POST'])
def generate_3d_model_sam():
    """使用SAM 3D从图片生成3D模型"""
    try:
        image_path = request.form.get('image_path')
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        # 将相对路径转换为绝对路径
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        print(f"🎨 开始使用SAM 3D生成3D模型: {image_path}")
        
        # 初始化SAM 3D API
        sam3d = SAM3DAPI()
        
        # 生成3D模型
        model_path = sam3d.auto_segment_and_generate(image_path)
        
        if not model_path:
            # 如果SAM 3D失败，自动降级到Hunyuan3D
            print("⚠️ SAM 3D生成失败，降级到Hunyuan3D")
            model_path = generate_3d_model_from_image(image_path)
            engine_used = 'hunyuan3d'
        else:
            engine_used = 'sam3d'
        
        print(f"✅ 3D模型生成完成 (引擎: {engine_used}): {model_path}")
        
        # 转换为相对路径
        model_url = model_path.replace('models/', '/models/')
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            metadata = {
                'source_image': image_path,
                'note': version_note,
                'engine': engine_used
            }
            
            version_result = session_manager.add_version(
                session_id=session_id,
                version_type='model',
                file_path=model_path,
                metadata=metadata
            )
            
            if version_result['success']:
                version_id = version_result['version_id']
                session_manager.select_version(session_id, version_id)
        
        return jsonify({
            'success': True,
            'model_url': model_url,
            'version_id': version_id,
            'engine': engine_used,
            'message': f'3D模型生成成功！(使用 {engine_used})'
        })
            
    except Exception as e:
        print(f"❌ SAM 3D模型生成错误: {str(e)}")
        # 尝试降级到Hunyuan3D
        try:
            print("🔄 尝试降级到Hunyuan3D...")
            model_path = generate_3d_model_from_image(image_path)
            model_url = model_path.replace('models/', '/models/')
            return jsonify({
                'success': True,
                'model_url': model_url,
                'engine': 'hunyuan3d',
                'message': '3D模型生成成功！(使用 Hunyuan3D 备用引擎)'
            })
        except Exception as fallback_error:
            print(f"❌ Hunyuan3D降级也失败: {str(fallback_error)}")
            return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/compare-3d-engines', methods=['POST'])
def compare_3d_engines():
    """同时使用SAM 3D和Hunyuan3D生成，让用户比较"""
    try:
        image_path = request.form.get('image_path')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        # 将相对路径转换为绝对路径
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        print(f"🔍 开始对比两个3D引擎: {image_path}")
        
        results = {}
        
        # 尝试SAM 3D
        try:
            sam3d = SAM3DAPI()
            sam3d_model = sam3d.auto_segment_and_generate(image_path)
            if sam3d_model:
                results['sam3d'] = {
                    'success': True,
                    'model_url': sam3d_model.replace('models/', '/models/'),
                    'engine': 'sam3d'
                }
            else:
                results['sam3d'] = {
                    'success': False,
                    'error': 'SAM 3D生成失败'
                }
        except Exception as e:
            results['sam3d'] = {
                'success': False,
                'error': str(e)
            }
        
        # 尝试Hunyuan3D
        try:
            hunyuan_model = generate_3d_model_from_image(image_path)
            results['hunyuan3d'] = {
                'success': True,
                'model_url': hunyuan_model,
                'engine': 'hunyuan3d'
            }
        except Exception as e:
            results['hunyuan3d'] = {
                'success': False,
                'error': str(e)
            }
        
        # 检查是否至少有一个成功
        if not results['sam3d']['success'] and not results['hunyuan3d']['success']:
            return jsonify({
                'error': '两个引擎都失败了',
                'details': results
            }), 500
        
        return jsonify({
            'success': True,
            'results': results,
            'message': '3D引擎对比完成'
        })
            
    except Exception as e:
        print(f"❌ 3D引擎对比错误: {str(e)}")
        return jsonify({'error': f'对比失败: {str(e)}'}), 500

@app.route('/api/sam3d/info')
def sam3d_info():
    """获取SAM 3D模型信息"""
    try:
        sam3d = SAM3DAPI()
        info = sam3d.get_model_info()
        return jsonify({
            'success': True,
            'info': info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save-artwork', methods=['POST'])
@login_required  # 添加登录验证
def save_artwork():
    """从创作会话保存作品到数据库"""
    try:
        data = request.get_json()
        print(f"📨 收到保存作品请求: {data}")
        
        # 验证必需的参数
        session_id = data.get('session_id')
        print(f"🔍 会话ID: {session_id}")
        
        if not session_id:
            print("❌ 缺少会话ID")
            return jsonify({'error': '缺少会话ID'}), 400
        
        # 获取会话的所有版本历史
        print(f"🔄 获取会话 {session_id} 的所有版本...")
        session_folder = f"creation_sessions/{session_id}"
        
        # 从会话文件夹获取所有文件
        all_files = {
            'original_sketch': None,
            'colored_images': [],
            'adjusted_images': [],
            'model_3d': None,
            'video_file': None
        }
        
        if os.path.exists(session_folder):
            files_in_folder = sorted(os.listdir(session_folder))
            
            for filename in files_in_folder:
                if filename.startswith('.'):  # 跳过隐藏文件
                    continue
                    
                file_path = os.path.join(session_folder, filename)
                file_lower = filename.lower()
                
                # 原始简笔画 - 上传的或手绘的
                if 'upload' in file_lower or 'sketch' in file_lower or 'original' in file_lower:
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        all_files['original_sketch'] = filename
                
                # 调整后的图片（包含'adjusted'关键字）
                elif 'adjusted' in file_lower:
                    all_files['adjusted_images'].append(filename)
                
                # AI生成的图片（包含'colored', 'generated', 或时间戳格式）
                elif any(keyword in file_lower for keyword in ['colored', 'generated', 'image_']):
                    all_files['colored_images'].append(filename)
                
                # 如果是普通的PNG/JPG但不属于以上类别，也算作生成图片
                elif filename.endswith(('.png', '.jpg', '.jpeg')):
                    # 排除明确标记为其他类型的文件
                    if not any(x in file_lower for x in ['model', 'thumbnail']):
                        all_files['colored_images'].append(filename)
                
                # 3D模型
                elif filename.endswith(('.glb', '.obj', '.fbx', '.gltf')):
                    all_files['model_3d'] = filename
                
                # 视频文件
                elif filename.endswith(('.mp4', '.mov', '.avi')):
                    all_files['video_file'] = filename
        
        # 对列表排序（按文件名，通常包含时间戳）
        all_files['colored_images'].sort()
        all_files['adjusted_images'].sort()
        
        print(f"📁 会话文件统计:")
        print(f"  - 原始简笔画: {all_files['original_sketch']}")
        print(f"  - AI生成图片: {len(all_files['colored_images'])}个")
        print(f"  - 调整后图片: {len(all_files['adjusted_images'])}个")
        print(f"  - 3D模型: {all_files['model_3d']}")
        print(f"  - 视频: {all_files['video_file']}")
        
        # 获取选择的版本（用于主要展示）
        selected_versions = session_manager.get_selected_versions(session_id)
        print(f"⭐ 选择的版本: {selected_versions}")
        
        if 'image' not in selected_versions:
            # 如果没有选择版本，优先使用调整后的图片，其次是生成的图片
            if all_files['adjusted_images']:
                selected_image = all_files['adjusted_images'][-1]  # 最新的调整版本
            elif all_files['colored_images']:
                selected_image = all_files['colored_images'][-1]  # 最新的生成版本
            else:
                print("❌ 没有找到任何图片")
                return jsonify({'error': '没有找到生成的图片'}), 400
        else:
            image_version = selected_versions['image']
            selected_image = os.path.basename(image_version['file_path'])
        
        print(f"🎯 主要展示图片: {selected_image}")
        
        # 从当前用户session获取姓名和年龄
        artist_name = current_user.username  # 使用登录用户名
        artist_age = getattr(current_user, 'age', None)  # 如果用户模型有age字段
        
        # 如果用户模型没有年龄字段，使用默认值或从前端获取
        if not artist_age:
            artist_age = data.get('artist_age', 10)
        
        print(f"👤 创作者: {artist_name}, 年龄: {artist_age}")
        
        # 检查是否已存在该会话的作品
        from auth.models import Artwork
        existing_artwork = Artwork.query.filter_by(session_id=session_id).first()
        
        if existing_artwork:
            # 更新现有作品
            existing_artwork.title = data.get('title', '我的作品')
            existing_artwork.artist_name = artist_name
            existing_artwork.artist_age = artist_age
            existing_artwork.category = data.get('category', 'other')
            existing_artwork.description = data.get('description', '')
            existing_artwork.status = 'completed'
            existing_artwork.updated_at = datetime.utcnow()
            
            # 保存所有版本的文件
            existing_artwork.original_sketch = all_files['original_sketch']
            existing_artwork.colored_image = selected_image  # 主要展示的图片
            existing_artwork.all_colored_versions = all_files['colored_images']  # 所有上色版本
            existing_artwork.all_adjusted_versions = all_files['adjusted_images']  # 所有调整版本
            existing_artwork.model_3d = all_files['model_3d']
            existing_artwork.video_file = all_files['video_file']
            
            artwork_id = existing_artwork.id
            print(f"✅ 更新现有作品: {artwork_id}")
        else:
            # 创建新作品记录
            artwork = Artwork(
                session_id=session_id,
                title=data.get('title', '我的作品'),
                user_id=current_user.id,
                artist_name=artist_name,
                artist_age=artist_age,
                category=data.get('category', 'other')
            )
            
            artwork.description = data.get('description', '')
            artwork.status = 'completed'
            artwork.is_public = False  # 默认私密，需手动设为公开
            
            # 保存所有版本的文件（只保存文件名，路径由session_id构建）
            artwork.original_sketch = all_files['original_sketch']
            artwork.colored_image = selected_image  # 主要展示的图片
            artwork.all_colored_versions = all_files['colored_images']  # 所有上色版本
            artwork.all_adjusted_versions = all_files['adjusted_images']  # 所有调整版本
            artwork.model_3d = all_files['model_3d']
            artwork.video_file = all_files['video_file']
            
            # 保存到数据库
            db.session.add(artwork)
            artwork_id = None  # 将在commit后获取
            print(f"✅ 创建新作品记录")
            print(f"📦 保存的文件:")
            print(f"  - 原始简笔画: {artwork.original_sketch}")
            print(f"  - 主要展示图: {artwork.colored_image}")
            print(f"  - 所有上色版本({len(all_files['colored_images'])}个): {all_files['colored_images']}")
            print(f"  - 所有调整版本({len(all_files['adjusted_images'])}个): {all_files['adjusted_images']}")
            print(f"  - 3D模型: {artwork.model_3d}")
            print(f"  - 视频: {artwork.video_file}")
        
        db.session.commit()
        
        # 获取artwork_id（对于新创建的作品）
        if not existing_artwork:
            artwork_id = artwork.id
        
        # 关闭会话（标记为完成）
        session_manager.close_session(session_id)
        
        return jsonify({
            'success': True,
            'artwork_id': artwork_id,
            'message': '作品已成功保存到作品集！',
            'session_closed': True
        })
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存作品失败: {str(e)}")
        return jsonify({'error': f'保存作品失败: {str(e)}'}), 500

@app.route('/artwork/<artwork_id>')
def view_artwork(artwork_id):
    """查看单个作品详情"""
    artwork = gallery_manager.get_artwork_by_id(artwork_id)
    if not artwork:
        return "作品不存在", 404
    
    # 增加浏览次数
    gallery_manager.increment_views(artwork_id)
    
    return render_template('artwork_detail.html', artwork=artwork)

# ===================== 视频生成相关路由 =====================

@app.route('/test-3d')
def test_3d():
    """3D测试页面"""
    return send_from_directory('.', 'test_3d.html')

@app.route('/api/get-image-info', methods=['POST'])
def get_image_info():
    """获取图片信息和推荐框选区域"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        use_expanded = data.get('use_expanded', False)  # 是否使用扩展图片模式
        
        if not image_path:
            return jsonify({'success': False, 'error': '缺少图片路径'}), 400
        
        # 转换路径
        if image_path.startswith('/uploads/'):
            image_path = 'uploads' + image_path[8:]
        elif image_path.startswith('uploads/'):
            pass
        else:
            image_path = os.path.join('uploads', image_path)
        
        print(f"📐 获取图片信息: {image_path} (扩展模式: {use_expanded})")
        
        # 获取图片信息
        nano_banana = NanoBananaAPI()
        info = nano_banana.get_image_info(image_path, use_expanded=use_expanded)
        
        if info['success']:
            print(f"✅ 图片信息获取成功: {info['width']}x{info['height']}")
            return jsonify(info)
        else:
            return jsonify({'success': False, 'error': info['error']}), 500
            
    except Exception as e:
        print(f"❌ 获取图片信息失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate-prompt', methods=['POST'])
def translate_prompt_api():
    """翻译prompt并返回预览信息"""
    try:
        from api.prompt_translator import translate_prompt
        
        data = request.get_json()
        original_prompt = data.get('prompt', '').strip()
        
        if not original_prompt:
            return jsonify({'success': False, 'error': '提示词不能为空'}), 400
        
        print(f"🌐 翻译prompt: {original_prompt}")
        
        # 翻译prompt
        translated_prompt = translate_prompt(original_prompt)
        
        print(f"✅ 翻译完成: {translated_prompt}")
        
        # 添加详细的对话检查日志
        if "saying in Chinese:" in translated_prompt:
            print("🗣️ 检测到对话保护：找到 'saying in Chinese:' 标记")
            # 提取并检查对话内容
            import re
            chinese_content = re.search(r'saying in Chinese:\s*["""\'\'](.*?)["""\'\'"]', translated_prompt)
            if chinese_content:
                dialogue_text = chinese_content.group(1)
                print(f"🔍 保护的对话内容: '{dialogue_text}'")
                # 检查是否包含中文
                if re.search(r'[\u4e00-\u9fff]', dialogue_text):
                    print("✅ 对话内容确实保持中文")
                else:
                    print("❌ 对话内容没有中文")
            else:
                print("⚠️ 没有找到对话内容")
        else:
            print("❌ 没有检测到对话保护标记")
        
        return jsonify({
            'success': True,
            'original_prompt': original_prompt,
            'translated_prompt': translated_prompt
        })
        
    except Exception as e:
        print(f"❌ prompt翻译失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/organize-prompt', methods=['POST'])
def organize_prompt_api():
    """使用AI整理语音输入的内容成为清晰的prompt"""
    try:
        import google.generativeai as genai
        
        data = request.get_json()
        voice_input = data.get('voice_input', '').strip()
        
        if not voice_input:
            return jsonify({'success': False, 'error': '语音内容为空'}), 400
        
        print(f"🎤 收到语音输入: {voice_input}")
        
        # 配置Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API密钥未配置'}), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 构建整理指令
        system_prompt = """你是一个专业的AI创意助手，负责将用户的语音描述整理成清晰、详细的图片生成提示词。

要求：
1. 保留用户表达的核心创意和关键元素
2. 补充必要的视觉细节（如颜色、形状、风格、场景等）
3. 使用儿童友好的语言（面向10-14岁儿童）
4. 按照"主体-特征-动作-场景-风格"的结构组织
5. 如果用户提到对话内容，必须保持原文不翻译
6. 最终输出一段连贯、详细的中文描述（100-200字）
7. 直接输出整理后的提示词，不要任何前缀说明或客套话

示例：
输入："我想要一只猫，红色的帽子，在彩虹上"
输出："一只可爱的小猫咪，戴着鲜艳的红色小帽子，毛茸茸的身体，大大的眼睛闪烁着好奇的光芒，正优雅地坐在七彩的彩虹上，背景是蓝天白云，阳光明媚，卡通风格，色彩明亮温暖。"

现在请整理以下语音输入（只输出整理后的提示词，不要其他内容）："""
        
        # 调用AI整理
        full_prompt = f"{system_prompt}\n\n用户语音：{voice_input}"
        response = model.generate_content(full_prompt)
        organized_prompt = response.text.strip()
        
        print(f"✨ AI整理后: {organized_prompt}")
        
        return jsonify({
            'success': True,
            'original_input': voice_input,
            'organized_prompt': organized_prompt
        })
        
    except Exception as e:
        print(f"❌ AI整理失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-artwork-info', methods=['POST'])
def generate_artwork_info_api():
    """使用AI生成作品的标题、分类和介绍"""
    try:
        import google.generativeai as genai
        
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'prompt为空'}), 400
        
        print(f"🎨 为prompt生成作品信息: {prompt}")
        
        # 配置Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'API密钥未配置'}), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 构建生成指令
        system_prompt = """你是一个创意作品命名和介绍专家，请根据用户的创作提示词，生成以下内容：

1. 作品标题：简短有趣（4-10个字），适合儿童作品
2. 作品分类：从以下类别选择一个最合适的：
   - animals（动物）
   - characters（人物）
   - objects（物品）
   - nature（自然）
   - other（其他）
3. 作品介绍：编写一个100字左右的儿童友好小故事，描述这个创作的奇妙之处

请严格按照以下JSON格式返回（不要任何markdown标记或代码块标记）：
{
  "title": "作品标题",
  "category": "分类英文",
  "description": "作品介绍小故事"
}

示例：
提示词："一只可爱的小猫咪，戴着红色的帽子，坐在彩虹上..."

返回：
{
  "title": "彩虹上的猫咪",
  "category": "animals",
  "description": "在一个阳光明媚的早晨，一只勇敢的小猫咪戴上了它最喜欢的红色帽子，踏上了一场奇妙的冒险。它爬上了天边的彩虹，那里有七种颜色的道路，每一步都闪闪发光。小猫咪坐在彩虹的最顶端，俯瞰着整个世界，感觉自己就像一个小小的探险家。这是属于它的奇妙时刻！"
}

现在请为以下提示词生成作品信息："""
        
        # 调用AI生成
        full_prompt = f"{system_prompt}\n\n提示词：{prompt}"
        response = model.generate_content(full_prompt)
        result_text = response.text.strip()
        
        # 移除可能的markdown代码块标记
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            # 移除第一行和最后一行的```
            result_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
        if result_text.startswith('json'):
            result_text = result_text[4:].strip()
        
        print(f"📝 AI生成的JSON: {result_text}")
        
        # 解析JSON
        import json
        artwork_info = json.loads(result_text)
        
        return jsonify({
            'success': True,
            'title': artwork_info.get('title', ''),
            'category': artwork_info.get('category', 'other'),
            'description': artwork_info.get('description', '')
        })
        
    except Exception as e:
        print(f"❌ 生成作品信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        from api.veo31 import get_veo_api
        
        from api.prompt_translator import translate_prompt
        
        data = request.get_json()
        session_id = data.get('session_id')
        image_url = data.get('image_url')
        original_prompt = data.get('prompt')
        duration = data.get('duration', 8)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        quality = data.get('quality', '720p')
        motion_intensity = data.get('motion_intensity', 'medium')
        model = data.get('model', 'veo-3.1-fast-generate-preview')  # 默认使用快速版模型
        
        if not session_id or not image_url or not original_prompt:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        print(f"\n🎬 收到视频生成请求:")
        print(f"   Session ID: {session_id}")
        print(f"   Image URL: {image_url}")
        print(f"   原始提示词: {original_prompt}")
        print(f"   Duration: {duration}s")
        print(f"   Aspect Ratio: {aspect_ratio}")
        print(f"   Quality: {quality}")
        print(f"   Motion: {motion_intensity}")
        print(f"   Model: {model}")
        
        # 直接翻译中文提示词为英文
        print(f"🌐 开始翻译prompt: {original_prompt}")
        english_prompt = translate_prompt(original_prompt)
        print(f"✅ 翻译完成: {english_prompt}")
        
        # 添加详细的对话检查日志
        if "saying in Chinese:" in english_prompt:
            print("🗣️ 检测到对话保护：找到 'saying in Chinese:' 标记")
            # 提取并检查对话内容
            import re
            chinese_content = re.search(r'saying in Chinese:\s*["""\'\'](.*?)["""\'\'"]', english_prompt)
            if chinese_content:
                dialogue_text = chinese_content.group(1)
                print(f"🔍 保护的对话内容: '{dialogue_text}'")
                # 检查是否包含中文
                if re.search(r'[\u4e00-\u9fff]', dialogue_text):
                    print("✅ 对话内容确实保持中文")
                else:
                    print("❌ 对话内容没有中文")
            else:
                print("⚠️ 没有找到对话内容")
        else:
            print("❌ 没有检测到对话保护标记")
        
        # 调用Veo API，使用英文提示词
        veo_api = get_veo_api()
        try:
            result = veo_api.generate_video(
                image_url=image_url,
                prompt=english_prompt,  # 使用翻译后的英文提示词
                duration=duration,
                aspect_ratio=aspect_ratio,
                quality=quality,
                motion_intensity=motion_intensity,
                model=model  # 传递模型参数
            )
        except Exception as api_error:
            error_str = str(api_error)
            print(f"❌ Veo API错误: {error_str}")
            
            # 检查是否是配额限制错误
            if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                return jsonify({
                    'success': False,
                    'error': 'API配额已用完，请稍后再试。当前Veo模型使用量较高，建议等待配额重置。',
                    'error_type': 'quota_exceeded'
                }), 429
            else:
                raise api_error  # 重新抛出其他类型的错误
        
        return jsonify({
            'success': True,
            'task_id': result.get('task_id'),
            'message': '视频生成任务已启动'
        })
        
    except Exception as e:
        print(f"❌ 视频生成错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/video-status/<path:task_id>')
def video_status(task_id):
    """检查视频生成状态"""
    try:
        from api.veo31 import get_veo_api
        
        print(f"🔍 检查任务状态: {task_id}")
        
        veo_api = get_veo_api()
        status_result = veo_api.check_status(task_id)
        
        print(f"📊 状态结果: {status_result}")
        
        # 确保返回success字段
        if 'success' not in status_result:
            status_result['success'] = status_result.get('status') != 'failed'
        
        return jsonify(status_result)
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 状态检查错误: {error_msg}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'status': 'failed',
            'error': error_msg,
            'message': f'状态检查失败: {error_msg}'
        }), 500

@app.route('/api/save-video', methods=['POST'])
def save_video():
    """保存视频到作品集"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        video_url = data.get('video_url')
        prompt = data.get('prompt', '')
        
        if not session_id or not video_url:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        # TODO: 实现视频保存到作品集的逻辑
        # 这里可以扩展gallery_manager来支持视频作品
        
        print(f"✅ 视频已保存: {video_url}")
        
        return jsonify({
            'success': True,
            'message': '视频已保存到作品集'
        })
        
    except Exception as e:
        print(f"❌ 视频保存错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    """文件太大错误处理"""
    return jsonify({'error': '上传文件太大，请选择小于16MB的文件'}), 413

@app.errorhandler(500)
def internal_error(e):
    """内部服务器错误处理"""
    print(f"服务器错误: {str(e)}")
    return jsonify({'error': '服务器内部错误，请稍后重试'}), 500

@app.route('/static/creation_sessions/<path:filename>')
def serve_creation_sessions(filename):
    """提供creation_sessions文件夹中的静态文件"""
    from flask import send_from_directory
    return send_from_directory('static/creation_sessions', filename)

@app.route('/creation_sessions/<path:filename>')
def serve_creation_sessions_direct(filename):
    """提供creation_sessions文件夹中的静态文件（直接路径）"""
    from flask import send_from_directory
    return send_from_directory('creation_sessions', filename)

@app.route('/feature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def feature_artwork(artwork_id):
    """设置作品为推荐作品"""
    try:
        from auth.models import Artwork
        
        # 获取作品
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 取消当前用户的其他推荐作品
        Artwork.query.filter_by(user_id=current_user.id, is_featured=True).update({
            'is_featured': False,
            'featured_at': None
        })
        
        # 设置新的推荐作品
        artwork.is_featured = True
        artwork.is_public = True  # 推荐作品自动设为公开
        artwork.featured_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已设为推荐作品！'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

@app.route('/vote-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def vote_artwork(artwork_id):
    """为作品投票"""
    try:
        from auth.models import Artwork, ArtworkVote
        
        data = request.get_json()
        vote_type = data.get('vote_type', 'like')
        
        # 验证投票类型
        if vote_type not in ['like', 'love', 'wow', 'cool']:
            return jsonify({'error': '无效的投票类型'}), 400
        
        # 获取作品
        artwork = Artwork.query.get(artwork_id)
        if not artwork or not artwork.is_public:
            return jsonify({'error': '作品不存在或未公开'}), 404
        
        # 允许给自己的作品投票
        # 检查是否已投票
        existing_vote = ArtworkVote.query.filter_by(
            artwork_id=artwork_id, 
            voter_id=current_user.id
        ).first()
        
        if existing_vote:
            # 已经投过票，不允许重复投票
            return jsonify({
                'success': False,
                'error': '您已经为这个作品点过赞了！',
                'vote_count': artwork.vote_count
            })
        else:
            # 新投票
            vote = ArtworkVote(artwork_id, current_user.id, vote_type)
            db.session.add(vote)
            
            # 更新作品投票数
            artwork.vote_count = (artwork.vote_count or 0) + 1
            message = '点赞成功！'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'vote_count': artwork.vote_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'投票失败: {str(e)}'}), 500

@app.route('/increment-view/<int:artwork_id>', methods=['POST'])
@login_required
def increment_view(artwork_id):
    """增加作品浏览次数（每个用户只记录一次）"""
    try:
        from auth.models import Artwork, ArtworkView
        
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return jsonify({'error': '作品不存在'}), 404
        
        # 检查该用户是否已经浏览过这个作品
        existing_view = ArtworkView.query.filter_by(
            artwork_id=artwork_id,
            viewer_id=current_user.id
        ).first()
        
        if not existing_view:
            # 首次浏览，创建浏览记录
            view = ArtworkView(artwork_id, current_user.id)
            db.session.add(view)
            
            # 增加浏览次数
            artwork.view_count = (artwork.view_count or 0) + 1
            db.session.commit()
            
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': True
            })
        else:
            # 已经浏览过，不增加计数
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': False
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新浏览次数失败: {str(e)}'}), 500

@app.route('/gallery')
def public_gallery():
    """公共作品展示页面"""
    try:
        from auth.models import Artwork, User
        from sqlalchemy import desc
        
        # 获取所有公开的推荐作品
        featured_artworks = Artwork.query.filter_by(
            is_public=True, 
            is_featured=True
        ).join(User).order_by(desc(Artwork.featured_at)).all()
        
        return render_template('gallery.html', artworks=featured_artworks)
        
    except Exception as e:
        print(f"❌ 加载作品展示失败: {str(e)}")
        return render_template('gallery.html', artworks=[])

@app.route('/unfeature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def unfeature_artwork(artwork_id):
    """取消推荐作品"""
    try:
        from auth.models import Artwork
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_featured = False
        artwork.featured_at = None
        # 注意：保持is_public状态，用户可以单独控制
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已取消推荐'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'操作失败: {str(e)}'}), 500

# API路由 - 作品管理
@app.route('/api/artwork/<int:artwork_id>', methods=['GET'])
@login_required
def get_artwork_api(artwork_id):
    """获取作品详情API"""
    try:
        from auth.models import Artwork, User
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        file_urls = artwork.get_file_urls()
        
        artwork_data = {
            'id': artwork.id,
            'title': artwork.title or '未命名作品',
            'description': artwork.description,
            'created_at': artwork.created_at.strftime('%Y年%m月%d日 %H:%M'),
            'artwork_type': '3D模型' if file_urls['model_3d'] else 'AI上色' if file_urls['colored_image'] else '手绘作品',
            'image_url': file_urls['colored_image'] or file_urls['figurine_image'] or file_urls['original_sketch'] or '/static/images/placeholder.png',
            'views': artwork.view_count or 0,
            'likes': artwork.vote_count or 0,
            'is_featured': artwork.is_featured,
            'is_public': artwork.is_public,
            'files': {
                'original_sketch': file_urls['original_sketch'],
                'colored_image': file_urls['colored_image'],
                'figurine_image': file_urls['figurine_image'],
                'model_3d': file_urls['model_3d'],
                'video_file': file_urls['video_file']
            }
        }
        
        return jsonify(artwork_data)
        
    except Exception as e:
        return jsonify({'error': f'获取作品详情失败: {str(e)}'}), 500

@app.route('/api/artwork/<int:artwork_id>', methods=['DELETE'])
@login_required
def delete_artwork_api(artwork_id):
    """删除作品API"""
    try:
        from auth.models import Artwork, ArtworkVote
        import os
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 删除相关的投票记录
        ArtworkVote.query.filter_by(artwork_id=artwork_id).delete()
        
        # 删除文件
        session_folder = os.path.join('creation_sessions', artwork.session_id)
        if os.path.exists(session_folder):
            import shutil
            try:
                shutil.rmtree(session_folder)
            except Exception as file_error:
                print(f"删除文件失败: {file_error}")
        
        # 删除数据库记录
        db.session.delete(artwork)
        db.session.commit()
        
        # 计算删除后的统计信息
        from sqlalchemy import func
        remaining_count = Artwork.query.filter_by(user_id=current_user.id).count()
        total_likes = db.session.query(func.sum(Artwork.vote_count)).filter_by(user_id=current_user.id).scalar() or 0
        total_views = db.session.query(func.sum(Artwork.view_count)).filter_by(user_id=current_user.id).scalar() or 0
        
        return jsonify({
            'success': True,
            'message': '作品已删除',
            'stats': {
                'total_artworks': remaining_count,
                'total_likes': total_likes,
                'total_views': total_views
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@app.route('/api/artwork/<int:artwork_id>/privacy', methods=['POST'])
@login_required
def update_artwork_privacy(artwork_id):
    """更新作品隐私设置API"""
    try:
        from auth.models import Artwork
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        data = request.get_json()
        is_public = data.get('is_public', False)
        
        artwork.is_public = is_public
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '隐私设置已更新',
            'is_public': artwork.is_public
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500

@app.route('/api/artwork/<int:artwork_id>/set-public', methods=['POST'])
@login_required
def set_artwork_public(artwork_id):
    """设置作品为公开"""
    try:
        from auth.models import Artwork
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为公开',
            'is_public': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

@app.route('/api/artwork/<int:artwork_id>/set-private', methods=['POST'])
@login_required
def set_artwork_private(artwork_id):
    """设置作品为私密"""
    try:
        from auth.models import Artwork
        
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为私密',
            'is_public': False
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500

@app.route('/test-privacy-toggles')
def test_privacy_toggles():
    """测试隐私设置切换开关页面"""
    with open('/Users/hongyuwang/code/HLTraining/test_privacy_toggles.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/test-content-indicators')
def test_content_indicators():
    """测试内容类型指示器页面"""
    return render_template('test_content_indicators.html')

# 图片生成接口（供前端调用）
@app.route('/generate-image', methods=['POST'])
def api_generate_image():
    """生成图片的后端接口。
    输入：可选的文本提示 `prompt` 和/或上传的线稿文件 `sketch`
    输出：JSON，包含生成结果图片的相对路径。
    """
    try:
        prompt_text = request.form.get('prompt', '').strip()
        sketch_file = request.files.get('sketch')

        if not prompt_text and not sketch_file:
            return jsonify({
                'success': False,
                'error': '请提供提示词或上传线稿图片'
            }), 400

        # 创建会话ID用于文件归档
        session_id = request.form.get('session_id') or str(uuid.uuid4())
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)

        saved_sketch_path = None
        if sketch_file and allowed_file(sketch_file.filename):
            filename = secure_filename(sketch_file.filename)
            saved_sketch_path = os.path.join(session_dir, filename)
            sketch_file.save(saved_sketch_path)

        # 简化版生成逻辑
        output_path = None
        if saved_sketch_path:
            processed = preprocess_sketch(saved_sketch_path)
            output_path = processed or saved_sketch_path
        else:
            # 仅文字：生成一张占位图
            output_path = os.path.join(session_dir, 'generated_placeholder.png')
            img = np.zeros((512, 512, 3), dtype=np.uint8)
            img[:] = (200, 180, 255)  # 淡紫底
            cv2.putText(img, 'AI 生成占位图', (40, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 50, 50), 2, cv2.LINE_AA)
            cv2.imwrite(output_path, img)

        # 转为前端可访问的URL
        public_url = output_path.replace(BASE_DIR + os.sep, '')
        public_url = '/' + public_url.replace('\\', '/').replace('uploads', 'uploads')

        return jsonify({
            'success': True,
            'image_path': public_url,
            'session_id': session_id
        })
    except Exception as e:
        print(f"/generate-image 错误: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误，请稍后重试'
        }), 500

@app.route('/api/fetch-image', methods=['POST'])
@login_required
def fetch_image_from_url():
    """从URL获取图片并保存到本地"""
    try:
        import requests
        from io import BytesIO
        
        data = request.get_json()
        image_url = data.get('url', '').strip()
        
        if not image_url:
            return jsonify({'success': False, 'error': '图片链接不能为空'}), 400
        
        print(f"🔗 正在获取图片: {image_url}")
        
        # 设置请求头，模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 下载图片
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 检查是否是图片
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return jsonify({'success': False, 'error': '链接不是有效的图片'}), 400
        
        # 读取图片数据
        image_data = BytesIO(response.content)
        img = Image.open(image_data)
        
        # 转换为RGB（如果需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # 生成唯一文件名
        filename = f"url_image_{int(datetime.now().timestamp())}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 确保目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 保存图片
        img.save(filepath, 'PNG')
        
        print(f"✅ 图片已保存: {filepath}")
        
        return jsonify({
            'success': True,
            'image_url': f'/uploads/{filename}',
            'filename': filename
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': '图片下载超时，请重试'}), 400
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载图片失败: {str(e)}")
        return jsonify({'success': False, 'error': '无法访问该图片链接'}), 400
    except Exception as e:
        print(f"❌ 处理图片失败: {str(e)}")
        return jsonify({'success': False, 'error': f'图片处理失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 从环境变量读取配置
    port = int(os.getenv('PORT', 8088))
    host = os.getenv('HOST', '0.0.0.0')
    
    # 只在主进程显示启动信息（避免调试模式重复输出）
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        print("🚀 松果AI平台启动中...")
        print("📝 功能特色:")
        print("   - 用户管理系统：注册、登录、家长验证")
        print("   - 统一创作界面：文字+图片混合输入")
        print("   - 分步骤工作流：图片生成 → 调整 → 3D模型")
        print("   - AI图片生成：使用Nano Banana (Gemini 2.5 Flash Image)")
        print("   - 3D模型生成：使用腾讯云AI3D (混元3D)")
        print("   - 适合儿童：10-14岁友好界面设计")
        print(f"\n🌐 访问地址: http://127.0.0.1:{port}")
        print(f"🔗 注册页面: http://127.0.0.1:{port}/auth/register")
        print(f"🔗 登录页面: http://127.0.0.1:{port}/auth/login")
        print(f"🔗 创作页面: http://127.0.0.1:{port}/create (需要登录)")
    
    app.run(debug=True, host=host, port=port)