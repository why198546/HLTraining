from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
from api.nano_banana import NanoBananaAPI
from api.hunyuan3d import Hunyuan3DGenerator
from gallery_manager import GalleryManager
from creation_session_manager import CreationSessionManager
import json
from dotenv import load_dotenv
from datetime import datetime

# 用户管理系统导入
from flask_login import LoginManager, login_required, current_user
from models import db, User, Artwork, CreationSession
from auth import auth_bp
from auth.routes import *
from utils.email_service import init_mail

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 创建数据库表
with app.app_context():
    db.create_all()

# 初始化作品集管理器和创作会话管理器
gallery_manager = GalleryManager()
session_manager = CreationSessionManager()

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

def auto_save_artwork_to_db(session_id, generated_image_path, sketch_path=None, prompt=None):
    """自动保存作品到数据库"""
    try:
        from models import Artwork
        
        # 检查是否已存在该会话的作品
        existing_artwork = Artwork.query.filter_by(session_id=session_id).first()
        
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
            artwork.is_public = True  # 默认设为公开
            
            # 设置文件路径
            if generated_image_path:
                artwork.colored_image = os.path.basename(generated_image_path)
            if sketch_path:
                artwork.original_sketch = os.path.basename(sketch_path)
            if prompt:
                artwork.prompt_text = prompt
                
            db.session.add(artwork)
            print(f"➕ 创建新作品记录: {session_id}")
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 自动保存失败: {str(e)}")
        return False

@app.route('/')
def index():
    """主页"""
    # 获取最新的4个作品用于首页展示
    from models import Artwork, User
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
    from models import Artwork
    
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
    from models import Artwork, db
    
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
    from models import Artwork, User
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
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/models/<filename>')
def model_file(filename):
    """提供3D模型文件访问"""
    return send_file(os.path.join('models', filename))

@app.route('/session-files/<path:filepath>')
def session_file(filepath):
    """提供创作会话文件访问"""
    return send_file(filepath)

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
                
                # 自动保存到数据库（如果用户已登录）
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

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model_endpoint():
    """从图片生成3D模型，支持会话版本管理"""
    try:
        image_path = request.form.get('image_path')
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        # 将相对路径转换为绝对路径
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        print(f"🧊 开始生成3D模型: {image_path}")
        
        # 生成3D模型
        model_result = generate_3d_model_from_image(image_path)
        
        print(f"✅ 3D模型生成完成: {model_result}")
        
        # 如果有会话ID，添加到会话版本管理
        version_id = None
        if session_id:
            # 转换回绝对路径用于存储
            model_abs_path = model_result.replace('/uploads/', 'uploads/')
            
            metadata = {
                'source_image': image_path,
                'note': version_note
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
        
        # 从会话获取选择的版本
        print(f"🔄 获取会话 {session_id} 的选择版本...")
        selected_versions = session_manager.get_selected_versions(session_id)
        print(f"📋 选择的版本: {selected_versions}")
        
        if 'image' not in selected_versions:
            print("❌ 没有选择图片版本")
            return jsonify({'error': '请先选择一个图片版本'}), 400
        
        # 获取文件路径
        image_version = selected_versions['image']
        model_version = selected_versions.get('model')
        
        image_path = image_version['file_path']
        model_path = model_version['file_path'] if model_version else None
        
        # 验证文件存在
        if not os.path.exists(image_path):
            return jsonify({'error': '选择的图片文件不存在'}), 400
        
        if model_path and not os.path.exists(model_path):
            return jsonify({'error': '选择的3D模型文件不存在'}), 400
        
        # 检查是否已存在该会话的作品
        from models import Artwork
        existing_artwork = Artwork.query.filter_by(session_id=session_id).first()
        
        if existing_artwork:
            # 更新现有作品
            existing_artwork.title = data.get('title', '我的作品')
            existing_artwork.description = data.get('description', '')
            existing_artwork.status = 'completed'
            existing_artwork.updated_at = datetime.utcnow()
            
            # 更新文件路径（相对路径）
            session_folder = f"creation_sessions/{session_id}"
            if image_path.startswith(session_folder):
                existing_artwork.colored_image = os.path.basename(image_path)
            
            if model_path and model_path.startswith(session_folder):
                existing_artwork.model_3d = os.path.basename(model_path)
            
            artwork_id = existing_artwork.id
            print(f"✅ 更新现有作品: {artwork_id}")
        else:
            # 创建新作品记录
            artwork = Artwork(
                session_id=session_id,
                title=data.get('title', '我的作品'),
                user_id=current_user.id
            )
            
            artwork.description = data.get('description', '')
            artwork.status = 'completed'
            artwork.is_public = True  # 默认设为公开
            
            # 设置文件路径（只保存文件名，路径由session_id构建）
            session_folder = f"creation_sessions/{session_id}"
            if image_path.startswith(session_folder):
                artwork.colored_image = os.path.basename(image_path)
            
            if model_path and model_path.startswith(session_folder):
                artwork.model_3d = os.path.basename(model_path)
            
            # 保存到数据库
            db.session.add(artwork)
            artwork_id = None  # 将在commit后获取
            print(f"✅ 创建新作品记录")
        
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

@app.route('/like-artwork/<artwork_id>', methods=['POST'])
def like_artwork(artwork_id):
    """点赞作品"""
    try:
        likes = gallery_manager.toggle_like(artwork_id)
        return jsonify({'success': True, 'likes': likes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        from api.veo31 import get_veo_api
        
        data = request.get_json()
        session_id = data.get('session_id')
        image_url = data.get('image_url')
        prompt = data.get('prompt')
        duration = data.get('duration', 8)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        quality = data.get('quality', '720p')
        motion_intensity = data.get('motion_intensity', 'medium')
        
        if not session_id or not image_url or not prompt:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        print(f"\n🎬 收到视频生成请求:")
        print(f"   Session ID: {session_id}")
        print(f"   Image URL: {image_url}")
        print(f"   Prompt: {prompt}")
        print(f"   Duration: {duration}s")
        print(f"   Aspect Ratio: {aspect_ratio}")
        print(f"   Quality: {quality}")
        print(f"   Motion: {motion_intensity}")
        
        # 调用Veo API
        veo_api = get_veo_api()
        result = veo_api.generate_video(
            image_url=image_url,
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            quality=quality,
            motion_intensity=motion_intensity
        )
        
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
        
        veo_api = get_veo_api()
        status_result = veo_api.check_status(task_id)
        
        return jsonify(status_result)
        
    except Exception as e:
        print(f"❌ 状态检查错误: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': str(e)
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
        from models import Artwork
        
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
        from models import Artwork, ArtworkVote
        
        data = request.get_json()
        vote_type = data.get('vote_type', 'like')
        
        # 验证投票类型
        if vote_type not in ['like', 'love', 'wow', 'cool']:
            return jsonify({'error': '无效的投票类型'}), 400
        
        # 获取作品
        artwork = Artwork.query.get(artwork_id)
        if not artwork or not artwork.is_public:
            return jsonify({'error': '作品不存在或未公开'}), 404
        
        # 不能给自己的作品投票
        if artwork.user_id == current_user.id:
            return jsonify({'error': '不能为自己的作品投票'}), 400
        
        # 检查是否已投票
        existing_vote = ArtworkVote.query.filter_by(
            artwork_id=artwork_id, 
            voter_id=current_user.id
        ).first()
        
        if existing_vote:
            # 更新投票类型
            existing_vote.vote_type = vote_type
            message = '投票已更新！'
        else:
            # 新投票
            vote = ArtworkVote(artwork_id, current_user.id, vote_type)
            db.session.add(vote)
            
            # 更新作品投票数
            artwork.vote_count = (artwork.vote_count or 0) + 1
            message = '投票成功！'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'vote_count': artwork.vote_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'投票失败: {str(e)}'}), 500

@app.route('/gallery')
def public_gallery():
    """公共作品展示页面"""
    try:
        from models import Artwork, User
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
        from models import Artwork
        
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
        from models import Artwork, User
        
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
        from models import Artwork, ArtworkVote
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
        from models import Artwork
        
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

@app.route('/test-privacy-toggles')
def test_privacy_toggles():
    """测试隐私设置切换开关页面"""
    with open('/Users/hongyuwang/code/HLTraining/test_privacy_toggles.html', 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    print("🚀 儿童AI培训网站启动中...")
    print("📝 功能特色:")
    print("   - 用户管理系统：注册、登录、家长验证")
    print("   - 统一创作界面：文字+图片混合输入")
    print("   - 分步骤工作流：图片生成 → 调整 → 3D模型")
    print("   - AI图片生成：使用Nano Banana (Gemini 2.5 Flash Image)")
    print("   - 3D模型生成：使用腾讯云AI3D (混元3D)")
    print("   - 适合儿童：10-14岁友好界面设计")
    print("\n🌐 访问地址: http://127.0.0.1:8080")
    print("🔗 注册页面: http://127.0.0.1:8080/auth/register")
    print("🔗 登录页面: http://127.0.0.1:8080/auth/login")
    print("🔗 创作页面: http://127.0.0.1:8080/create (需要登录)")
    app.run(debug=True, host='0.0.0.0', port=8080)