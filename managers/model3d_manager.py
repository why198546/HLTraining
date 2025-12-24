"""3D模型相关业务逻辑管理器"""
import os

import cv2
import numpy as np

from api.hunyuan3d import Hunyuan3DGenerator
from api.sam3d_api import SAM3DAPI


class Model3DManager:
    """3D模型生成管理器"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    @staticmethod
    def allowed_file(filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Model3DManager.ALLOWED_EXTENSIONS
    
    @staticmethod
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
    
    @staticmethod
    def generate_3d_model_from_image(image_path, session_id=None, version_number=1, api_version='rapid'):
        """从单张图片生成3D模型
        
        Args:
            image_path: 图片文件路径
            session_id: 会话ID，如果提供，则直接保存到session目录
            version_number: 版本号
            api_version: API版本，'rapid'=极速版（默认），'pro'=专业版
            
        Returns:
            str: 3D模型文件路径（绝对路径）
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        print(f"🧊 开始3D模型生成: {image_path}")
        if session_id:
            print(f"💾 Session ID: {session_id}, 版本号: v{version_number}")
        print(f"🔧 API版本: {api_version}")
        
        # 初始化3D生成器
        generator_3d = Hunyuan3DGenerator()
        
        # 生成3D模型（如果失败会抛出异常）
        model_path = generator_3d.generate_3d_model(image_path, session_id, version_number, api_version)
        
        print(f"✅ 3D模型生成成功: {model_path}")
        return model_path
    
    @staticmethod
    def generate_3d_model_from_multi_view(view_images):
        """从多视角图片生成3D模型
        
        Args:
            view_images: dict with keys 'front', 'back', 'left', 'right'
        
        Returns:
            str: 3D模型文件路径（绝对路径）
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        print(f"🧊 开始多视角3D模型生成")
        
        # 初始化3D生成器
        generator_3d = Hunyuan3DGenerator()
        
        # 生成3D模型（多视角模式）
        # 传递view_images字典，生成器会格式化为Hunyuan API要求的ViewImages数组
        model_path = generator_3d.generate_3d_model_multi_view(view_images)
        
        print(f"✅ 多视角3D模型生成成功: {model_path}")
        return model_path
    
    @staticmethod
    def generate_with_sam3d(image_path):
        """使用SAM 3D生成3D模型
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            tuple: (model_path, engine_name) - 模型路径和使用的引擎名称
            
        Note:
            如果SAM 3D失败，会自动降级到Hunyuan3D
        """
        print(f"🎨 开始使用SAM 3D生成3D模型: {image_path}")
        
        # 初始化SAM 3D API
        sam3d = SAM3DAPI()
        
        # 生成3D模型
        model_path = sam3d.auto_segment_and_generate(image_path)
        
        if not model_path:
            # 如果SAM 3D失败，自动降级到Hunyuan3D
            print("⚠️ SAM 3D生成失败，降级到Hunyuan3D")
            model_path = Model3DManager.generate_3d_model_from_image(image_path)
            engine_used = 'hunyuan3d'
        else:
            engine_used = 'sam3d'
        
        print(f"✅ 3D模型生成完成 (引擎: {engine_used}): {model_path}")
        return model_path, engine_used
    
    @staticmethod
    def compare_engines(image_path):
        """同时使用SAM 3D和Hunyuan3D生成，进行对比
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            dict: 包含两个引擎生成结果的字典
                {
                    'sam3d': {'success': bool, 'model_url': str, ...},
                    'hunyuan3d': {'success': bool, 'model_url': str, ...}
                }
        """
        print(f"🔍 开始对比两个3D引擎: {image_path}")
        
        results = {}
        
        # 尝试SAM 3D
        try:
            sam3d = SAM3DAPI()
            sam3d_model = sam3d.auto_segment_and_generate(image_path)
            if sam3d_model:
                results['sam3d'] = {
                    'success': True,
                    'model_path': sam3d_model,
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
            hunyuan_model = Model3DManager.generate_3d_model_from_image(image_path)
            results['hunyuan3d'] = {
                'success': True,
                'model_path': hunyuan_model,
                'engine': 'hunyuan3d'
            }
        except Exception as e:
            results['hunyuan3d'] = {
                'success': False,
                'error': str(e)
            }
        
        return results
    
    @staticmethod
    def get_sam3d_info():
        """获取SAM 3D模型信息"""
        sam3d = SAM3DAPI()
        return sam3d.get_model_info()
