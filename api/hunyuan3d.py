"""
简化的3D模型生成器
专为儿童AI培训网站设计，使用本地算法从2D图片生成基础3D模型
"""

import os
import cv2
import numpy as np
import base64
import json
import uuid
from PIL import Image

class Simple3DGenerator:
    def __init__(self):
        # 确保models文件夹存在
        self.models_folder = "models"
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
            print(f"✅ 创建模型目录: {self.models_folder}")
    
    def generate_3d_model(self, image_path):
        """从2D图片生成3D模型 - 使用本地算法"""
        try:
            print("🎯 开始生成3D模型...")
            
            # 分析图像获取轮廓信息
            contour, image_data = self._analyze_image_for_3d(image_path)
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            model_id = str(uuid.uuid4())[:8]
            model_filename = f"{base_name}_3d_{model_id}.gltf"
            model_path = os.path.join(self.models_folder, model_filename)
            
            # 基于轮廓创建GLTF模型
            gltf_content = self._create_enhanced_gltf(contour, image_data, base_name)
            
            # 保存GLTF文件
            with open(model_path, 'w', encoding='utf-8') as f:
                f.write(gltf_content)
            
            print(f"🎨 3D模型生成完成: {model_path}")
            return model_path
            
        except Exception as e:
            print(f"❌ 3D模型生成错误: {str(e)}")
            return None
    
    def _analyze_image_for_3d(self, image_path):
        """分析图像以获取3D生成所需的信息"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图像文件")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 选择最大的轮廓
            if contours:
                main_contour = max(contours, key=cv2.contourArea)
                # 简化轮廓
                epsilon = 0.02 * cv2.arcLength(main_contour, True)
                simplified_contour = cv2.approxPolyDP(main_contour, epsilon, True)
            else:
                # 如果没找到轮廓，创建一个默认的矩形轮廓
                h, w = gray.shape
                simplified_contour = np.array([[[w//4, h//4]], [[3*w//4, h//4]], [[3*w//4, 3*h//4]], [[w//4, 3*h//4]]])
            
            # 获取图像信息
            image_data = {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2] if len(image.shape) == 3 else 1
            }
            
            return simplified_contour, image_data
            
        except Exception as e:
            print(f"图像分析错误: {str(e)}")
            # 返回默认数据
            default_contour = np.array([[[100, 100]], [[300, 100]], [[300, 300]], [[100, 300]]])
            default_data = {'width': 400, 'height': 400, 'channels': 3}
            return default_contour, default_data
    
    def _create_enhanced_gltf(self, contour, image_data, model_name):
        """创建增强的GLTF 3D模型"""
        try:
            # 归一化轮廓坐标
            width = image_data['width']
            height = image_data['height']
            
            # 将轮廓点转换为3D坐标
            vertices = []
            indices = []
            
            # 底部顶点
            for i, point in enumerate(contour):
                x = (point[0][0] / width - 0.5) * 2  # 归一化到[-1, 1]
                z = -(point[0][1] / height - 0.5) * 2  # Z轴，翻转Y坐标
                vertices.extend([x, 0.0, z])  # 底部 Y=0
            
            # 顶部顶点
            extrude_height = 0.3  # 挤出高度
            for i, point in enumerate(contour):
                x = (point[0][0] / width - 0.5) * 2
                z = -(point[0][1] / height - 0.5) * 2
                vertices.extend([x, extrude_height, z])  # 顶部
            
            # 生成索引
            n = len(contour)
            
            # 底面三角形
            for i in range(1, n - 1):
                indices.extend([0, i, i + 1])
            
            # 顶面三角形
            for i in range(1, n - 1):
                indices.extend([n, n + i + 1, n + i])
            
            # 侧面
            for i in range(n):
                next_i = (i + 1) % n
                # 每个侧面两个三角形
                indices.extend([i, i + n, next_i])
                indices.extend([next_i, i + n, next_i + n])
            
            # 构建GLTF结构
            gltf = {
                "asset": {
                    "version": "2.0",
                    "generator": "AI创意工坊 3D生成器"
                },
                "scene": 0,
                "scenes": [
                    {
                        "nodes": [0]
                    }
                ],
                "nodes": [
                    {
                        "mesh": 0,
                        "name": model_name
                    }
                ],
                "meshes": [
                    {
                        "primitives": [
                            {
                                "attributes": {
                                    "POSITION": 0
                                },
                                "indices": 1,
                                "material": 0
                            }
                        ]
                    }
                ],
                "accessors": [
                    {
                        "bufferView": 0,
                        "componentType": 5126,  # FLOAT
                        "count": len(vertices) // 3,
                        "type": "VEC3",
                        "max": [max(vertices[::3]), max(vertices[1::3]), max(vertices[2::3])],
                        "min": [min(vertices[::3]), min(vertices[1::3]), min(vertices[2::3])]
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
                "buffers": [
                    {
                        "byteLength": len(vertices) * 4 + len(indices) * 2,
                        "uri": f"data:application/octet-stream;base64,{self._create_buffer_data(vertices, indices)}"
                    }
                ],
                "materials": [
                    {
                        "name": "DefaultMaterial",
                        "pbrMetallicRoughness": {
                            "baseColorFactor": [0.8, 0.6, 0.9, 1.0],  # 淡紫色
                            "metallicFactor": 0.1,
                            "roughnessFactor": 0.8
                        }
                    }
                ]
            }
            
            return json.dumps(gltf, indent=2)
            
        except Exception as e:
            print(f"GLTF生成错误: {str(e)}")
            return self._create_simple_cube_gltf(model_name)
    
    def _create_buffer_data(self, vertices, indices):
        """创建缓冲区数据"""
        import struct
        
        # 将顶点数据转换为字节
        vertex_bytes = struct.pack(f'{len(vertices)}f', *vertices)
        
        # 将索引数据转换为字节
        index_bytes = struct.pack(f'{len(indices)}H', *indices)
        
        # 合并数据
        buffer_data = vertex_bytes + index_bytes
        
        # 转换为base64
        return base64.b64encode(buffer_data).decode('utf-8')
    
    def _create_simple_cube_gltf(self, model_name):
        """创建简单的立方体GLTF模型作为备选"""
        gltf = {
            "asset": {
                "version": "2.0",
                "generator": "AI创意工坊 简单3D生成器"
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0, "name": model_name}],
            "meshes": [{
                "primitives": [{
                    "attributes": {"POSITION": 0},
                    "indices": 1,
                    "material": 0
                }]
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": 8,
                    "type": "VEC3",
                    "max": [0.5, 0.5, 0.5],
                    "min": [-0.5, -0.5, -0.5]
                },
                {
                    "bufferView": 1,
                    "componentType": 5123,
                    "count": 36,
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteLength": 96, "target": 34962},
                {"buffer": 0, "byteOffset": 96, "byteLength": 72, "target": 34963}
            ],
            "buffers": [{
                "byteLength": 168,
                "uri": "data:application/octet-stream;base64,AAC/vwAAvr8AAL6/AAC+vwAAvr8AAL+/AAC/vwAAvr8AAL+/AAC/vwAAvr8AAL6/AAC/vwAAvb8AAL6/AAC/vwAAvb8AAL+/AAC/vwAAvb8AAL+/AAC/vwAAvb8AAL6/AAABAAIAAgADAAAABABFAAUABgAGAEcABAAIAAkACQAKAAgACwAMAAwADQALAA4ADwAPABAADgA="
            }],
            "materials": [{
                "name": "DefaultMaterial",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.7, 0.8, 0.9, 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.9
                }
            }]
        }
        
        return json.dumps(gltf, indent=2)