from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
from api.nano_banana import NanoBananaAPI
from api.hunyuan3d import Simple3DGenerator
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    try:
        print(f"🧊 开始3D模型生成: {image_path}")
        
        # 初始化3D生成器
        generator_3d = Simple3DGenerator()
        
        # 生成3D模型
        model_path = generator_3d.generate_3d_model(image_path)
        
        if model_path:
            print(f"✅ 3D模型生成成功: {model_path}")
            return model_path.replace('uploads/', '/uploads/')
        else:
            print("❌ 3D模型生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return None

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/create')
def create():
    """创作页面"""
    return render_template('create.html')

@app.route('/gallery')
def gallery():
    """作品集页面"""
    return render_template('gallery.html')

@app.route('/test')
def test():
    """测试页面"""
    return render_template('test.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件访问"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """统一的图片生成接口 - 支持文字和图片混合输入"""
    try:
        prompt = request.form.get('prompt', '').strip()
        uploaded_file = request.files.get('sketch')
        
        if not prompt and not uploaded_file:
            return jsonify({'error': '请输入文字描述或上传图片'}), 400
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        # 处理上传的图片
        sketch_path = None
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = str(uuid.uuid4()) + '_' + secure_filename(uploaded_file.filename)
            sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(sketch_path)
            
            # 预处理手绘图片
            processed_sketch = preprocess_sketch(sketch_path)
            if processed_sketch:
                sketch_path = processed_sketch
        
        print(f"🎨 开始生成图片 - 文字: {prompt}, 图片: {sketch_path}")
        
        # 根据输入类型生成图片
        if sketch_path and prompt:
            # 图片+文字模式
            generated_image_path = nano_banana.generate_image_from_sketch_and_text(sketch_path, prompt)
        elif sketch_path:
            # 纯图片模式
            generated_image_path = nano_banana.generate_image_from_sketch(sketch_path)
        else:
            # 纯文字模式
            generated_image_path = nano_banana.generate_image_from_text(prompt)
        
        if generated_image_path:
            print(f"✅ 图片生成完成: {generated_image_path}")
            
            # 返回相对路径用于前端显示
            relative_path = generated_image_path.replace('uploads/', '/uploads/')
            
            return jsonify({
                'success': True,
                'image_url': relative_path,
                'message': '图片生成成功！'
            })
        else:
            return jsonify({'error': '图片生成失败，请稍后重试'}), 500
            
    except Exception as e:
        print(f"❌ 图片生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.route('/adjust-image', methods=['POST'])
def adjust_image():
    """调整现有图片"""
    try:
        current_image = request.form.get('current_image')
        adjust_prompt = request.form.get('adjust_prompt', '').strip()
        
        if not current_image or not adjust_prompt:
            return jsonify({'error': '缺少图片路径或调整说明'}), 400
        
        # 将相对路径转换为绝对路径
        if current_image.startswith('/uploads/'):
            current_image = current_image.replace('/uploads/', 'uploads/')
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        print(f"🔧 开始调整图片: {current_image} - 调整说明: {adjust_prompt}")
        
        # 使用调整提示词重新生成图片
        adjusted_image_path = nano_banana.adjust_image(current_image, adjust_prompt)
        
        if adjusted_image_path:
            print(f"✅ 图片调整完成: {adjusted_image_path}")
            
            # 返回相对路径用于前端显示
            relative_path = adjusted_image_path.replace('uploads/', '/uploads/')
            
            return jsonify({
                'success': True,
                'image_url': relative_path,
                'message': '图片调整成功！'
            })
        else:
            return jsonify({'error': '图片调整失败，请稍后重试'}), 500
            
    except Exception as e:
        print(f"❌ 图片调整错误: {str(e)}")
        return jsonify({'error': f'调整失败: {str(e)}'}), 500

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model_endpoint():
    """从图片生成3D模型"""
    try:
        image_path = request.form.get('image_path')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        # 将相对路径转换为绝对路径
        if image_path.startswith('/uploads/'):
            image_path = image_path.replace('/uploads/', 'uploads/')
        
        print(f"🧊 开始生成3D模型: {image_path}")
        
        # 生成3D模型
        model_result = generate_3d_model_from_image(image_path)
        
        if model_result:
            print(f"✅ 3D模型生成完成: {model_result}")
            
            return jsonify({
                'success': True,
                'model_url': model_result,
                'message': '3D模型生成成功！'
            })
        else:
            return jsonify({'error': '3D模型生成失败，请稍后重试'}), 500
            
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

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
    print("   - 3D模型生成：使用本地算法")
    print("   - 适合儿童：10-14岁友好界面设计")
    print("\n🌐 访问地址: http://127.0.0.1:8080")
    print("🔗 创作页面: http://127.0.0.1:8080/create")
    app.run(debug=True, host='0.0.0.0', port=8080)