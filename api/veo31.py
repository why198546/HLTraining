"""
Veo 3.1 视频生成API集成
使用Google Gemini API的Veo 3.1模型
参考文档：https://ai.google.dev/gemini-api/docs/video
"""

import os
import time
import google.genai as genai
from google.genai import types
from typing import Dict, Optional
import base64

class Veo31API:
    """Veo 3.1 视频生成API客户端"""
    
    def __init__(self):
        # 使用Gemini API密钥
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('NANO_BANANA_API_KEY')
        if not self.api_key:
            raise ValueError("未找到GEMINI_API_KEY或NANO_BANANA_API_KEY环境变量")
        
        # 初始化Gemini客户端
        self.client = genai.Client(api_key=self.api_key)
        
        # 存储任务操作（用于轮询）
        self.operations = {}
        
        print("✅ Veo 3.1 API (Google Gemini)初始化成功")
    
    def generate_video(
        self, 
        image_url: str, 
        prompt: str, 
        duration: int = 8,
        aspect_ratio: str = "16:9",
        quality: str = "720p",
        motion_intensity: str = "medium"
    ) -> Dict:
        """
        生成视频（Image-to-Video）
        
        Args:
            image_url: 源图片URL（本地路径或HTTP URL）
            prompt: 视频动作描述
            duration: 视频时长（4/6/8秒）
            aspect_ratio: 宽高比 (16:9 或 9:16)
            quality: 分辨率 (720p 或 1080p)
            motion_intensity: 运动强度 (low/medium/high) - 仅作为提示词参考
            
        Returns:
            包含operation_name的字典
        """
        try:
            print(f"\n🎬 开始使用Veo 3.1生成视频:")
            print(f"   图片: {image_url}")
            print(f"   提示词: {prompt}")
            print(f"   时长: {duration}秒")
            print(f"   宽高比: {aspect_ratio}")
            print(f"   分辨率: {quality}")
            
            # 读取图片并通过Nano Banana重新生成以获得正确的图片对象
            if image_url.startswith('/'):
                # 本地文件路径
                image_path = image_url.lstrip('/')
                if not os.path.exists(image_path):
                    # 尝试添加当前目录
                    image_path = os.path.join(os.getcwd(), image_url.lstrip('/'))
                
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"图片文件不存在: {image_url}")
                
                print(f"   📖 读取图片文件: {image_path}")
            else:
                # HTTP URL - 需要先下载
                import requests
                
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                
                # 保存为临时文件
                image_path = os.path.join('uploads', f'temp_veo_{int(time.time())}.png')
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"   📖 图片已下载并保存: {image_path}")
            
            # 上传图片到Gemini
            print(f"   📤 上传图片到Gemini...")
            
            # 确定MIME类型
            if image_path.lower().endswith('.png'):
                mime_type = 'image/png'
            elif image_path.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            else:
                mime_type = 'image/png'  # 默认
            
            with open(image_path, 'rb') as f:
                uploaded_file = self.client.files.upload(
                    file=f,
                    config=types.UploadFileConfig(mime_type=mime_type)
                )
            print(f"   ✅ 图片已上传: {uploaded_file.name}")
            
            # 删除临时文件
            if 'temp_veo_' in image_path:
                os.remove(image_path)
            
            # 使用Nano Banana重新生成图片以获得正确的图片对象格式
            print(f"   🔄 通过Nano Banana处理图片...")
            result = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[
                    types.Part(file_data=types.FileData(file_uri=uploaded_file.uri)),
                    "Generate an exact copy of this image"
                ]
            )
            
            # 获取生成的图片对象
            image_data = None
            if result.candidates and len(result.candidates) > 0:
                candidate = result.candidates[0]
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = part.inline_data
                            print(f"   ✅ 图片对象已准备 (mime: {image_data.mime_type}, size: {len(image_data.data)} bytes)")
                            break
                    
                    if not image_data:
                        # 调试：打印part结构
                        print(f"   ⚠️  未找到inline_data，检查parts结构:")
                        for i, part in enumerate(candidate.content.parts):
                            print(f"      Part {i}: {type(part)}, 属性: {[attr for attr in dir(part) if not attr.startswith('_')]}")
                        raise Exception("无法从Nano Banana获取图片数据（未找到inline_data）")
                else:
                    raise Exception("返回结果格式不正确（无parts属性）")
            else:
                raise Exception("Nano Banana未返回结果")
            
            # 增强提示词（根据运动强度）
            enhanced_prompt = prompt
            if motion_intensity == "high":
                enhanced_prompt = f"{prompt} The camera moves dynamically with fast, energetic motion."
            elif motion_intensity == "low":
                enhanced_prompt = f"{prompt} The camera moves slowly and gently with minimal motion."
            
            # 确保时长有效（Veo 3.1支持4-8秒）
            valid_durations = [4, 6, 8]
            if duration not in valid_durations:
                # 找到最接近的有效时长
                duration = min(valid_durations, key=lambda x: abs(x - duration))
                print(f"   ⚠️  时长调整为{duration}秒（Veo 3.1支持: {valid_durations}）")
            
            # 调用Veo 3.1 API
            print(f"   🚀 调用Veo 3.1 API...")
            
            # 使用types.Image，接受image_bytes（原始字节）和mime_type
            image_obj = types.Image(
                image_bytes=image_data.data,  # 直接使用原始字节，不需要base64编码
                mime_type=image_data.mime_type
            )
            
            print(f"   📦 Image对象已创建 (mime: {image_data.mime_type}, size: {len(image_data.data)} bytes)")
            
            operation = self.client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt=enhanced_prompt,
                image=image_obj,
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    resolution=quality,
                    duration_seconds=duration,
                )
            )
            
            operation_name = operation.name
            self.operations[operation_name] = operation
            
            print(f"✅ 视频生成任务已创建")
            print(f"   操作ID: {operation_name}")
            
            return {
                'task_id': operation_name,
                'status': 'processing',
                'message': '视频生成中，请稍候...'
            }
            
        except Exception as e:
            print(f"❌ 视频生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"视频生成失败: {str(e)}")
    
    def check_status(self, task_id: str) -> Dict:
        """
        检查视频生成状态
        
        Args:
            task_id: 任务ID（operation name）
            
        Returns:
            包含状态信息的字典
        """
        try:
            # 获取或刷新操作状态
            if task_id in self.operations:
                operation = self.operations[task_id]
            else:
                # 从名称重新获取操作
                operation = types.GenerateVideosOperation(name=task_id)
            
            # 刷新操作状态
            operation = self.client.operations.get(operation)
            self.operations[task_id] = operation
            
            if operation.done:
                # 检查是否成功
                if hasattr(operation, 'error') and operation.error:
                    print(f"❌ 视频生成失败: {operation.error}")
                    return {
                        'status': 'failed',
                        'error': str(operation.error),
                        'message': '视频生成失败'
                    }
                
                # 获取生成的视频
                try:
                    # 检查response和generated_videos
                    if not hasattr(operation, 'response') or not operation.response:
                        print(f"❌ Operation没有response属性")
                        print(f"   Operation属性: {[attr for attr in dir(operation) if not attr.startswith('_')]}")
                        raise Exception("视频生成完成但无法获取结果")
                    
                    if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
                        print(f"❌ Response没有generated_videos或为空")
                        print(f"   Response属性: {[attr for attr in dir(operation.response) if not attr.startswith('_')]}")
                        print(f"   Response内容: {operation.response}")
                        raise Exception("视频生成完成但无法获取视频数据")
                    
                    generated_video = operation.response.generated_videos[0]
                    video_file = generated_video.video
                    
                    # 下载视频到本地
                    video_filename = f"veo_generated_{int(time.time())}.mp4"
                    video_path = os.path.join('uploads', video_filename)
                    
                    # 确保uploads目录存在
                    os.makedirs('uploads', exist_ok=True)
                    
                    # 下载视频
                    print(f"📥 下载视频到: {video_path}")
                    
                    with open(video_path, 'wb') as f:
                        # download方法返回的是一个迭代器，每个chunk可能是int或bytes
                        total_bytes = 0
                        
                        for chunk in self.client.files.download(file=video_file):
                            # 确保chunk是bytes类型
                            if isinstance(chunk, bytes):
                                f.write(chunk)
                                total_bytes += len(chunk)
                            elif isinstance(chunk, int):
                                # 单个字节，转换为bytes
                                f.write(bytes([chunk]))
                                total_bytes += 1
                        
                        print(f"✅ 视频下载完成: {total_bytes / (1024*1024):.2f} MB")
                    
                    video_url = f"/uploads/{video_filename}"
                    
                    print(f"✅ 视频已生成: {video_url}")
                    
                    return {
                        'status': 'completed',
                        'progress': 100,
                        'video_url': video_url,
                        'message': '视频生成完成！'
                    }
                    
                except Exception as e:
                    print(f"❌ 处理视频结果失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    return {
                        'status': 'failed',
                        'error': str(e),
                        'message': '无法获取生成的视频'
                    }
            else:
                # 还在处理中
                print(f"⏳ 视频生成中...")
                return {
                    'status': 'processing',
                    'progress': 50,  # 无法获取精确进度，使用固定值
                    'message': '视频生成中，请稍候...'
                }
                
        except Exception as e:
            print(f"❌ 状态检查失败: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'message': '状态检查失败'
            }
    
    def get_video_url(self, task_id: str) -> Optional[str]:
        """
        获取生成的视频URL
        
        Args:
            task_id: 任务ID
            
        Returns:
            视频URL或None
        """
        status_result = self.check_status(task_id)
        
        if status_result.get('status') == 'completed':
            return status_result.get('video_url')
        
        return None


# 全局实例
veo_api = None

def get_veo_api() -> Veo31API:
    """获取Veo API实例（单例模式）"""
    global veo_api
    if veo_api is None:
        veo_api = Veo31API()
    return veo_api


# 测试函数
def test_veo_api():
    """测试Veo API连接"""
    try:
        api = get_veo_api()
        print("✅ Veo 3.1 API初始化成功")
        print(f"   API Key: {api.api_key[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Veo 3.1 API初始化失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 测试API
    test_veo_api()
