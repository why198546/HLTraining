import json
import os
from datetime import datetime
import uuid
import shutil
from typing import List, Dict, Optional

class VersionManager:
    """作品版本管理器，支持图片和3D模型的版本控制和回退"""
    
    def __init__(self, base_folder='static/gallery'):
        self.base_folder = base_folder
        self.versions_file = 'artwork_versions.json'
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.base_folder, exist_ok=True)
    
    def load_versions_data(self) -> List[Dict]:
        """加载版本数据"""
        if os.path.exists(self.versions_file):
            try:
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_versions_data(self, data: List[Dict]):
        """保存版本数据"""
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_version(self, artwork_id: str, image_path: str = None, model_path: str = None, 
                      version_note: str = "", auto_note: str = "") -> Dict:
        """
        创建新版本
        
        Args:
            artwork_id: 作品ID
            image_path: 图片文件路径
            model_path: 3D模型文件路径
            version_note: 用户备注
            auto_note: 自动生成的备注（如AI参数等）
        """
        try:
            version_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # 创建版本目录
            version_dir = os.path.join(self.base_folder, artwork_id, 'versions', version_id)
            os.makedirs(version_dir, exist_ok=True)
            
            # 保存文件
            saved_files = {}
            
            if image_path and os.path.exists(image_path):
                image_filename = f"image_v{version_id}.png"
                image_dest = os.path.join(version_dir, image_filename)
                shutil.copy2(image_path, image_dest)
                saved_files['image'] = f"gallery/{artwork_id}/versions/{version_id}/{image_filename}"
            
            if model_path and os.path.exists(model_path):
                model_filename = f"model_v{version_id}.glb"
                model_dest = os.path.join(version_dir, model_filename)
                shutil.copy2(model_path, model_dest)
                saved_files['model'] = f"gallery/{artwork_id}/versions/{version_id}/{model_filename}"
            
            # 创建版本数据
            version_data = {
                'version_id': version_id,
                'artwork_id': artwork_id,
                'created_at': timestamp.isoformat(),
                'version_note': version_note,
                'auto_note': auto_note,
                'files': saved_files,
                'is_current': False  # 默认不是当前版本
            }
            
            # 加载现有版本数据
            versions_data = self.load_versions_data()
            versions_data.append(version_data)
            
            # 保存版本数据
            self.save_versions_data(versions_data)
            
            return {
                'success': True,
                'version_id': version_id,
                'message': f'版本 {version_id[:8]} 创建成功！'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'创建版本失败: {str(e)}'
            }
    
    def get_artwork_versions(self, artwork_id: str) -> List[Dict]:
        """获取作品的所有版本"""
        versions_data = self.load_versions_data()
        artwork_versions = [v for v in versions_data if v['artwork_id'] == artwork_id]
        
        # 按创建时间排序（最新的在前）
        artwork_versions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return artwork_versions
    
    def set_current_version(self, artwork_id: str, version_id: str) -> Dict:
        """设置当前版本（回退功能）"""
        try:
            versions_data = self.load_versions_data()
            
            # 清除所有当前版本标记
            for version in versions_data:
                if version['artwork_id'] == artwork_id:
                    version['is_current'] = False
            
            # 设置新的当前版本
            target_version = None
            for version in versions_data:
                if version['version_id'] == version_id and version['artwork_id'] == artwork_id:
                    version['is_current'] = True
                    target_version = version
                    break
            
            if not target_version:
                return {
                    'success': False,
                    'error': '版本不存在'
                }
            
            # 复制版本文件到主目录
            artwork_dir = os.path.join(self.base_folder, artwork_id)
            
            if 'image' in target_version['files']:
                src_image = os.path.join(self.base_folder, '..', '..', target_version['files']['image'])
                dest_image = os.path.join(artwork_dir, f"generated_{artwork_id}.png")
                if os.path.exists(src_image):
                    shutil.copy2(src_image, dest_image)
            
            if 'model' in target_version['files']:
                src_model = os.path.join(self.base_folder, '..', '..', target_version['files']['model'])
                dest_model = os.path.join(artwork_dir, f"model_{artwork_id}.glb")
                if os.path.exists(src_model):
                    shutil.copy2(src_model, dest_model)
            
            # 保存版本数据
            self.save_versions_data(versions_data)
            
            return {
                'success': True,
                'message': f'已回退到版本 {version_id[:8]}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'回退失败: {str(e)}'
            }
    
    def get_current_version(self, artwork_id: str) -> Optional[Dict]:
        """获取当前版本"""
        versions_data = self.load_versions_data()
        
        for version in versions_data:
            if version['artwork_id'] == artwork_id and version.get('is_current', False):
                return version
        
        return None
    
    def delete_version(self, artwork_id: str, version_id: str) -> Dict:
        """删除指定版本"""
        try:
            versions_data = self.load_versions_data()
            
            # 查找要删除的版本
            version_to_delete = None
            for i, version in enumerate(versions_data):
                if version['version_id'] == version_id and version['artwork_id'] == artwork_id:
                    version_to_delete = version
                    versions_data.pop(i)
                    break
            
            if not version_to_delete:
                return {
                    'success': False,
                    'error': '版本不存在'
                }
            
            # 检查是否是当前版本
            if version_to_delete.get('is_current', False):
                return {
                    'success': False,
                    'error': '不能删除当前版本，请先切换到其他版本'
                }
            
            # 删除版本文件
            version_dir = os.path.join(self.base_folder, artwork_id, 'versions', version_id)
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            
            # 保存版本数据
            self.save_versions_data(versions_data)
            
            return {
                'success': True,
                'message': f'版本 {version_id[:8]} 已删除'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'删除版本失败: {str(e)}'
            }
    
    def get_version_stats(self, artwork_id: str) -> Dict:
        """获取版本统计信息"""
        versions = self.get_artwork_versions(artwork_id)
        current_version = self.get_current_version(artwork_id)
        
        return {
            'total_versions': len(versions),
            'current_version_id': current_version['version_id'] if current_version else None,
            'latest_version_date': versions[0]['created_at'] if versions else None,
            'has_image_versions': any('image' in v.get('files', {}) for v in versions),
            'has_model_versions': any('model' in v.get('files', {}) for v in versions)
        }