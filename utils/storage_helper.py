"""
存储助手 - 统一本地存储和OSS存储接口
根据配置自动选择存储方式
"""
import os
import shutil
from datetime import datetime
from .oss_storage import oss_storage

class StorageHelper:
    def __init__(self, use_oss=None):
        """
        初始化存储助手
        
        Args:
            use_oss: 是否使用OSS，None表示根据环境变量自动判断
        """
        if use_oss is None:
            self.use_oss = os.getenv('USE_OSS_STORAGE', 'false').lower() == 'true'
        else:
            self.use_oss = use_oss
        
        self.oss_available = oss_storage is not None
        
        # 如果配置使用OSS但OSS不可用，回退到本地存储
        if self.use_oss and not self.oss_available:
            print("警告: OSS配置不可用，回退到本地存储")
            self.use_oss = False
    
    def save_file(self, local_path, storage_path, keep_local=False):
        """
        保存文件
        
        Args:
            local_path: 本地文件路径
            storage_path: 存储路径（相对路径，如 gallery/xxx/image.png）
            keep_local: 是否保留本地副本
            
        Returns:
            dict: {
                'success': bool,
                'url': str,  # 访问URL
                'storage_path': str,  # 存储路径
                'storage_type': 'oss' or 'local'
            }
        """
        if self.use_oss:
            # 上传到OSS
            result = oss_storage.upload_file(local_path, storage_path)
            
            if result['success']:
                # 如果不保留本地文件，则删除
                if not keep_local and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                    except:
                        pass
                
                return {
                    'success': True,
                    'url': result['url'],
                    'storage_path': storage_path,
                    'storage_type': 'oss'
                }
            else:
                # OSS上传失败，回退到本地存储
                print(f"OSS上传失败: {result.get('error')}，使用本地存储")
                return self._save_local(local_path, storage_path)
        else:
            # 使用本地存储
            return self._save_local(local_path, storage_path)
    
    def _save_local(self, local_path, storage_path):
        """保存到本地存储"""
        try:
            # 构建完整的本地路径
            full_path = os.path.join('static', storage_path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 如果源文件和目标文件不同，则复制
            if os.path.abspath(local_path) != os.path.abspath(full_path):
                shutil.copy2(local_path, full_path)
            
            # 生成访问URL
            url = f'/static/{storage_path}'
            
            return {
                'success': True,
                'url': url,
                'storage_path': storage_path,
                'storage_type': 'local'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'storage_type': 'local'
            }
    
    def save_bytes(self, data, storage_path, content_type='application/octet-stream'):
        """
        保存字节数据
        
        Args:
            data: 字节数据
            storage_path: 存储路径
            content_type: MIME类型
            
        Returns:
            dict: 保存结果
        """
        if self.use_oss:
            result = oss_storage.upload_bytes(data, storage_path, content_type)
            if result['success']:
                return {
                    'success': True,
                    'url': result['url'],
                    'storage_path': storage_path,
                    'storage_type': 'oss'
                }
            else:
                print(f"OSS上传失败: {result.get('error')}，使用本地存储")
                return self._save_bytes_local(data, storage_path)
        else:
            return self._save_bytes_local(data, storage_path)
    
    def _save_bytes_local(self, data, storage_path):
        """保存字节数据到本地"""
        try:
            full_path = os.path.join('static', storage_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'wb') as f:
                f.write(data)
            
            return {
                'success': True,
                'url': f'/static/{storage_path}',
                'storage_path': storage_path,
                'storage_type': 'local'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'storage_type': 'local'
            }
    
    def get_file_url(self, storage_path):
        """
        获取文件访问URL
        
        Args:
            storage_path: 存储路径
            
        Returns:
            str: 访问URL
        """
        if self.use_oss:
            return oss_storage.get_file_url(storage_path)
        else:
            return f'/static/{storage_path}'
    
    def delete_file(self, storage_path):
        """
        删除文件
        
        Args:
            storage_path: 存储路径
            
        Returns:
            dict: 删除结果
        """
        if self.use_oss:
            return oss_storage.delete_file(storage_path)
        else:
            try:
                full_path = os.path.join('static', storage_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def file_exists(self, storage_path):
        """
        检查文件是否存在
        
        Args:
            storage_path: 存储路径
            
        Returns:
            bool: 是否存在
        """
        if self.use_oss:
            return oss_storage.file_exists(storage_path)
        else:
            full_path = os.path.join('static', storage_path)
            return os.path.exists(full_path)


# 创建全局实例
storage_helper = StorageHelper()
