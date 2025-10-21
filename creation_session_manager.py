import json
import os
from datetime import datetime
import uuid
import shutil
from typing import List, Dict, Optional

class CreationSessionManager:
    """创作会话管理器 - 在创作过程中管理版本，方便用户选择"""
    
    def __init__(self, sessions_folder='creation_sessions'):
        self.sessions_folder = sessions_folder
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.sessions_folder, exist_ok=True)
    
    def create_session(self, user_info: Dict = None) -> str:
        """创建新的创作会话"""
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(self.sessions_folder, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'user_info': user_info or {},
            'versions': [],
            'current_step': 'prompt',  # prompt, image_generated, model_generated
            'status': 'active'
        }
        
        self._save_session_data(session_id, session_data)
        return session_id
    
    def add_version(self, session_id: str, version_type: str, file_path: str, 
                   metadata: Dict = None) -> Dict:
        """
        向会话添加新版本
        
        Args:
            session_id: 会话ID
            version_type: 版本类型 ('image' 或 'model')
            file_path: 文件路径
            metadata: 版本元数据（如提示词、参数等）
        """
        try:
            session_data = self._load_session_data(session_id)
            if not session_data:
                return {'success': False, 'error': '会话不存在'}
            
            version_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # 复制文件到会话目录
            session_dir = os.path.join(self.sessions_folder, session_id)
            if version_type == 'image':
                filename = f"image_v{len([v for v in session_data['versions'] if v['type'] == 'image']) + 1}_{version_id[:8]}.png"
            else:  # model
                filename = f"model_v{len([v for v in session_data['versions'] if v['type'] == 'model']) + 1}_{version_id[:8]}.glb"
            
            dest_path = os.path.join(session_dir, filename)
            shutil.copy2(file_path, dest_path)
            
            # 创建版本数据
            version_data = {
                'version_id': version_id,
                'type': version_type,
                'file_path': dest_path,
                'filename': filename,
                'created_at': timestamp.isoformat(),
                'metadata': metadata or {},
                'is_selected': False
            }
            
            session_data['versions'].append(version_data)
            
            # 更新会话状态
            if version_type == 'image':
                session_data['current_step'] = 'image_generated'
            elif version_type == 'model':
                session_data['current_step'] = 'model_generated'
            
            self._save_session_data(session_id, session_data)
            
            return {
                'success': True,
                'version_id': version_id,
                'filename': filename,
                'message': f'{version_type.title()}版本已添加'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'添加版本失败: {str(e)}'}
    
    def select_version(self, session_id: str, version_id: str) -> Dict:
        """选择指定版本作为当前版本"""
        try:
            session_data = self._load_session_data(session_id)
            if not session_data:
                return {'success': False, 'error': '会话不存在'}
            
            # 清除同类型的所有选择状态
            selected_version = None
            for version in session_data['versions']:
                if version['version_id'] == version_id:
                    selected_version = version
                    version['is_selected'] = True
                elif selected_version and version['type'] == selected_version['type']:
                    version['is_selected'] = False
            
            if not selected_version:
                return {'success': False, 'error': '版本不存在'}
            
            self._save_session_data(session_id, session_data)
            
            return {
                'success': True,
                'message': f'{selected_version["type"].title()}版本已选择'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'选择版本失败: {str(e)}'}
    
    def get_session_versions(self, session_id: str, version_type: str = None) -> List[Dict]:
        """获取会话的所有版本"""
        session_data = self._load_session_data(session_id)
        if not session_data:
            return []
        
        versions = session_data['versions']
        if version_type:
            versions = [v for v in versions if v['type'] == version_type]
        
        # 按创建时间排序（最新在前）
        versions.sort(key=lambda x: x['created_at'], reverse=True)
        
        # 转换文件路径为URL路径
        for version in versions:
            version['url_path'] = self._file_path_to_url(version['file_path'])
        
        return versions
    
    def get_selected_versions(self, session_id: str) -> Dict:
        """获取当前选择的版本"""
        session_data = self._load_session_data(session_id)
        if not session_data:
            return {}
        
        selected = {}
        for version in session_data['versions']:
            if version.get('is_selected', False):
                selected[version['type']] = version.copy()
                selected[version['type']]['url_path'] = self._file_path_to_url(version['file_path'])
        
        return selected
    
    def delete_version(self, session_id: str, version_id: str) -> Dict:
        """删除指定版本"""
        try:
            session_data = self._load_session_data(session_id)
            if not session_data:
                return {'success': False, 'error': '会话不存在'}
            
            # 找到要删除的版本
            version_to_delete = None
            for i, version in enumerate(session_data['versions']):
                if version['version_id'] == version_id:
                    version_to_delete = version
                    session_data['versions'].pop(i)
                    break
            
            if not version_to_delete:
                return {'success': False, 'error': '版本不存在'}
            
            # 检查是否是选中的版本
            if version_to_delete.get('is_selected', False):
                return {'success': False, 'error': '不能删除当前选中的版本，请先选择其他版本'}
            
            # 删除文件
            if os.path.exists(version_to_delete['file_path']):
                os.remove(version_to_delete['file_path'])
            
            self._save_session_data(session_id, session_data)
            
            return {
                'success': True,
                'message': f'{version_to_delete["type"].title()}版本已删除'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'删除版本失败: {str(e)}'}
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        session_data = self._load_session_data(session_id)
        if not session_data:
            return None
        
        # 统计版本信息
        image_versions = [v for v in session_data['versions'] if v['type'] == 'image']
        model_versions = [v for v in session_data['versions'] if v['type'] == 'model']
        
        session_data['stats'] = {
            'total_versions': len(session_data['versions']),
            'image_versions': len(image_versions),
            'model_versions': len(model_versions),
            'selected_image': any(v.get('is_selected') for v in image_versions),
            'selected_model': any(v.get('is_selected') for v in model_versions)
        }
        
        return session_data
    
    def close_session(self, session_id: str) -> Dict:
        """关闭会话（标记为完成）"""
        try:
            session_data = self._load_session_data(session_id)
            if not session_data:
                return {'success': False, 'error': '会话不存在'}
            
            session_data['status'] = 'completed'
            session_data['completed_at'] = datetime.now().isoformat()
            
            self._save_session_data(session_id, session_data)
            
            return {'success': True, 'message': '会话已关闭'}
            
        except Exception as e:
            return {'success': False, 'error': f'关闭会话失败: {str(e)}'}
    
    def cleanup_old_sessions(self, days: int = 7) -> Dict:
        """清理旧的会话数据"""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for session_dir in os.listdir(self.sessions_folder):
                session_path = os.path.join(self.sessions_folder, session_dir)
                if os.path.isdir(session_path):
                    session_data = self._load_session_data(session_dir)
                    if session_data:
                        created_at = datetime.fromisoformat(session_data['created_at']).timestamp()
                        if created_at < cutoff_date and session_data.get('status') == 'completed':
                            shutil.rmtree(session_path)
                            cleaned_count += 1
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'message': f'已清理 {cleaned_count} 个旧会话'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'清理失败: {str(e)}'}
    
    def _load_session_data(self, session_id: str) -> Optional[Dict]:
        """加载会话数据"""
        session_file = os.path.join(self.sessions_folder, session_id, 'session.json')
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None
        return None
    
    def _save_session_data(self, session_id: str, data: Dict):
        """保存会话数据"""
        session_dir = os.path.join(self.sessions_folder, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        session_file = os.path.join(session_dir, 'session.json')
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _file_path_to_url(self, file_path: str) -> str:
        """将文件路径转换为URL路径"""
        # 将绝对路径转换为相对于应用根目录的URL路径
        if file_path.startswith(self.sessions_folder):
            return f'/session-files/{file_path}'
        return file_path