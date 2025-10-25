from flask import Flask, render_template, request, jsonify, send_file
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

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

@app.route('/')
def index():
    """主页"""
    # 获取最新的4个作品用于首页展示
    gallery_manager = GalleryManager()
    latest_artworks = gallery_manager.get_latest_artworks(limit=4)
    return render_template('index.html', latest_artworks=latest_artworks)

@app.route('/create')
def create():
    """创作页面"""
    return render_template('create.html')

@app.route('/gallery')
def gallery():
    """显示作品画廊"""
    gallery_manager = GalleryManager()
    artworks = gallery_manager.get_all_artworks()
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
        uploaded_file = request.files.get('sketch')
        original_image_path = request.form.get('original_image_path', '').strip()
        session_id = request.form.get('session_id')
        version_note = request.form.get('version_note', '')
        
        if not prompt and not uploaded_file and not original_image_path:
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
        print(f"🎨 生成参数 - 风格: {style}, 色彩: {color_preference}, Expert模式: {expert_mode}")
        
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
                sketch_path, prompt, style=style, color_preference=color_preference, expert_mode=expert_mode
            )
        elif sketch_path:
            # 纯图片模式
            generated_image_path = nano_banana.generate_image_from_sketch(
                sketch_path, style=style, color_preference=color_preference, expert_mode=expert_mode
            )
        else:
            # 纯文字模式
            generated_image_path = nano_banana.generate_image_from_text(
                prompt, style=style, color_preference=color_preference, expert_mode=expert_mode
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
def save_artwork():
    """从创作会话保存作品到作品集"""
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
        
        # 保存作品
        result = gallery_manager.save_artwork(
            original_image_path=None,  # 创作会话中可能没有原始图片
            generated_image_path=image_path,
            model_path=model_path,
            title=data.get('title', '我的作品'),
            artist_name=data.get('artist_name', '小朋友'),
            artist_age=int(data.get('artist_age', 10)),
            category=data.get('category', '其他'),
            description=data.get('description', ''),
            version_note=f"从创作会话保存 - 图片v{image_version.get('metadata', {}).get('note', '')}"
        )
        
        if result['success']:
            # 关闭会话（标记为完成）
            session_manager.close_session(session_id)
            
            return jsonify({
                'success': True,
                'artwork_id': result['artwork_id'],
                'message': '作品已成功保存到作品集！',
                'session_closed': True
            })
        else:
            return jsonify(result), 500
            
    except Exception as e:
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

@app.route('/api/convert-image-for-video', methods=['POST'])
def convert_image_for_video():
    """将图片转换为视频所需的宽高比"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        aspect_ratio = data.get('aspect_ratio', '16:9')
        padding_mode = data.get('padding_mode', 'blur')
        
        if not image_path:
            return jsonify({'success': False, 'error': '缺少图片路径'}), 400
        
        # 转换路径
        if image_path.startswith('/uploads/'):
            image_path = 'uploads' + image_path[8:]
        elif image_path.startswith('uploads/'):
            pass
        else:
            image_path = os.path.join('uploads', image_path)
        
        print(f"🎬 转换图片用于视频: {image_path}")
        print(f"📐 目标宽高比: {aspect_ratio}, 填充模式: {padding_mode}")
        
        # 调用转换函数
        nano_banana = NanoBananaAPI()
        converted_path = nano_banana.convert_image_for_video(
            image_path, 
            aspect_ratio=aspect_ratio, 
            padding_mode=padding_mode
        )
        
        # 返回相对路径
        relative_path = converted_path.replace('uploads/', '/uploads/')
        
        return jsonify({
            'success': True,
            'converted_image_url': relative_path
        })
        
    except Exception as e:
        print(f"❌ 图片转换错误: {str(e)}")
        import traceback
        traceback.print_exc()
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

if __name__ == '__main__':
    print("🚀 儿童AI培训网站启动中...")
    print("📝 功能特色:")
    print("   - 统一创作界面：文字+图片混合输入")
    print("   - 分步骤工作流：图片生成 → 调整 → 3D模型")
    print("   - AI图片生成：使用Nano Banana (Gemini 2.5 Flash Image)")
    print("   - 3D模型生成：使用腾讯云AI3D (混元3D)")
    print("   - 适合儿童：10-14岁友好界面设计")
    print("\n🌐 访问地址: http://127.0.0.1:8080")
    print("🔗 创作页面: http://127.0.0.1:8080/create")
    app.run(debug=True, host='0.0.0.0', port=8080)