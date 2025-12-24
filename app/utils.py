"""通用工具函数"""
import glob
import os
from datetime import datetime

import cv2
import numpy as np


def normalize_path_for_url(file_path):
    """
    将文件系统路径转换为URL路径（跨平台）
    
    Args:
        file_path: 文件系统路径，可能包含 \ 或 /
        
    Returns:
        标准化的URL路径，以 / 开头，使用 / 作为分隔符
        
    Examples:
        Windows: 'uploads\\\\file.png' -> '/uploads/file.png'
        Linux/Mac: 'uploads/file.png' -> '/uploads/file.png'
    """
    if not file_path:
        return ''
    
    # 统一使用正斜杠（URL标准）
    url_path = file_path.replace('\\', '/')
    
    # 确保 uploads 目录路径以 /uploads/ 开头
    if 'uploads/' in url_path and not url_path.startswith('/'):
        # 找到 uploads/ 的位置
        idx = url_path.find('uploads/')
        url_path = '/' + url_path[idx:]
    elif 'models/' in url_path and not url_path.startswith('/'):
        # 旧的 models/ 路径也映射到 /uploads/3d_models/
        url_path = url_path.replace('models/', '/uploads/3d_models/')
    
    # 如果还没有 /，添加 /
    if not url_path.startswith('/'):
        url_path = '/' + url_path
    
    return url_path


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_sketch(image_path, force_process=False):
    """智能预处理图片
    
    Args:
        image_path: 图片路径
        force_process: 是否强制处理（默认False，会自动判断）
    
    Returns:
        str: 处理后的图片路径，如果不需要处理则返回原路径
    """
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # 如果不强制处理，则智能判断是否需要预处理
        if not force_process:
            # 判断是否是手绘线稿：
            # 1. 检查颜色分布 - 手绘线稿通常颜色单一
            # 2. 检查饱和度 - 手绘线稿饱和度低
            # 3. 检查边缘密度 - 手绘线稿边缘清晰
            
            # 转换到HSV色彩空间
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # 计算平均饱和度
            avg_saturation = np.mean(s)
            
            # 计算颜色种类（简化版）
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            unique_values = len(np.unique(gray))
            
            print(f"📊 图片分析 - 平均饱和度: {avg_saturation:.1f}, 灰度层次: {unique_values}")
            
            # 判断标准：
            # - 平均饱和度 < 30 且灰度层次 < 100 → 可能是线稿
            # - 平均饱和度 > 50 → 肯定是彩色图，不处理
            if avg_saturation > 50:
                print("✅ 检测到彩色参考图，保持原图不处理")
                return image_path
            elif avg_saturation < 30 and unique_values < 100:
                print("📝 检测到手绘线稿，进行预处理")
                # 继续执行预处理
            else:
                print("🤔 图片类型不明确，保持原图以保留更多信息")
                return image_path
        
        # 对手绘线稿进行预处理
        print("🎨 开始预处理手绘线稿...")
        
        # 转换为灰度图
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # 二值化处理
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 保存预处理后的图片
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, binary)
        
        print(f"✅ 预处理完成: {processed_path}")
        return processed_path
    except Exception as e:
        print(f"❌ 图片预处理错误: {str(e)}")
        # 出错时返回原图路径，不影响后续流程
        return image_path


def auto_save_artwork_to_db(session_id, generated_image_path, sketch_path=None, prompt=None, model_3d_path=None):
    """自动保存作品到数据库
    
    Args:
        session_id: 会话ID
        generated_image_path: 生成的图片路径
        sketch_path: 原始草图路径（可选）
        prompt: 提示词（可选）
        model_3d_path: 3D模型路径（可选）
        
    Returns:
        bool: 保存是否成功
    """
    try:
        from flask_login import current_user

        from auth.models import Artwork, db

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
            if model_3d_path:
                existing_artwork.model_3d = os.path.basename(model_3d_path)
                print(f"🧊 更新3D模型: {os.path.basename(model_3d_path)}")
            
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
            if model_3d_path:
                artwork.model_3d = os.path.basename(model_3d_path)
                print(f"🧊 保存3D模型: {os.path.basename(model_3d_path)}")
            
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
        from auth.models import db
        db.session.rollback()
        print(f"❌ 自动保存失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
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
