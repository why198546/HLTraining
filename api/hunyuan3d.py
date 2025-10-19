"""
混元3D模型生成器 - 使用腾讯云AI3D服务
专为儿童AI培训网站设计，支持图片转3D模型功能
"""

import os
import base64
import json
import uuid
import time
import requests
from PIL import Image
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

class Hunyuan3DGenerator:
    def __init__(self):
        # 确保models文件夹存在
        self.models_folder = "models"
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
            print(f"✅ 创建模型目录: {self.models_folder}")
        
        # 初始化腾讯云客户端
        self._init_tencent_client()
    
    def _init_tencent_client(self):
        """初始化腾讯云AI3D客户端"""
        try:
            # 尝试导入AI3D模块
            try:
                from tencentcloud.ai3d.v20250513 import ai3d_client, models
                self.ai3d_client = ai3d_client
                self.models = models
            except ImportError:
                print("⚠️ 腾讯云AI3D SDK未安装，请运行: pip install tencentcloud-sdk-python-ai3d")
                self.client = None
                return
            
            # 使用环境变量凭据（推荐方式）
            try:
                cred = credential.EnvironmentVariableCredential().get_credential()
            except Exception:
                # 如果环境变量凭据不可用，尝试直接从环境变量读取
                secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
                secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
                
                if not secret_id or not secret_key:
                    print("⚠️ 未找到腾讯云密钥，请设置TENCENTCLOUD_SECRET_ID和TENCENTCLOUD_SECRET_KEY环境变量")
                    self.client = None
                    return
                
                cred = credential.Credential(secret_id, secret_key)
            
            # 实例化HTTP选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ai3d.tencentcloudapi.com"
            
            # 实例化client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 实例化AI3D客户端
            self.client = self.ai3d_client.Ai3dClient(cred, "ap-guangzhou", clientProfile)
            
            print("✅ 腾讯云AI3D客户端初始化成功")
            
        except Exception as e:
            print(f"❌ 腾讯云客户端初始化失败: {str(e)}")
            self.client = None
    
    def generate_3d_model(self, image_path):
        """从2D图片生成3D模型"""
        try:
            print("🎯 开始生成3D模型...")
            
            # 检查AI3D API是否可用
            if not self.client:
                raise Exception("❌ 腾讯云AI3D服务不可用，请检查API密钥配置")
            
            # 使用腾讯云AI3D API生成3D模型
            model_path = self._generate_with_ai3d_api(image_path)
            if model_path:
                return model_path
            
            # API调用失败，抛出错误
            raise Exception("❌ 腾讯云AI3D服务调用失败，请稍后重试")
            
        except Exception as e:
            print(f"❌ 3D模型生成错误: {str(e)}")
            raise e
    
    def _generate_with_ai3d_api(self, image_path):
        """使用腾讯云AI3D API生成3D模型"""
        try:
            print("🚀 调用腾讯云AI3D API...")
            
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                raise Exception("AI3D客户端未初始化")
            
            # 读取并编码图片
            image_base64 = self._encode_image_to_base64(image_path)
            if not image_base64:
                return None
            
            # 创建请求对象
            req = self.models.SubmitHunyuanTo3DJobRequest()
            params = {
                "ImageBase64": image_base64,
                "ResultFormat": "GLB"  # 生成模型的格式：OBJ，GLB，STL，USDZ，FBX，MP4
            }
            req.from_json_string(json.dumps(params))
            
            # 提交3D生成任务
            resp = self.client.SubmitHunyuanTo3DJob(req)
            result = json.loads(resp.to_json_string())
            
            if 'JobId' in result:
                job_id = result['JobId']
                print(f"✅ 3D生成任务已提交，JobId: {job_id}")
                
                # 轮询任务状态
                model_url = self._poll_job_status(job_id)
                if model_url:
                    # 下载模型文件
                    return self._download_3d_model(model_url, image_path)
            
            return None
            
        except TencentCloudSDKException as e:
            print(f"❌ 腾讯云SDK错误: {e}")
            return None
        except Exception as e:
            print(f"❌ AI3D API调用错误: {str(e)}")
            return None
    
    def _poll_job_status(self, job_id, max_attempts=30):
        """轮询任务状态"""
        try:
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                raise Exception("AI3D客户端未初始化")
            
            for attempt in range(max_attempts):
                print(f"⏳ 检查任务状态... ({attempt + 1}/{max_attempts})")
                
                # 查询任务状态
                req = self.models.QueryHunyuanTo3DJobRequest()
                params = {"JobId": job_id}
                req.from_json_string(json.dumps(params))
                
                resp = self.client.QueryHunyuanTo3DJob(req)
                result = json.loads(resp.to_json_string())
                
                if 'Status' in result:
                    status = result['Status']
                    print(f"📊 任务状态: {status}")
                    
                    if status in ['SUCCESS', 'DONE']:  # 修复：添加DONE状态
                        # 检查是否有模型文件
                        result_files = result.get('ResultFile3Ds', [])
                        if result_files:
                            model_url = result_files[0].get('Url', '')
                            print(f"🎉 3D模型生成完成: {model_url}")
                            return model_url
                        else:
                            # 尝试旧的字段名
                            model_url = result.get('ModelUrl', '')
                            if model_url:
                                print(f"🎉 3D模型生成完成: {model_url}")
                                return model_url
                            else:
                                print("❌ 3D模型生成完成但未找到下载链接")
                                return None
                    elif status in ['FAILED', 'ERROR']:
                        error_msg = result.get('ErrorMessage', '生成失败')
                        print(f"❌ 3D模型生成失败: {error_msg}")
                        return None
                    elif status in ['PROCESSING', 'PENDING', 'RUN', 'RUNNING']:
                        time.sleep(10)  # 等待10秒后重试
                        continue
                
                time.sleep(5)  # 短暂等待
            
            print("⏰ 任务查询超时")
            return None
            
        except Exception as e:
            print(f"❌ 任务状态查询错误: {str(e)}")
            return None
    
    def _download_3d_model(self, model_url, image_path):
        """下载GLB格式的3D模型文件"""
        try:
            print(f"📥 下载GLB格式3D模型...")
            
            response = requests.get(model_url, timeout=60)
            if response.status_code == 200:
                # 生成文件名
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                unique_id = str(uuid.uuid4())[:8]
                
                # 直接保存为GLB文件
                glb_filename = f"{base_name}_ai3d_{unique_id}.glb"
                glb_path = os.path.join(self.models_folder, glb_filename)
                
                with open(glb_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ GLB模型下载完成: {glb_path}")
                return glb_path
                
            else:
                print(f"❌ 模型下载失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 模型下载错误: {str(e)}")
            return None
    def _encode_image_to_base64(self, image_path):
        """将图片编码为base64格式"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ 图片编码错误: {str(e)}")
            return None


# 向后兼容的别名
Simple3DGenerator = Hunyuan3DGenerator