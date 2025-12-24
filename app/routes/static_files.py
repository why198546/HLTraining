"""静态文件服务路由"""
import os

from flask import Blueprint, current_app, send_from_directory

static_files_bp = Blueprint('static_files', __name__)


@static_files_bp.route('/uploads/<path:filepath>')
def uploaded_file(filepath):
    """提供上传文件的访问（支持子目录）"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        # 检查文件扩展名，为3D模型文件设置正确的MIME类型
        if filepath.endswith('.glb'):
            mimetype = 'model/gltf-binary'
        elif filepath.endswith('.stl'):
            mimetype = 'application/sla'
        else:
            mimetype = None  # 让Flask自动检测
        
        # 支持子目录路径
        return send_from_directory(upload_folder, filepath, mimetype=mimetype)
    except FileNotFoundError:
        return "文件不存在", 404


@static_files_bp.route('/models/<filename>')
def model_file(filename):
    """提供3D模型文件的访问"""
    # 为3D模型文件设置正确的MIME类型
    if filename.endswith('.glb'):
        mimetype = 'model/gltf-binary'
    elif filename.endswith('.stl'):
        mimetype = 'application/sla'
    else:
        mimetype = None
    
    return send_from_directory('models', filename, mimetype=mimetype)


@static_files_bp.route('/creation_sessions/<path:filepath>')
def creation_session_file(filepath):
    """提供创作会话文件的访问"""
    try:
        # 使用绝对路径或相对于项目根目录的路径
        base_dir = os.path.abspath('.')
        full_path = os.path.join(base_dir, 'creation_sessions', filepath)
        
        # 调试信息
        print(f"🔍 请求文件: {filepath}")
        print(f"🔍 完整路径: {full_path}")
        print(f"🔍 文件是否存在: {os.path.exists(full_path)}")
        
        # 检查文件扩展名，为GLB和STL文件设置正确的MIME类型
        if filepath.endswith('.glb'):
            mimetype = 'model/gltf-binary'
        elif filepath.endswith('.stl'):
            mimetype = 'application/sla'
        else:
            mimetype = None  # 让Flask自动检测
        
        return send_from_directory(
            os.path.join(base_dir, 'creation_sessions'), 
            filepath,
            mimetype=mimetype
        )
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filepath}")
        return "文件不存在", 404
    except Exception as e:
        print(f"❌ 错误: {e}")
        return f"服务器错误: {str(e)}", 500


@static_files_bp.route('/static/creation_sessions/<path:filename>')
def static_creation_session(filename):
    """静态创作会话文件"""
    session_file_path = os.path.join('creation_sessions', filename)
    if os.path.exists(session_file_path):
        # 为3D模型文件设置正确的MIME类型
        if filename.endswith('.glb'):
            mimetype = 'model/gltf-binary'
        elif filename.endswith('.stl'):
            mimetype = 'application/sla'
        else:
            mimetype = None
        
        return send_from_directory('creation_sessions', filename, mimetype=mimetype)
    return "文件不存在", 404
