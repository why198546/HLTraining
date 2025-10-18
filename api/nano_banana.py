import requests
import os
import json
import time
from PIL import Image
import base64
import io
import cv2
import numpy as np

class NanoBananaAPI:
    """图像上色API类 - 使用OpenCV实现本地图像处理"""
    
    def __init__(self):
        # 从环境变量获取API密钥，或使用默认值
        self.api_key = os.getenv('NANO_BANANA_API_KEY', 'your-api-key-here')
        self.base_url = 'https://api.nanobanana.com/v1'  # 示例URL，需要替换为实际API地址
        self.upload_folder = 'uploads'
        
        # 预定义的颜色调色板 - 适合儿童的鲜艳颜色
        self.color_palette = [
            [255, 0, 0],    # 红色
            [0, 255, 0],    # 绿色
            [0, 0, 255],    # 蓝色
            [255, 255, 0],  # 黄色
            [255, 0, 255],  # 紫红色
            [0, 255, 255],  # 青色
            [255, 165, 0],  # 橙色
            [255, 192, 203], # 粉色
            [128, 0, 128],  # 紫色
            [0, 128, 0],    # 深绿色
            [255, 20, 147], # 深粉色
            [30, 144, 255], # 道奇蓝
        ]
        
    def _enhance_with_opencv(self, image_path):
        """使用OpenCV进行图像增强和上色"""
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图像: {image_path}")
                return None
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊以减少噪声
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 边缘检测
            edges = cv2.Canny(blurred, 50, 150)
            
            # 创建一个彩色版本
            colored_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # 使用K-means聚类进行颜色量化和着色
            data = colored_img.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means聚类
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            k = min(8, len(self.color_palette))  # 使用8种主要颜色
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # 将聚类中心替换为我们的颜色调色板
            for i in range(k):
                if i < len(self.color_palette):
                    centers[i] = self.color_palette[i]
            
            # 重建图像
            centers = np.uint8(centers)
            colored_data = centers[labels.flatten()]
            colored_result = colored_data.reshape(colored_img.shape)
            
            # 使用边缘信息来增强细节
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            edges_colored = cv2.bitwise_not(edges_colored)
            
            # 结合颜色和边缘
            final_result = cv2.bitwise_and(colored_result, edges_colored)
            
            # 添加一些饱和度增强
            hsv = cv2.cvtColor(final_result, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = hsv[:,:,1] * 1.2  # 增加饱和度
            hsv[:,:,1][hsv[:,:,1] > 255] = 255  # 限制在255以内
            final_result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            return final_result
            
        except Exception as e:
            print(f"OpenCV处理错误: {str(e)}")
            return None
    
    def _apply_cartoon_effect(self, img):
        """应用卡通效果"""
        try:
            # 双边滤波去噪同时保持边缘
            bilateral = cv2.bilateralFilter(img, 15, 80, 80)
            
            # 转换为灰度图用于边缘检测
            gray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY)
            gray_blur = cv2.medianBlur(gray, 5)
            
            # 创建边缘遮罩
            edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            
            # 转换边缘为3通道
            edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 结合颜色和边缘
            cartoon = cv2.bitwise_and(bilateral, edges)
            
            return cartoon
            
        except Exception as e:
            print(f"卡通效果处理错误: {str(e)}")
            return img
    
    def _encode_image_to_base64(self, image_path):
        """将图片编码为base64格式"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码错误: {str(e)}")
            return None
    
    def _save_opencv_image(self, cv_image, filename):
        """保存OpenCV图像到文件"""
        try:
            output_path = os.path.join(self.upload_folder, filename)
            success = cv2.imwrite(output_path, cv_image)
            if success:
                return output_path
            else:
                print(f"保存图片失败: {output_path}")
                return None
        except Exception as e:
            print(f"保存图片错误: {str(e)}")
            return None
    
    def colorize_sketch(self, sketch_path):
        """为手绘简笔画上色 - 使用OpenCV本地处理"""
        try:
            print("正在使用OpenCV进行图片上色...")
            
            # 使用OpenCV处理图像
            colored_img = self._enhance_with_opencv(sketch_path)
            if colored_img is None:
                return None
            
            # 应用卡通效果
            cartoon_img = self._apply_cartoon_effect(colored_img)
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(sketch_path))[0]
            colored_filename = f"{base_name}_colored.png"
            
            # 保存处理后的图像
            result_path = self._save_opencv_image(cartoon_img, colored_filename)
            
            if result_path:
                print(f"图片上色完成: {result_path}")
                return result_path
            else:
                print("保存上色图片失败")
                return None
                
        except Exception as e:
            print(f"图片上色错误: {str(e)}")
            return None
    
    def _apply_figurine_style(self, image_path):
        """应用手办风格效果"""
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # 1. 增强饱和度和亮度
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv[:,:,1] = hsv[:,:,1] * 1.4  # 增加饱和度
            hsv[:,:,1][hsv[:,:,1] > 255] = 255
            hsv[:,:,2] = hsv[:,:,2] * 1.1  # 增加亮度
            hsv[:,:,2][hsv[:,:,2] > 255] = 255
            enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # 2. 应用双边滤波实现光滑的塑料质感
            smooth = cv2.bilateralFilter(enhanced, 15, 100, 100)
            
            # 3. 增强对比度
            lab = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced_contrast = cv2.merge([l, a, b])
            enhanced_contrast = cv2.cvtColor(enhanced_contrast, cv2.COLOR_LAB2BGR)
            
            # 4. 添加边缘增强以模拟立体感
            gray = cv2.cvtColor(enhanced_contrast, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges = cv2.dilate(edges, np.ones((2,2), np.uint8), iterations=1)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 5. 结合增强的颜色和边缘
            figurine_result = cv2.addWeighted(enhanced_contrast, 0.8, edges_colored, 0.2, 0)
            
            return figurine_result
            
        except Exception as e:
            print(f"手办风格处理错误: {str(e)}")
            return None
    
    def generate_figurine_style(self, colored_image_path):
        """生成手办风格图片 - 使用OpenCV本地处理"""
        try:
            print("正在生成手办风格图片...")
            
            # 使用OpenCV应用手办风格
            figurine_img = self._apply_figurine_style(colored_image_path)
            if figurine_img is None:
                return None
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(colored_image_path))[0]
            figurine_filename = f"{base_name}_figurine.png"
            
            # 保存处理后的图像
            result_path = self._save_opencv_image(figurine_img, figurine_filename)
            
            if result_path:
                print(f"手办风格图片生成完成: {result_path}")
                return result_path
            else:
                print("保存手办风格图片失败")
                return None
                
        except Exception as e:
            print(f"手办风格生成错误: {str(e)}")
            return None
    
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