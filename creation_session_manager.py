"""
创作会话管理器
管理用户的创作会话，包括版本控制、选择状态等
"""

import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class CreationSessionManager:
    """创作会话管理器"""
    
    def __init__(self, sessions_dir: str = "sessions"):
        """
        初始化会话管理器
        
        Args:
            sessions_dir: 会话数据存储目录
        """
        self.sessions_dir = sessions_dir
        self.sessions = {}  # 内存中的会话缓存
        
        # 确保会话目录存在
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # 加载现有会话
        self._load_sessions()
    
    def _load_sessions(self):
        """从文件系统加载现有会话"""
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # 移除 .json 后缀
                    session_path = os.path.join(self.sessions_dir, filename)
                    with open(session_path, 'r', encoding='utf-8') as f:
                        self.sessions[session_id] = json.load(f)
        except Exception as e:
            print(f"加载会话数据时出错: {e}")
    
    def _save_session(self, session_id: str):
        """保存会话到文件"""
        try:
            session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存会话 {session_id} 时出错: {e}")
    
    def create_session(self, user_info: Dict[str, Any]) -> str:
        """
        创建新的创作会话
        
        Args:
            user_info: 用户信息字典
            
        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            'session_id': session_id,
            'user_info': user_info,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'versions': {
                'original': [],     # 原始图片版本
                'image': [],        # 彩色图片版本
                'figurine': [],     # 手办风格版本
                'model': []         # 3D模型版本
            },
            'selected_versions': {},  # 当前选中的版本
            'metadata': {}
        }
        
        self.sessions[session_id] = session_data
        self._save_session(session_id)
        
        print(f"✅ 创建会话成功: {session_id}")
        return session_id
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict]: 会话信息或None
        """
        return self.sessions.get(session_id)
    
    def get_session_versions(self, session_id: str, version_type: str) -> List[Dict[str, Any]]:
        """
        获取会话中指定类型的版本列表
        
        Args:
            session_id: 会话ID
            version_type: 版本类型 ('original', 'image', 'figurine', 'model')
            
        Returns:
            List[Dict]: 版本列表
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return session.get('versions', {}).get(version_type, [])
    
    def add_version(self, session_id: str, version_type: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加新版本到会话
        
        Args:
            session_id: 会话ID
            version_type: 版本类型
            version_data: 版本数据
            
        Returns:
            Dict: 操作结果
        """
        if session_id not in self.sessions:
            return {'success': False, 'error': '会话不存在'}
        
        # 生成版本ID
        version_id = str(uuid.uuid4())
        version_data['version_id'] = version_id
        version_data['created_at'] = datetime.now().isoformat()
        
        # 添加到会话
        self.sessions[session_id]['versions'][version_type].append(version_data)
        self.sessions[session_id]['updated_at'] = datetime.now().isoformat()
        
        # 保存会话
        self._save_session(session_id)
        
        print(f"✅ 添加版本成功: {session_id} - {version_type} - {version_id}")
        return {
            'success': True,
            'version_id': version_id,
            'version_data': version_data
        }
    
    def select_version(self, session_id: str, version_id: str) -> Dict[str, Any]:
        """
        选择特定版本
        
        Args:
            session_id: 会话ID
            version_id: 版本ID
            
        Returns:
            Dict: 操作结果
        """
        if session_id not in self.sessions:
            return {'success': False, 'error': '会话不存在'}
        
        session = self.sessions[session_id]
        
        # 查找版本
        found_version = None
        found_type = None
        
        for version_type, versions in session['versions'].items():
            for version in versions:
                if version.get('version_id') == version_id:
                    found_version = version
                    found_type = version_type
                    break
            if found_version:
                break
        
        if not found_version:
            return {'success': False, 'error': '版本不存在'}
        
        # 设置选中版本
        session['selected_versions'][found_type] = version_id
        session['updated_at'] = datetime.now().isoformat()
        
        # 保存会话
        self._save_session(session_id)
        
        print(f"✅ 选择版本成功: {session_id} - {found_type} - {version_id}")
        return {
            'success': True,
            'version_type': found_type,
            'version_id': version_id,
            'version_data': found_version
        }
    
    def get_selected_versions(self, session_id: str) -> Dict[str, str]:
        """
        获取当前选中的版本
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict: 选中的版本ID字典
        """
        session = self.sessions.get(session_id)
        if not session:
            return {}
        
        return session.get('selected_versions', {})
    
    def delete_version(self, session_id: str, version_id: str) -> Dict[str, Any]:
        """
        删除版本
        
        Args:
            session_id: 会话ID
            version_id: 版本ID
            
        Returns:
            Dict: 操作结果
        """
        if session_id not in self.sessions:
            return {'success': False, 'error': '会话不存在'}
        
        session = self.sessions[session_id]
        
        # 查找并删除版本
        for version_type, versions in session['versions'].items():
            for i, version in enumerate(versions):
                if version.get('version_id') == version_id:
                    # 删除版本
                    deleted_version = versions.pop(i)
                    
                    # 如果删除的是当前选中版本，清除选择
                    if session['selected_versions'].get(version_type) == version_id:
                        del session['selected_versions'][version_type]
                    
                    session['updated_at'] = datetime.now().isoformat()
                    self._save_session(session_id)
                    
                    print(f"✅ 删除版本成功: {session_id} - {version_type} - {version_id}")
                    return {
                        'success': True,
                        'deleted_version': deleted_version
                    }
        
        return {'success': False, 'error': '版本不存在'}
    
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        关闭会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            Dict: 操作结果
        """
        if session_id not in self.sessions:
            return {'success': False, 'error': '会话不存在'}
        
        # 更新会话状态
        self.sessions[session_id]['status'] = 'closed'
        self.sessions[session_id]['closed_at'] = datetime.now().isoformat()
        self.sessions[session_id]['updated_at'] = datetime.now().isoformat()
        
        # 保存会话
        self._save_session(session_id)
        
        # 从内存中移除（可选）
        # del self.sessions[session_id]
        
        print(f"✅ 关闭会话成功: {session_id}")
        return {'success': True}
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        清理旧会话
        
        Args:
            days: 保留天数
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            created_at = datetime.fromisoformat(session['created_at']).timestamp()
            if created_at < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            # 删除文件
            session_path = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_path):
                os.remove(session_path)
            
            # 从内存中移除
            del self.sessions[session_id]
            print(f"🗑️ 清理旧会话: {session_id}")
        
        if sessions_to_remove:
            print(f"🧹 清理完成，删除 {len(sessions_to_remove)} 个旧会话")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            Dict: 统计信息
        """
        active_sessions = sum(1 for s in self.sessions.values() if s.get('status') == 'active')
        total_sessions = len(self.sessions)
        
        version_counts = {'original': 0, 'image': 0, 'figurine': 0, 'model': 0}
        for session in self.sessions.values():
            for version_type, versions in session.get('versions', {}).items():
                version_counts[version_type] += len(versions)
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'closed_sessions': total_sessions - active_sessions,
            'version_counts': version_counts
        }