"""
阿里云OSS存储服务
用于将用户上传的文件和生成的图片、3D模型存储到OSS
"""
import oss2
import os
from datetime import datetime
from dotenv import load_dotenv
import mimetypes

load_dotenv()

class OSSStorage:
    def __init__(self):
        """初始化OSS连接"""
        self.access_key_id = os.getenv('ALIYUN_OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIYUN_OSS_ACCESS_KEY_SECRET')
        self.endpoint = os.getenv('ALIYUN_OSS_ENDPOINT')
        self.bucket_name = os.getenv('ALIYUN_OSS_BUCKET_NAME')
        self.cdn_domain = os.getenv('ALIYUN_OSS_CDN_DOMAIN')  # 可选的CDN域名
        
        if not all([self.access_key_id, self.access_key_secret, self.endpoint, self.bucket_name]):
            raise ValueError("OSS配置不完整，请检查环境变量")
        
        # 创建认证对象
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        
        # 创建Bucket对象
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        
    def upload_file(self, local_path, oss_path, content_type=None):
        """
        上传文件到OSS
        
        Args:
            local_path: 本地文件路径
            oss_path: OSS上的存储路径（例如: gallery/xxx.png）
            content_type: 文件MIME类型，如果不指定则自动检测
            
        Returns:
            dict: {
                'success': bool,
                'url': str,  # 文件访问URL
                'oss_path': str,  # OSS存储路径
                'error': str  # 错误信息（如果失败）
            }
        """
        try:
            if not os.path.exists(local_path):
                return {
                    'success': False,
                    'error': f'本地文件不存在: {local_path}'
                }
            
            # 自动检测Content-Type
            if not content_type:
                content_type, _ = mimetypes.guess_type(local_path)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # 上传文件
            with open(local_path, 'rb') as f:
                result = self.bucket.put_object(
                    oss_path, 
                    f,
                    headers={'Content-Type': content_type}
                )
            
            # 生成访问URL
            url = self.get_file_url(oss_path)
            
            return {
                'success': True,
                'url': url,
                'oss_path': oss_path,
                'size': os.path.getsize(local_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_bytes(self, data, oss_path, content_type='application/octet-stream'):
        """
        上传字节数据到OSS
        
        Args:
            data: 字节数据
            oss_path: OSS存储路径
            content_type: MIME类型
            
        Returns:
            dict: 上传结果
        """
        try:
            result = self.bucket.put_object(
                oss_path,
                data,
                headers={'Content-Type': content_type}
            )
            
            url = self.get_file_url(oss_path)
            
            return {
                'success': True,
                'url': url,
                'oss_path': oss_path,
                'size': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_file(self, oss_path, local_path):
        """
        从OSS下载文件到本地
        
        Args:
            oss_path: OSS文件路径
            local_path: 本地保存路径
            
        Returns:
            dict: 下载结果
        """
        try:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 下载文件
            self.bucket.get_object_to_file(oss_path, local_path)
            
            return {
                'success': True,
                'local_path': local_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, oss_path):
        """
        删除OSS上的文件
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            dict: 删除结果
        """
        try:
            self.bucket.delete_object(oss_path)
            return {
                'success': True,
                'oss_path': oss_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def file_exists(self, oss_path):
        """
        检查文件是否存在
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            bool: 是否存在
        """
        try:
            return self.bucket.object_exists(oss_path)
        except:
            return False
    
    def get_file_url(self, oss_path):
        """
        获取文件访问URL
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            str: 访问URL
        """
        # 如果配置了CDN域名，使用CDN
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{oss_path}"
        else:
            # 使用OSS默认域名
            return f"https://{self.bucket_name}.{self.endpoint}/{oss_path}"
    
    def get_file_info(self, oss_path):
        """
        获取文件信息
        
        Args:
            oss_path: OSS文件路径
            
        Returns:
            dict: 文件信息
        """
        try:
            meta = self.bucket.get_object_meta(oss_path)
            return {
                'success': True,
                'size': meta.headers.get('Content-Length'),
                'content_type': meta.headers.get('Content-Type'),
                'last_modified': meta.headers.get('Last-Modified')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_files(self, prefix='', max_keys=100):
        """
        列出指定前缀的文件
        
        Args:
            prefix: 路径前缀
            max_keys: 最大返回数量
            
        Returns:
            list: 文件列表
        """
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=max_keys):
                files.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified
                })
            return {
                'success': True,
                'files': files
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 创建全局实例
try:
    oss_storage = OSSStorage()
except Exception as e:
    print(f"OSS初始化失败: {e}")
    oss_storage = None
