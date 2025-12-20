"""会话管理API路由 - 创作会话和版本管理"""
from flask import Blueprint, jsonify, request

from managers.creation_session_manager import CreationSessionManager

session_api_bp = Blueprint('session_api', __name__)

# 初始化managers
session_manager = CreationSessionManager()


@session_api_bp.route('/create-session', methods=['POST'])
def create_session():
    """创建新的创作会话"""
    try:
        user_info = request.get_json() or {}
        session_id = session_manager.create_session(user_info)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': '创作会话已创建'
        })
        
    except Exception as e:
        return jsonify({'error': f'创建会话失败: {str(e)}'}), 500


@session_api_bp.route('/session/<session_id>/info')
def get_session_info(session_id):
    """获取会话信息"""
    try:
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            return jsonify({'error': '会话不存在'}), 404
        
        return jsonify({
            'success': True,
            'session': session_info
        })
        
    except Exception as e:
        return jsonify({'error': f'获取会话信息失败: {str(e)}'}), 500


@session_api_bp.route('/session/<session_id>/versions')
def get_session_versions(session_id):
    """获取会话的所有版本"""
    try:
        version_type = request.args.get('type')  # 'image' 或 'model'
        versions = session_manager.get_session_versions(session_id, version_type)
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        return jsonify({'error': f'获取版本失败: {str(e)}'}), 500


@session_api_bp.route('/session/<session_id>/selected-versions')
def get_selected_versions(session_id):
    """获取当前选择的版本"""
    try:
        selected = session_manager.get_selected_versions(session_id)
        
        return jsonify({
            'success': True,
            'selected': selected
        })
        
    except Exception as e:
        return jsonify({'error': f'获取选择版本失败: {str(e)}'}), 500


@session_api_bp.route('/session/<session_id>/select-version', methods=['POST'])
def select_version(session_id):
    """选择版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.select_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'选择版本失败: {str(e)}'}), 500


@session_api_bp.route('/session/<session_id>/delete-version', methods=['DELETE'])
def delete_version(session_id):
    """删除版本"""
    try:
        data = request.get_json()
        version_id = data.get('version_id')
        
        if not version_id:
            return jsonify({'error': '缺少版本ID'}), 400
        
        result = session_manager.delete_version(session_id, version_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'删除版本失败: {str(e)}'}), 500
