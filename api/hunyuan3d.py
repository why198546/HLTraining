import requests
import os
import json
import time
import uuid
import cv2
import numpy as np
from PIL import Image

class Hunyuan3DAPI:
    """3D模型生成API类 - 使用本地算法从2D图像生成3D模型"""
    
    def __init__(self):
        # 从环境变量获取API密钥，或使用默认值
        self.api_key = os.getenv('HUNYUAN3D_API_KEY', 'your-api-key-here')
        self.base_url = 'https://api.hunyuan3d.com/v1'  # 示例URL，需要替换为实际API地址
        self.upload_folder = 'uploads'
        self.models_folder = 'models'
        
        # 确保模型文件夹存在
        os.makedirs(self.models_folder, exist_ok=True)
    
    def _encode_image_to_base64(self, image_path):
        """将图片编码为base64格式"""
        try:
            import base64
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码错误: {str(e)}")
            return None
    
    def _analyze_image_for_3d(self, image_path):
        """分析图像以生成3D形状"""
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                return None, None
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None, None
            
            # 获取最大轮廓（主要物体）
            main_contour = max(contours, key=cv2.contourArea)
            
            # 计算轮廓的边界框
            x, y, w, h = cv2.boundingRect(main_contour)
            
            # 归一化轮廓点到[-1, 1]范围
            normalized_contour = []
            for point in main_contour:
                px, py = point[0]
                # 归一化到[-1, 1]
                norm_x = (px - x - w/2) / (w/2) if w > 0 else 0
                norm_y = (py - y - h/2) / (h/2) if h > 0 else 0
                normalized_contour.append([norm_x, norm_y])
            
            return normalized_contour, img
            
        except Exception as e:
            print(f"图像分析错误: {str(e)}")
            return None, None
    
    def _create_enhanced_gltf(self, contour, image_data, model_name):
        """基于图像轮廓创建增强的GLTF 3D模型"""
        try:
            if not contour:
                # 如果没有轮廓，创建一个简单的立方体
                return self._create_simple_cube_gltf(model_name)
            
            # 从轮廓生成顶点
            vertices = []
            indices = []
            
            # 底面顶点（z=0）
            for i, point in enumerate(contour):
                vertices.extend([point[0], point[1], 0.0])  # 底面
            
            # 顶面顶点（z=0.5，给模型一些厚度）
            for i, point in enumerate(contour):
                vertices.extend([point[0], point[1], 0.5])  # 顶面
            
            # 生成三角形索引
            n = len(contour)
            
            # 底面三角形（fan triangulation）
            for i in range(1, n-1):
                indices.extend([0, i, i+1])
            
            # 顶面三角形
            for i in range(1, n-1):
                indices.extend([n, n+i+1, n+i])
            
            # 侧面三角形
            for i in range(n):
                next_i = (i + 1) % n
                # 第一个三角形
                indices.extend([i, i+n, next_i])
                # 第二个三角形
                indices.extend([next_i, i+n, next_i+n])
            
            # 创建GLTF内容
            gltf_content = {
                "asset": {
                    "version": "2.0",
                    "generator": "HLTraining 3D Generator"
                },
                "scenes": [{"nodes": [0]}],
                "nodes": [{"mesh": 0}],
                "meshes": [{
                    "primitives": [{
                        "attributes": {
                            "POSITION": 0
                        },
                        "indices": 1,
                        "material": 0
                    }]
                }],
                "materials": [{
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [0.8, 0.6, 0.4, 1.0],
                        "metallicFactor": 0.1,
                        "roughnessFactor": 0.8
                    },
                    "name": "ChildFriendlyMaterial"
                }],
                "accessors": [
                    {
                        "bufferView": 0,
                        "componentType": 5126,  # FLOAT
                        "count": len(vertices) // 3,
                        "type": "VEC3",
                        "max": [1.0, 1.0, 0.5],
                        "min": [-1.0, -1.0, 0.0]
                    },
                    {
                        "bufferView": 1,
                        "componentType": 5123,  # UNSIGNED_SHORT
                        "count": len(indices),
                        "type": "SCALAR"
                    }
                ],
                "bufferViews": [
                    {
                        "buffer": 0,
                        "byteOffset": 0,
                        "byteLength": len(vertices) * 4,  # 4 bytes per float
                        "target": 34962  # ARRAY_BUFFER
                    },
                    {
                        "buffer": 0,
                        "byteOffset": len(vertices) * 4,
                        "byteLength": len(indices) * 2,  # 2 bytes per short
                        "target": 34963  # ELEMENT_ARRAY_BUFFER
                    }
                ],
                "buffers": [{
                    "byteLength": len(vertices) * 4 + len(indices) * 2,
                    "uri": f"data:application/octet-stream;base64,{self._create_binary_data(vertices, indices)}"
                }]
            }
            
            return json.dumps(gltf_content, indent=2)
            
        except Exception as e:
            print(f"创建GLTF模型错误: {str(e)}")
            return self._create_simple_cube_gltf(model_name)
    
    def _create_binary_data(self, vertices, indices):
        """创建GLTF的二进制数据"""
        import struct
        import base64
        
        # 将浮点数顶点数据转换为字节
        vertex_bytes = struct.pack(f'{len(vertices)}f', *vertices)
        
        # 将整数索引数据转换为字节
        index_bytes = struct.pack(f'{len(indices)}H', *indices)
        
        # 合并数据
        combined_data = vertex_bytes + index_bytes
        
        # 转换为base64
        return base64.b64encode(combined_data).decode('utf-8')
    
    def _create_simple_cube_gltf(self, model_name):
        """创建一个简单的彩色立方体GLTF模型（备用方案）"""
        gltf_content = {
            "asset": {
                "version": "2.0",
                "generator": "HLTraining 3D Generator - Simple Cube"
            },
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {
                        "POSITION": 0
                    },
                    "indices": 1,
                    "material": 0
                }]
            }],
            "materials": [{
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.9, 0.3, 0.5, 1.0],  # 粉色，儿童友好
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.9
                },
                "name": "CubeMaterial"
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": 8,
                    "type": "VEC3",
                    "max": [1.0, 1.0, 1.0],
                    "min": [-1.0, -1.0, -1.0]
                },
                {
                    "bufferView": 1,
                    "componentType": 5123,
                    "count": 36,
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {
                    "buffer": 0,
                    "byteOffset": 0,
                    "byteLength": 96,
                    "target": 34962
                },
                {
                    "buffer": 0,
                    "byteOffset": 96,
                    "byteLength": 72,
                    "target": 34963
                }
            ],
            "buffers": [{
                "byteLength": 168,
                "uri": "data:application/octet-stream;base64,AACAvwAAgL8AAIC/AACAvwAAgL8AAIA/AACAvwAAgD8AAIC/AACAvwAAgD8AAIA/AACAPwAAgL8AAIC/AACAPwAAgL8AAIA/AACAPwAAgD8AAIC/AACAPwAAgD8AAIA/AAAAAAEAAAACAAAAAwAAAAIAAAABAAAABAAAAAUAAAAGAAAABwAAAAYAAAAFAAAACAAAAAgAAAAJAAAACgAAAAkAAAAIAAAACwAAAAsAAAAMAAAADQAAAA0AAAALAAAADgAAAA4AAAAPAAAA"
            }]
        }
        
        return json.dumps(gltf_content, indent=2)
    
    def generate_3d_model(self, image_path):
        """从2D图片生成3D模型 - 使用本地算法基于图像轮廓"""
        try:
            print("正在基于图像生成3D模型...")
            
            # 分析图像获取轮廓信息
            contour, image_data = self._analyze_image_for_3d(image_path)
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            model_id = str(uuid.uuid4())[:8]
            model_filename = f"{base_name}_{model_id}.gltf"
            model_path = os.path.join(self.models_folder, model_filename)
            
            # 基于轮廓创建GLTF模型
            gltf_content = self._create_enhanced_gltf(contour, image_data, base_name)
            
            # 保存GLTF文件
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(gltf_content)
            
            print(f"3D模型生成完成，保存至: {model_path}")
            return model_path
            
        except Exception as e:
            print(f"3D模型生成错误: {str(e)}")
            return None
    
    def optimize_for_web(self, model_path):
        """优化3D模型以适合Web展示"""
        try:
            print(f"正在优化3D模型: {model_path}")
            
            # 这里可以添加模型优化逻辑
            # 例如：减少多边形数量、压缩纹理等
            
            optimized_filename = model_path.replace('.gltf', '_optimized.gltf')
            
            # 简单复制文件作为示例（实际开发中需要真正的优化）
            import shutil
            shutil.copy2(model_path, optimized_filename)
            
            print(f"模型优化完成: {optimized_filename}")
            return optimized_filename
            
        except Exception as e:
            print(f"模型优化错误: {str(e)}")
            return model_path  # 返回原始文件
    
    def check_api_status(self):
        """检查API状态"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # response = requests.get(f'{self.base_url}/status', headers=headers)
            # return response.status_code == 200
            
            # 模拟API状态检查
            return True
            
        except Exception as e:
            print(f"API状态检查失败: {str(e)}")
            return False