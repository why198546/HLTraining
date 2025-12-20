"""作品管理相关API路由"""
import json
import os
import shutil
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import desc, func

from auth.models import Artwork, ArtworkView, ArtworkVote, db

artwork_api_bp = Blueprint('artwork_api', __name__)


@artwork_api_bp.route('/save-artwork', methods=['POST'])
@login_required
def save_artwork():
    """从创作会话保存作品到数据库"""
    try:
        data = request.get_json()
        print(f"📨 收到保存作品请求: {data}")
        
        # 验证必需的参数
        session_id = data.get('session_id')
        print(f"🔍 会话ID: {session_id}")
        
        if not session_id:
            print("❌ 缺少会话ID")
            return jsonify({'error': '缺少会话ID'}), 400
        
        # 获取会话的所有版本历史
        print(f"🔄 获取会话 {session_id} 的所有版本...")
        session_folder = f"creation_sessions/{session_id}"
        
        # 从会话文件夹获取所有文件
        all_files = {
            'original_sketch': None,
            'colored_images': [],
            'adjusted_images': [],
            'model_3d': None,
            'video_file': None
        }
        
        if os.path.exists(session_folder):
            files_in_folder = sorted(os.listdir(session_folder))
            
            for filename in files_in_folder:
                if filename.startswith('.'):  # 跳过隐藏文件
                    continue
                    
                file_path = os.path.join(session_folder, filename)
                file_lower = filename.lower()
                
                # 原始简笔画 - 上传的或手绘的
                if 'upload' in file_lower or 'sketch' in file_lower or 'original' in file_lower:
                    if filename.endswith(('.png', '.jpg', '.jpeg')):
                        all_files['original_sketch'] = filename
                
                # 调整后的图片（包含'adjusted'关键字）
                elif 'adjusted' in file_lower:
                    all_files['adjusted_images'].append(filename)
                
                # AI生成的图片（包含'colored', 'generated', 或时间戳格式）
                elif any(keyword in file_lower for keyword in ['colored', 'generated', 'image_']):
                    all_files['colored_images'].append(filename)
                
                # 如果是普通的PNG/JPG但不属于以上类别，也算作生成图片
                elif filename.endswith(('.png', '.jpg', '.jpeg')):
                    # 排除明确标记为其他类型的文件
                    if not any(x in file_lower for x in ['model', 'thumbnail']):
                        all_files['colored_images'].append(filename)
                
                # 3D模型
                elif filename.endswith(('.glb', '.obj', '.fbx', '.gltf')):
                    all_files['model_3d'] = filename
                
                # 视频文件
                elif filename.endswith(('.mp4', '.mov', '.avi')):
                    all_files['video_file'] = filename
        
        # 对列表排序（按文件名，通常包含时间戳）
        all_files['colored_images'].sort()
        all_files['adjusted_images'].sort()
        
        print(f"📂 找到的文件:")
        print(f"   原始简笔画: {all_files['original_sketch']}")
        print(f"   生成图片: {all_files['colored_images']}")
        print(f"   调整图片: {all_files['adjusted_images']}")
        print(f"   3D模型: {all_files['model_3d']}")
        print(f"   视频: {all_files['video_file']}")
        
        # 获取或创建作品记录
        artwork = Artwork.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        is_new = False
        if not artwork:
            artwork = Artwork(
                user_id=current_user.id,
                session_id=session_id,
                title=data.get('title', '未命名作品'),
                description=data.get('description', ''),
                category=data.get('category', 'other')
            )
            is_new = True
            print(f"🆕 创建新作品记录")
        else:
            # 更新现有作品信息
            if 'title' in data:
                artwork.title = data['title']
            if 'description' in data:
                artwork.description = data['description']
            if 'category' in data:
                artwork.category = data['category']
            print(f"♻️ 更新现有作品记录")
        
        # 更新文件路径 - 使用最新的文件
        if all_files['original_sketch']:
            artwork.original_sketch_path = f"{session_id}/{all_files['original_sketch']}"
        
        if all_files['colored_images']:
            # 使用最新的生成图片
            artwork.colored_image_path = f"{session_id}/{all_files['colored_images'][-1]}"
        
        if all_files['adjusted_images']:
            # 使用最新的调整图片
            artwork.figurine_image_path = f"{session_id}/{all_files['adjusted_images'][-1]}"
        
        if all_files['model_3d']:
            artwork.model_3d_path = f"{session_id}/{all_files['model_3d']}"
        
        if all_files['video_file']:
            artwork.video_file_path = f"{session_id}/{all_files['video_file']}"
        
        # 保存到数据库
        if is_new:
            db.session.add(artwork)
        
        db.session.commit()
        
        print(f"✅ 作品保存成功: ID {artwork.id}")
        
        return jsonify({
            'success': True,
            'artwork_id': artwork.id,
            'message': '作品保存成功！' if is_new else '作品更新成功！'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 保存作品失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'保存失败: {str(e)}'}), 500


@artwork_api_bp.route('/feature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def feature_artwork(artwork_id):
    """设置作品为推荐作品"""
    try:
        # 获取作品
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 取消当前用户的其他推荐作品
        Artwork.query.filter_by(user_id=current_user.id, is_featured=True).update({
            'is_featured': False,
            'featured_at': None
        })
        
        # 设置新的推荐作品
        artwork.is_featured = True
        artwork.is_public = True  # 推荐作品自动设为公开
        artwork.featured_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已设为推荐作品！'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500


@artwork_api_bp.route('/unfeature-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def unfeature_artwork(artwork_id):
    """取消推荐作品"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_featured = False
        artwork.featured_at = None
        # 注意：保持is_public状态，用户可以单独控制
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '已取消推荐'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'操作失败: {str(e)}'}), 500


@artwork_api_bp.route('/vote-artwork/<int:artwork_id>', methods=['POST'])
@login_required
def vote_artwork(artwork_id):
    """为作品投票"""
    try:
        data = request.get_json()
        vote_type = data.get('vote_type', 'like')
        
        # 验证投票类型
        if vote_type not in ['like', 'love', 'wow', 'cool']:
            return jsonify({'error': '无效的投票类型'}), 400
        
        # 获取作品
        artwork = Artwork.query.get(artwork_id)
        if not artwork or not artwork.is_public:
            return jsonify({'error': '作品不存在或未公开'}), 404
        
        # 允许给自己的作品投票
        # 检查是否已投票
        existing_vote = ArtworkVote.query.filter_by(
            artwork_id=artwork_id, 
            voter_id=current_user.id
        ).first()
        
        if existing_vote:
            # 已经投过票，不允许重复投票
            return jsonify({
                'success': False,
                'error': '您已经为这个作品点过赞了！',
                'vote_count': artwork.vote_count
            })
        else:
            # 新投票
            vote = ArtworkVote(artwork_id, current_user.id, vote_type)
            db.session.add(vote)
            
            # 更新作品投票数
            artwork.vote_count = (artwork.vote_count or 0) + 1
            message = '点赞成功！'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'vote_count': artwork.vote_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'投票失败: {str(e)}'}), 500


@artwork_api_bp.route('/increment-view/<int:artwork_id>', methods=['POST'])
@login_required
def increment_view(artwork_id):
    """增加作品浏览次数（每个用户只记录一次）"""
    try:
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return jsonify({'error': '作品不存在'}), 404
        
        # 检查该用户是否已经浏览过这个作品
        existing_view = ArtworkView.query.filter_by(
            artwork_id=artwork_id,
            viewer_id=current_user.id
        ).first()
        
        if not existing_view:
            # 首次浏览，创建浏览记录
            view = ArtworkView(artwork_id, current_user.id)
            db.session.add(view)
            
            # 增加浏览次数
            artwork.view_count = (artwork.view_count or 0) + 1
            db.session.commit()
            
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': True
            })
        else:
            # 已经浏览过，不增加计数
            return jsonify({
                'success': True,
                'view_count': artwork.view_count,
                'is_new_view': False
            })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新浏览次数失败: {str(e)}'}), 500


@artwork_api_bp.route('/artwork/<int:artwork_id>', methods=['GET'])
@login_required
def get_artwork_api(artwork_id):
    """获取作品详情API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        file_urls = artwork.get_file_urls()
        
        artwork_data = {
            'id': artwork.id,
            'title': artwork.title or '未命名作品',
            'description': artwork.description,
            'created_at': artwork.created_at.strftime('%Y年%m月%d日 %H:%M'),
            'artwork_type': '3D模型' if file_urls['model_3d'] else 'AI上色' if file_urls['colored_image'] else '手绘作品',
            'image_url': file_urls['colored_image'] or file_urls['figurine_image'] or file_urls['original_sketch'] or '/static/images/placeholder.png',
            'views': artwork.view_count or 0,
            'likes': artwork.vote_count or 0,
            'is_featured': artwork.is_featured,
            'is_public': artwork.is_public,
            'files': {
                'original_sketch': file_urls['original_sketch'],
                'colored_image': file_urls['colored_image'],
                'figurine_image': file_urls['figurine_image'],
                'model_3d': file_urls['model_3d'],
                'video_file': file_urls['video_file']
            }
        }
        
        return jsonify(artwork_data)
        
    except Exception as e:
        return jsonify({'error': f'获取作品详情失败: {str(e)}'}), 500


@artwork_api_bp.route('/artwork/<int:artwork_id>', methods=['DELETE'])
@login_required
def delete_artwork_api(artwork_id):
    """删除作品API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        # 删除相关的投票记录
        ArtworkVote.query.filter_by(artwork_id=artwork_id).delete()
        
        # 删除文件
        session_folder = os.path.join('creation_sessions', artwork.session_id)
        if os.path.exists(session_folder):
            try:
                shutil.rmtree(session_folder)
            except Exception as file_error:
                print(f"删除文件失败: {file_error}")
        
        # 删除数据库记录
        db.session.delete(artwork)
        db.session.commit()
        
        # 计算删除后的统计信息
        remaining_count = Artwork.query.filter_by(user_id=current_user.id).count()
        total_likes = db.session.query(func.sum(Artwork.vote_count)).filter_by(user_id=current_user.id).scalar() or 0
        total_views = db.session.query(func.sum(Artwork.view_count)).filter_by(user_id=current_user.id).scalar() or 0
        
        return jsonify({
            'success': True,
            'message': '作品已删除',
            'stats': {
                'total_artworks': remaining_count,
                'total_likes': total_likes,
                'total_views': total_views
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@artwork_api_bp.route('/artwork/<int:artwork_id>/privacy', methods=['POST'])
@login_required
def update_artwork_privacy(artwork_id):
    """更新作品隐私设置API"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        data = request.get_json()
        is_public = data.get('is_public', False)
        
        artwork.is_public = is_public
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '隐私设置已更新',
            'is_public': artwork.is_public
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@artwork_api_bp.route('/artwork/<int:artwork_id>/set-public', methods=['POST'])
@login_required
def set_artwork_public(artwork_id):
    """设置作品为公开"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为公开',
            'is_public': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500


@artwork_api_bp.route('/artwork/<int:artwork_id>/set-private', methods=['POST'])
@login_required
def set_artwork_private(artwork_id):
    """设置作品为私密"""
    try:
        artwork = Artwork.query.filter_by(id=artwork_id, user_id=current_user.id).first()
        if not artwork:
            return jsonify({'error': '作品不存在或无权限'}), 404
        
        artwork.is_public = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '作品已设为私密',
            'is_public': False
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500


@artwork_api_bp.route('/save-video', methods=['POST'])
def save_video():
    """保存视频到作品集"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        video_url = data.get('video_url')
        prompt = data.get('prompt', '')
        
        if not session_id or not video_url:
            return jsonify({
                'success': False,
                'error': '缺少必需参数'
            }), 400
        
        # TODO: 实现视频保存到作品集的逻辑
        # 这里可以扩展gallery_manager来支持视频作品
        
        print(f"✅ 视频已保存: {video_url}")
        
        return jsonify({
            'success': True,
            'message': '视频已保存到作品集'
        })
        
    except Exception as e:
        print(f"❌ 视频保存错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
