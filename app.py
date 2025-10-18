from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
from api.nano_banana import NanoBananaAPI
from api.hunyuan3d import Hunyuan3DAPI
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

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/generate-from-text', methods=['POST'])
def generate_from_text():
    """从文字描述生成图片"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        workflow = data.get('workflow', 'text-to-image')
        
        if not prompt:
            return jsonify({'error': '缺少文字描述'}), 400
        
        # 初始化Nano Banana API
        nano_banana = NanoBananaAPI()
        
        print(f"🎨 开始文字生成图片: {prompt}")
        
        # 使用Gemini生成图片
        generated_image_path = nano_banana.generate_image_from_text(prompt)
        
        if generated_image_path:
            print(f"✅ 文字生成图片完成: {generated_image_path}")
            
            result = {
                'success': True,
                'image_path': generated_image_path.replace('uploads/', ''),
                'message': '图片生成成功！'
            }
            
            # 如果是完整工作流程，继续生成3D模型
            if workflow == 'text-to-image-to-model':
                print("🧊 继续生成3D模型...")
                model_result = generate_3d_model_from_image(generated_image_path)
                if model_result:
                    result['model_path'] = model_result
                    result['message'] = '图片和3D模型生成完成！'
            
            return jsonify(result)
        else:
            return jsonify({'error': '图片生成失败，请稍后重试'}), 500
            
    except Exception as e:
        print(f"❌ 文字生成图片错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

def generate_3d_model_from_image(image_path):
    """从图片生成3D模型"""
    try:
        # 这里可以集成Hunyuan3D或其他3D生成服务
        # 目前返回模拟结果
        print(f"🧊 正在为图片生成3D模型: {image_path}")
        
        # 模拟3D模型生成过程
        import time
        time.sleep(2)  # 模拟处理时间
        
        # 返回模拟的模型文件路径
        model_filename = os.path.basename(image_path).replace('.png', '_model.obj')
        return model_filename
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return None

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(filepath)
            
            # 预处理图片
            processed_path = preprocess_sketch(filepath)
            if processed_path is None:
                return jsonify({'error': '图片预处理失败'}), 500
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': '文件上传成功！',
                'processed': True
            })
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/colorize', methods=['POST'])
def colorize_image():
    """使用AI模型为图片上色"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': '缺少文件名'}), 400
        
        # 获取文件路径
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
        
        # 使用预处理后的文件
        processed_path = filepath.replace('.', '_processed.')
        
        # 获取用户描述
        description = request.json.get('description', '')
        
        # 调用Nano Banana API进行上色
        nano_api = NanoBananaAPI()
        colored_image_path = nano_api.colorize_sketch(processed_path, description)
        
        if colored_image_path:
            # 生成手办风格图片
            figurine_path = nano_api.generate_figurine_style(colored_image_path, description)
            
            return jsonify({
                'success': True,
                'colored_image': os.path.basename(colored_image_path),
                'figurine_image': os.path.basename(figurine_path) if figurine_path else None,
                'message': 'AI上色完成！'
            })
        else:
            return jsonify({'error': 'AI上色失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'上色失败: {str(e)}'}), 500

@app.route('/generate_3d', methods=['POST'])
def generate_3d_model():
    """生成3D模型"""
    try:
        data = request.get_json()
        image_filename = data.get('image_filename')
        
        if not image_filename:
            return jsonify({'error': '缺少图片文件名'}), 400
        
        # 获取图片路径
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        if not os.path.exists(image_path):
            return jsonify({'error': '图片文件不存在'}), 404
        
        # 调用Hunyuan3D API生成3D模型
        hunyuan_api = Hunyuan3DAPI()
        model_path = hunyuan_api.generate_3d_model(image_path)
        
        if model_path:
            return jsonify({
                'success': True,
                'model_file': os.path.basename(model_path),
                'message': '3D模型生成完成！'
            })
        else:
            return jsonify({'error': '3D模型生成失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'3D模型生成失败: {str(e)}'}), 500

@app.route('/finetune', methods=['POST'])
def finetune_model():
    """模型微调"""
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'colorization')
        training_images = data.get('training_images', [])
        
        if not training_images:
            return jsonify({'error': '缺少训练图片'}), 400
        
        # 这里可以实现模型微调逻辑
        # 由于微调通常需要大量计算资源，这里提供一个简化的示例
        
        return jsonify({
            'success': True,
            'message': '模型微调已开始，请稍后查看结果',
            'job_id': str(uuid.uuid4())
        })
        
    except Exception as e:
        return jsonify({'error': f'模型微调失败: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/gallery')
def gallery():
    """作品展示页面"""
    return render_template('gallery.html')

@app.route('/tutorial')
def tutorial():
    """教程页面"""
    return render_template('tutorial.html')

@app.route('/test-images')
def test_images():
    """图片显示测试页面"""
    return send_file('test_images.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/generate-3d-model', methods=['POST'])
def generate_3d_model_endpoint():
    """生成3D模型的端点"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': '缺少图片路径'}), 400
        
        # 调用3D模型生成
        model_result = generate_3d_model_from_image(os.path.join('uploads', image_path))
        
        if model_result:
            return jsonify({
                'success': True,
                'model_path': model_result,
                'message': '3D模型生成成功！'
            })
        else:
            return jsonify({'error': '3D模型生成失败'}), 500
            
    except Exception as e:
        print(f"❌ 3D模型生成错误: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': '文件太大，请选择小于16MB的图片'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)