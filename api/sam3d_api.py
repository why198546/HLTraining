import os
import requests
import base64
import time
from PIL import Image
import numpy as np
import io
from typing import Optional, Dict, Any
import trimesh
import tempfile

class SAM3DAPI:
    """SAM 3D API类 - 通过Hugging Face Spaces集成Meta SAM 3D Objects"""
    
    def __init__(self):
        """初始化SAM 3D客户端（Hugging Face方案）"""
        # Hugging Face配置
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', '')  # 可选，提高速率限制
        self.upload_folder = 'uploads'
        self.models_folder = 'models'
        
        # 确保文件夹存在
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.models_folder, exist_ok=True)
        
        # Hugging Face Inference API端点
        self.api_url = "https://api-inference.huggingface.co/models/facebook/sam-3d-objects"
        
        # 初始化Gradio客户端（备用方案）
        self.gradio_client = None
        try:
            from gradio_client import Client
            # 注意：这个Space URL可能需要根据实际情况调整
            # 目前SAM 3D可能还没有公开的Gradio Space
            # self.gradio_client = Client("facebook/sam-3d-objects")
            print("✅ Gradio客户端准备就绪（如果Space可用）")
        except Exception as e:
            print(f"⚠️ Gradio客户端初始化失败: {str(e)}")
        
        print("✅ SAM 3D API 客户端初始化成功 (Hugging Face方案)")
    
    def generate_3d_from_image(self, image_path: str, mask: Optional[np.ndarray] = None) -> Optional[str]:
        """从单张图片生成3D模型
        
        Args:
            image_path: 输入图片路径
            mask: 可选的物体遮罩（二值化numpy数组）
            
        Returns:
            3D模型文件路径（GLTF格式）或None
        """
        try:
            print(f"🎨 开始使用SAM 3D生成3D模型: {image_path}")
            
            # 1. 准备RGBA图片（mask嵌入alpha通道）
            rgba_image = self._prepare_rgba_image(image_path, mask)
            
            # 2. 调用Hugging Face API
            ply_path = self._call_sam3d_api(rgba_image)
            
            if not ply_path:
                print("❌ SAM 3D API调用失败")
                return None
            
            # 3. 转换为GLTF格式
            gltf_path = self.convert_to_gltf(ply_path)
            
            if gltf_path:
                print(f"✅ SAM 3D生成完成: {gltf_path}")
                return gltf_path
            else:
                print("❌ GLTF转换失败")
                return None
                
        except Exception as e:
            print(f"❌ SAM 3D生成错误: {str(e)}")
            return None
    
    def auto_segment_and_generate(self, image_path: str) -> Optional[str]:
        """自动分割图片中的主要物体并生成3D模型
        
        使用简单的背景移除作为mask，或者直接使用整个图片
        
        Args:
            image_path: 输入图片路径
            
        Returns:
            3D模型文件路径（GLTF格式）或None
        """
        try:
            print(f"🔍 自动分割并生成3D模型: {image_path}")
            
            # 方案1: 使用简单的背景移除
            mask = self._simple_background_removal(image_path)
            
            # 方案2: 如果有SAM 2 API，可以调用它来生成更好的mask
            # mask = self._call_sam2_for_mask(image_path)
            
            return self.generate_3d_from_image(image_path, mask)
            
        except Exception as e:
            print(f"❌ 自动分割生成错误: {str(e)}")
            return None
    
    def convert_to_gltf(self, ply_path: str) -> Optional[str]:
        """将Gaussian Splat (.ply) 转换为GLTF格式用于Web显示
        
        Args:
            ply_path: PLY文件路径
            
        Returns:
            GLTF文件路径或None
        """
        try:
            print(f"🔄 转换PLY到GLTF: {ply_path}")
            
            # 使用trimesh加载PLY文件
            mesh = trimesh.load(ply_path)
            
            # 生成GLTF文件路径
            base_name = os.path.splitext(os.path.basename(ply_path))[0]
            gltf_filename = f"{base_name}.gltf"
            gltf_path = os.path.join(self.models_folder, gltf_filename)
            
            # 导出为GLTF
            mesh.export(gltf_path, file_type='gltf')
            
            print(f"✅ GLTF转换完成: {gltf_path}")
            return gltf_path
            
        except Exception as e:
            print(f"❌ GLTF转换错误: {str(e)}")
            return None
    
    def _prepare_rgba_image(self, image_path: str, mask: Optional[np.ndarray] = None) -> Image.Image:
        """准备RGBA格式图片，将mask嵌入alpha通道
        
        Args:
            image_path: 原始图片路径
            mask: 可选的mask（二值化numpy数组）
            
        Returns:
            RGBA格式的PIL Image
        """
        # 加载原始图片
        img = Image.open(image_path).convert('RGB')
        
        if mask is None:
            # 如果没有mask，创建一个全白的alpha通道（全部可见）
            alpha = Image.new('L', img.size, 255)
        else:
            # 将mask转换为PIL Image
            if isinstance(mask, np.ndarray):
                # 确保mask是0-255范围
                mask_normalized = (mask * 255).astype(np.uint8)
                alpha = Image.fromarray(mask_normalized, mode='L')
                # 调整大小以匹配原图
                if alpha.size != img.size:
                    alpha = alpha.resize(img.size, Image.LANCZOS)
            else:
                alpha = mask
        
        # 合并RGB和Alpha通道
        rgba = img.copy()
        rgba.putalpha(alpha)
        
        return rgba
    
    def _simple_background_removal(self, image_path: str) -> np.ndarray:
        """简单的背景移除，生成mask
        
        使用基于颜色的简单算法，假设背景是纯色或接近白色
        
        Args:
            image_path: 图片路径
            
        Returns:
            二值化mask（numpy数组，0-1范围）
        """
        import cv2
        
        # 读取图片
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 假设背景是白色或浅色
        # 定义白色范围
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        # 创建mask（白色部分为0，其他为1）
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        foreground_mask = cv2.bitwise_not(white_mask)
        
        # 形态学操作，去除噪点
        kernel = np.ones((5, 5), np.uint8)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
        
        # 归一化到0-1
        mask_normalized = foreground_mask.astype(np.float32) / 255.0
        
        return mask_normalized
    
    def _call_sam3d_api(self, rgba_image: Image.Image, max_retries: int = 3) -> Optional[str]:
        """调用SAM 3D API（Hugging Face Inference API）
        
        Args:
            rgba_image: RGBA格式的PIL Image
            max_retries: 最大重试次数
            
        Returns:
            PLY文件路径或None
        """
        # 注意：由于SAM 3D刚发布，Hugging Face Inference API可能还不支持
        # 这里提供一个框架，实际使用时可能需要调整
        
        print("⚠️ 注意：SAM 3D的Hugging Face Inference API可能还不可用")
        print("📝 当前实现为占位符，需要等待官方API支持或使用本地部署")
        
        # 方案A: 尝试使用Hugging Face Inference API
        for attempt in range(max_retries):
            try:
                print(f"🔥 尝试调用SAM 3D API (尝试 {attempt + 1}/{max_retries})...")
                
                # 将图片转换为字节
                img_byte_arr = io.BytesIO()
                rgba_image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # 准备请求头
                headers = {
                    "Content-Type": "image/png"
                }
                if self.hf_token:
                    headers["Authorization"] = f"Bearer {self.hf_token}"
                
                # 发送请求
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=img_byte_arr,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # 保存PLY文件
                    timestamp = int(time.time())
                    ply_filename = f"sam3d_model_{timestamp}.ply"
                    ply_path = os.path.join(self.models_folder, ply_filename)
                    
                    with open(ply_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ SAM 3D API调用成功，PLY已保存: {ply_path}")
                    return ply_path
                else:
                    print(f"⚠️ API返回错误: {response.status_code}")
                    print(f"响应内容: {response.text[:200]}")
                    
            except Exception as e:
                print(f"⚠️ 尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    print("🔄 等待2秒后重试...")
                    time.sleep(2)
        
        # 方案B: 如果Inference API不可用，尝试使用Gradio Client
        if self.gradio_client:
            try:
                print("🔄 尝试使用Gradio Client...")
                # 这里需要根据实际的Gradio Space接口调整
                # result = self.gradio_client.predict(rgba_image, api_name="/predict")
                # return result
                print("⚠️ Gradio Client方案需要等待官方Space发布")
            except Exception as e:
                print(f"❌ Gradio Client调用失败: {str(e)}")
        
        print("❌ 所有API调用方案都失败了")
        print("💡 建议：")
        print("   1. 检查Hugging Face Token是否配置正确")
        print("   2. 等待SAM 3D官方API支持")
        print("   3. 或考虑本地部署SAM 3D模型")
        
        return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取SAM 3D模型信息
        
        Returns:
            包含模型信息的字典
        """
        return {
            "name": "SAM 3D Objects",
            "provider": "Meta AI",
            "version": "1.0",
            "method": "Hugging Face Spaces",
            "input_format": "RGBA (mask in alpha channel)",
            "output_format": "Gaussian Splat (.ply) -> GLTF",
            "status": "experimental",
            "note": "需要等待官方API支持或使用本地部署"
        }
