"""
混元3D模型生成器 - 使用腾讯云AI3D服务
专为儿童AI培训网站设计，支持图片转3D模型功能
"""

import base64
import json
import os
import time
import uuid

import requests
from dotenv import load_dotenv
from PIL import Image
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import \
    TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

# 加载环境变量
load_dotenv()


class Hunyuan3DGenerator:
    def __init__(self):
        # 确保models文件夹存在（改为uploads/3d_models）
        self.models_folder = "uploads/3d_models"
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder, exist_ok=True)
            print(f"✅ 创建模型目录: {self.models_folder}")
        
        # 初始化腾讯云客户端
        self._init_tencent_client()
    
    def _init_tencent_client(self):
        """初始化腾讯云AI3D客户端"""
        try:
            print("🔧 初始化腾讯云AI3D客户端...")
            
            # 尝试导入AI3D模块
            try:
                from tencentcloud.ai3d.v20250513 import ai3d_client, models
                self.ai3d_client = ai3d_client
                self.models = models
                print("✅ AI3D SDK模块导入成功")
            except ImportError:
                print("⚠️ 腾讯云AI3D SDK未安装，请运行: pip install tencentcloud-sdk-python-ai3d")
                self.client = None
                return
            
            # 使用环境变量凭据（推荐方式）
            try:
                cred = credential.EnvironmentVariableCredential().get_credential()
                print("✅ 使用环境变量凭据")
            except Exception:
                # 如果环境变量凭据不可用，尝试直接从环境变量读取
                secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
                secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
                
                print(f"🔑 读取密钥: ID={'已设置' if secret_id else '未设置'}, KEY={'已设置' if secret_key else '未设置'}")
                
                if not secret_id or not secret_key:
                    print("⚠️ 未找到腾讯云密钥，请设置TENCENTCLOUD_SECRET_ID和TENCENTCLOUD_SECRET_KEY环境变量")
                    print("📖 运行以下命令配置: .\\setup-3d-api.ps1")
                    self.client = None
                    return
                
                cred = credential.Credential(secret_id, secret_key)
                print("✅ 使用直接凭据")
            
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
    
    def generate_3d_model(self, image_path, session_id=None, version_number=1, api_version='rapid'):
        """从2D图片生成3D模型，始终返回统一的dict结构
        
        Returns:
            { 'success': True, 'model_path': str, 'stl_path': Optional[str] }
            { 'success': False, 'error': str }
        """
        try:
            print("🎯 开始生成3D模型...")
            
            # 检查AI3D API是否可用
            if not self.client:
                raise Exception("腾讯云AI3D服务未配置，请联系管理员设置API密钥")
            
            # 根据版本选择不同的API
            if api_version == 'pro':
                print("📌 使用专业版API（质量更高，速度较慢）")
                model_paths = self._generate_with_ai3d_pro_api(image_path, session_id, version_number)
            else:
                print("📌 使用极速版API（速度更快）")
                model_paths = self._generate_with_ai3d_api(image_path, session_id, version_number)
            
            if model_paths:
                return {
                    'success': True,
                    'model_path': model_paths.get('glb_path'),
                    'stl_path': model_paths.get('stl_path')
                }
            
            # API调用失败
            return {
                'success': False,
                'error': "3D模型生成服务暂时不可用，请稍后重试"
            }
            
        except Exception as e:
            print(f"❌ 3D模型生成错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_with_ai3d_api(self, image_path, session_id=None, version_number=1):
        """使用腾讯云AI3D极速版API生成3D模型（单图模式）"""
        try:
            print("🚀 调用腾讯云AI3D极速版API...")
            print(f"📁 输入图片: {image_path}")
            
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                print("❌ AI3D客户端未初始化")
                return None
            
            print("✅ 客户端状态: 正常")
            
            # 读取并编码图片
            print("📷 正在编码图片...")
            image_base64 = self._encode_image_to_base64(image_path)
            if not image_base64:
                print("❌ 图片编码失败")
                return None
            
            print(f"✅ 图片编码成功 (大小: {len(image_base64)} 字节)")
            
            # 创建请求对象（使用极速版API - 更快更稳定）
            print("📝 创建API请求（极速版）...")
            req = self.models.SubmitHunyuanTo3DRapidJobRequest()
            params = {
                "ImageBase64": image_base64,
                "ResultFormat": "GLB"  # 生成GLB格式，适合Web预览（支持：OBJ，GLB，STL，USDZ，FBX，MP4）
            }
            req.from_json_string(json.dumps(params))
            
            # 提交3D生成任务
            print("📤 提交3D生成任务到腾讯云（极速版）...")
            resp = self.client.SubmitHunyuanTo3DRapidJob(req)
            result = json.loads(resp.to_json_string())
            
            print(f"📥 API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'JobId' in result:
                job_id = result['JobId']
                print(f"✅ 任务提交成功，JobId: {job_id}")
                
                # 轮询任务状态（使用极速版的查询接口）
                model_url = self._poll_rapid_job_status(job_id)
                if model_url:
                    # 下载模型文件
                    return self._download_3d_model(model_url, image_path, session_id, version_number)
                else:
                    print("❌ 任务状态轮询失败")
            else:
                print(f"❌ API响应中没有JobId")
            
            return None
            
        except TencentCloudSDKException as e:
            print(f"❌ 腾讯云SDK异常:")
            print(f"   错误码: {e.get_code()}")
            print(f"   错误信息: {e.get_message()}")
            print(f"   请求ID: {e.get_request_id()}")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")
            import traceback
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            return None
    
    def _generate_with_ai3d_pro_api(self, image_path, session_id=None, version_number=1):
        """使用腾讯云AI3D专业版API生成3D模型（单图模式）"""
        try:
            print("🚀 调用腾讯云AI3D专业版API...")
            print(f"📁 输入图片: {image_path}")
            
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                print("❌ AI3D客户端未初始化")
                return None
            
            print("✅ 客户端状态: 正常")
            
            # 读取并编码图片
            print("📷 正在编码图片...")
            image_base64 = self._encode_image_to_base64(image_path)
            if not image_base64:
                print("❌ 图片编码失败")
                return None
            
            print(f"✅ 图片编码成功 (大小: {len(image_base64)} 字节)")
            
            # 创建请求对象（使用Pro API）
            print("📝 创建API请求（专业版）...")
            req = self.models.SubmitHunyuanTo3DProJobRequest()
            params = {
                "ImageBase64": image_base64,
                "ResultFormat": "GLB"  # 生成GLB格式，适合Web预览
            }
            req.from_json_string(json.dumps(params))
            
            # 提交3D生成任务
            print("📤 提交3D生成任务到腾讯云（专业版）...")
            resp = self.client.SubmitHunyuanTo3DProJob(req)
            result = json.loads(resp.to_json_string())
            
            print(f"📥 API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'JobId' in result:
                job_id = result['JobId']
                print(f"✅ 任务提交成功，JobId: {job_id}")
                
                # 轮询任务状态（使用Pro版本的查询接口）
                model_url = self._poll_pro_job_status(job_id)
                if model_url:
                    # 下载模型文件
                    return self._download_3d_model(model_url, image_path, session_id, version_number)
                else:
                    print("❌ 任务状态轮询失败")
            else:
                print(f"❌ API响应中没有JobId")
            
            return None
            
        except TencentCloudSDKException as e:
            print(f"❌ 腾讯云SDK异常:")
            print(f"   错误码: {e.get_code()}")
            print(f"   错误信息: {e.get_message()}")
            print(f"   请求ID: {e.get_request_id()}")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")
            import traceback
            print(f"堆栈跟踪:\n{traceback.format_exc()}")
            return None
    
    def generate_3d_model_multi_view(self, view_images):
        """从多视角图片生成3D模型（使用专业版API）
        
        Args:
            view_images: dict with keys 'front', 'back', 'left', 'right'
        
        Returns:
            str: 3D模型文件路径
        """
        try:
            print("🎯 开始生成3D模型（多视角模式）...")
            
            # 检查AI3D API是否可用
            if not self.client:
                raise Exception("❌ 腾讯云AI3D服务不可用，请检查API密钥配置")
            
            # 使用腾讯云AI3D Pro API生成3D模型
            model_path = self._generate_with_ai3d_pro_multi_view_api(view_images)
            if model_path:
                return model_path
            
            # API调用失败，抛出错误
            raise Exception("❌ 腾讯云AI3D Pro服务调用失败，请稍后重试")
            
        except Exception as e:
            print(f"❌ 多视角3D模型生成错误: {str(e)}")
            raise e
    
    def _generate_with_ai3d_pro_multi_view_api(self, view_images):
        """使用腾讯云AI3D Pro API生成3D模型（多视角）"""
        try:
            print("🚀 调用腾讯云AI3D Pro API（多视角）...")
            
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                raise Exception("AI3D客户端未初始化")
            
            # 准备ViewImages数组
            view_images_array = []
            view_type_mapping = {
                'front': 'Front',
                'back': 'Back',
                'left': 'Left',
                'right': 'Right'
            }
            
            # 获取服务器地址用于构建图片URL
            # 假设图片已经在uploads文件夹中，可以通过HTTP访问
            base_url = "http://127.0.0.1:8088"  # 根据实际服务器地址调整
            
            for view_key, view_type in view_type_mapping.items():
                image_path = view_images.get(view_key)
                if not image_path:
                    raise Exception(f"缺少{view_key}视角图片")
                
                # 将本地路径转换为URL
                # image_path格式: uploads/view_front_xxx.png
                if image_path.startswith('uploads/'):
                    image_url = f"{base_url}/{image_path}"
                elif image_path.startswith('/uploads/'):
                    image_url = f"{base_url}{image_path}"
                else:
                    image_url = f"{base_url}/uploads/{os.path.basename(image_path)}"
                
                view_images_array.append({
                    "ViewType": view_type,
                    "ImageUrl": image_url
                })
            
            print(f"✅ 已准备{len(view_images_array)}个视角的图片")
            print(f"📝 ViewImages: {view_images_array}")
            
            # 创建请求对象（专业版）
            req = self.models.SubmitHunyuanTo3DProJobRequest()
            params = {
                "ViewImages": view_images_array,
                "ResultFormat": "GLB"  # 生成GLB格式，适合Web预览
            }
            req.from_json_string(json.dumps(params))
            
            # 提交3D生成任务
            resp = self.client.SubmitHunyuanTo3DProJob(req)
            result = json.loads(resp.to_json_string())
            
            if 'JobId' in result:
                job_id = result['JobId']
                print(f"✅ 多视角3D生成任务已提交，JobId: {job_id}")
                
                # 轮询任务状态（使用Pro版本的查询接口）
                model_url = self._poll_pro_job_status(job_id)
                if model_url:
                    # 下载模型文件
                    return self._download_3d_model(model_url, view_images['front'])
            
            return None
            
        except TencentCloudSDKException as e:
            print(f"❌ 腾讯云SDK错误: {e}")
            return None
        except Exception as e:
            print(f"❌ AI3D Pro API调用错误: {str(e)}")
            return None
    
    def _poll_pro_job_status(self, job_id, max_attempts=30):
        """轮询专业版任务状态"""
        try:
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                raise Exception("AI3D客户端未初始化")
            
            for attempt in range(max_attempts):
                print(f"⏳ 检查任务状态... ({attempt + 1}/{max_attempts})")
                
                # 查询任务状态（专业版）
                req = self.models.QueryHunyuanTo3DProJobRequest()
                params = {"JobId": job_id}
                req.from_json_string(json.dumps(params))
                
                resp = self.client.QueryHunyuanTo3DProJob(req)
                result = json.loads(resp.to_json_string())
                
                if 'Status' in result:
                    status = result['Status']
                    print(f"📊 任务状态: {status}")
                    
                    if status in ['SUCCESS', 'DONE']:
                        # 打印完整的结果用于调试
                        print(f"🔍 完整API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        
                        # 检查是否有模型文件
                        result_files = result.get('ResultFile3Ds', [])
                        if result_files:
                            model_url = result_files[0].get('Url', '')
                            print(f"🎉 3D模型生成完成: {model_url}")
                            return model_url
                        else:
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
    
    def _poll_rapid_job_status(self, job_id, max_attempts=30):
        """轮询极速版任务状态"""
        try:
            # 检查客户端和模型是否可用
            if not self.client or not hasattr(self, 'models'):
                raise Exception("AI3D客户端未初始化")
            
            for attempt in range(max_attempts):
                print(f"⏳ 检查任务状态... ({attempt + 1}/{max_attempts})")
                
                # 查询任务状态（极速版）
                req = self.models.QueryHunyuanTo3DRapidJobRequest()
                params = {"JobId": job_id}
                req.from_json_string(json.dumps(params))
                
                resp = self.client.QueryHunyuanTo3DRapidJob(req)
                result = json.loads(resp.to_json_string())
                
                if 'Status' in result:
                    status = result['Status']
                    print(f"📊 任务状态: {status}")
                    
                    if status in ['SUCCESS', 'DONE']:
                        # 打印完整的结果用于调试
                        print(f"🔍 完整API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        
                        # 检查是否有模型文件
                        result_files = result.get('ResultFile3Ds', [])
                        if result_files:
                            model_url = result_files[0].get('Url', '')
                            print(f"🎉 3D模型生成完成（极速版）: {model_url}")
                            return model_url
                        else:
                            model_url = result.get('ModelUrl', '')
                            if model_url:
                                print(f"🎉 3D模型生成完成（极速版）: {model_url}")
                                return model_url
                            else:
                                print("❌ 3D模型生成完成但未找到下载链接")
                                return None
                    elif status in ['FAILED', 'ERROR']:
                        error_msg = result.get('ErrorMessage', '生成失败')
                        print(f"❌ 3D模型生成失败: {error_msg}")
                        return None
                    elif status in ['PROCESSING', 'PENDING', 'RUN', 'RUNNING', 'WAIT']:
                        time.sleep(10)  # 等待10秒后重试
                        continue
                
                time.sleep(5)  # 短暂等待
            
            print("⏰ 任务查询超时")
            return None
            
        except Exception as e:
            print(f"❌ 任务状态查询错误: {str(e)}")
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
    
    def _download_3d_model(self, model_url, image_path, session_id=None, version_number=1):
        """下载3D模型文件并生成STL版本用于3D打印
        
        Returns dict: {'glb_path': str, 'stl_path': Optional[str]}
        """
        try:
            print(f"📥 下载3D模型...")
            
            response = requests.get(model_url, timeout=60)
            if response.status_code == 200:
                # 生成文件名
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                unique_id = str(uuid.uuid4())[:8]
                
                # 统一保存到uploads/3d_models，便于静态访问
                save_dir = self.models_folder
                # 保留session信息在文件名中以防冲突
                session_suffix = f"_{session_id}" if session_id else ""
                glb_filename = f"model_v{version_number}{session_suffix}_{unique_id}.glb"
                print(f"💾 保存到目录: {save_dir}")
                
                # 确保目录存在
                os.makedirs(save_dir, exist_ok=True)
                
                # 检查文件头，判断是ZIP还是GLB
                content = response.content
                is_zip = content[:2] == b'PK'
                
                if is_zip:
                    print("🔍 检测到ZIP文件，开始解压...")
                    import io
                    import zipfile

                    # 创建临时ZIP文件对象
                    zip_data = io.BytesIO(content)
                    
                    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                        # 列出ZIP中的文件
                        file_list = zip_ref.namelist()
                        print(f"📦 ZIP文件内容: {file_list}")
                        
                        # 优先查找GLB文件
                        glb_file = None
                        obj_file = None
                        mtl_file = None
                        texture_files = []
                        
                        for filename in file_list:
                            if filename.endswith('.glb'):
                                glb_file = filename
                            elif filename.endswith('.obj'):
                                obj_file = filename
                            elif filename.endswith('.mtl'):
                                mtl_file = filename
                            elif filename.endswith(('.png', '.jpg', '.jpeg')):
                                texture_files.append(filename)
                        
                        if glb_file:
                            print(f"✅ 找到GLB文件: {glb_file}")
                            # 提取GLB文件
                            glb_data = zip_ref.read(glb_file)
                            glb_path = os.path.join(save_dir, glb_filename)
                            
                            with open(glb_path, 'wb') as f:
                                f.write(glb_data)
                            
                            print(f"✅ GLB模型解压完成: {glb_path}")
                        elif obj_file:
                            print(f"✅ 找到OBJ文件: {obj_file}")
                            print(f"📦 相关文件: MTL={mtl_file}, 纹理={texture_files}")
                            
                            # 创建临时目录解压所有OBJ相关文件
                            import tempfile
                            temp_dir = tempfile.mkdtemp()
                            
                            # 解压OBJ及其依赖文件
                            zip_ref.extract(obj_file, temp_dir)
                            if mtl_file:
                                zip_ref.extract(mtl_file, temp_dir)
                            for tex_file in texture_files:
                                zip_ref.extract(tex_file, temp_dir)
                            
                            obj_path = os.path.join(temp_dir, obj_file)
                            print(f"🔄 正在将OBJ转换为GLB格式...")
                            
                            # 使用trimesh将OBJ转换为GLB
                            try:
                                import trimesh
                                mesh = trimesh.load(obj_path, force='mesh')
                                
                                # 保存为GLB
                                glb_path = os.path.join(save_dir, glb_filename)
                                mesh.export(glb_path, file_type='glb')
                                print(f"✅ OBJ→GLB转换完成: {glb_path}")
                                
                                # 清理临时文件
                                import shutil
                                shutil.rmtree(temp_dir)
                            except ImportError:
                                print("❌ 需要安装trimesh库: pip install trimesh")
                                import shutil
                                shutil.rmtree(temp_dir)
                                return None
                            except Exception as conv_err:
                                print(f"❌ OBJ转换失败: {str(conv_err)}")
                                import shutil
                                shutil.rmtree(temp_dir)
                                return None
                        else:
                            print(f"❌ ZIP中未找到GLB或OBJ文件，文件列表: {file_list}")
                            return None
                else:
                    # 直接保存GLB文件（Web预览用）
                    glb_path = os.path.join(save_dir, glb_filename)
                    
                    with open(glb_path, 'wb') as f:
                        f.write(content)
                    
                    print(f"✅ GLB模型下载完成: {glb_path}")
                
                # 尝试生成STL版本用于3D打印
                stl_path = self._convert_glb_to_stl(glb_path)
                if stl_path:
                    print(f"✅ STL模型生成完成: {stl_path}")
                
                return {
                    'glb_path': glb_path,
                    'stl_path': stl_path
                }
                
            else:
                print(f"❌ 模型下载失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 模型下载错误: {str(e)}")
            return None
    def _convert_glb_to_stl(self, glb_path):
        """将GLB模型转换为STL格式用于3D打印"""
        try:
            import trimesh
            
            print(f"🔄 开始GLB→STL转换: {glb_path}")
            
            # 加载GLB模型
            mesh = trimesh.load(glb_path)
            print(f"✅ GLB模型加载成功，面数: {len(mesh.faces) if hasattr(mesh, 'faces') else 'N/A'}")
            
            # 生成STL文件路径
            stl_path = glb_path.replace('.glb', '.stl')
            
            # 导出为STL
            mesh.export(stl_path)
            
            # 验证文件是否生成
            if os.path.exists(stl_path):
                file_size = os.path.getsize(stl_path)
                print(f"✅ STL文件生成成功: {stl_path} ({file_size} bytes)")
                return stl_path
            else:
                print(f"❌ STL文件未生成: {stl_path}")
                return None
            
        except ImportError:
            print("⚠️  trimesh未安装，无法生成STL文件。运行: pip install trimesh")
            return None
        except Exception as e:
            print(f"⚠️  GLB转STL失败: {str(e)}")
            import traceback
            traceback.print_exc()
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