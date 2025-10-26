#!/usr/bin/env python3
"""
将JSON文件中的作品迁移到数据库
"""

import sys
import os
import json
from datetime import datetime
sys.path.append('.')

from app import app
from models import db, Artwork, User

def migrate_artworks_from_json():
    """从JSON文件迁移作品到数据库"""
    with app.app_context():
        print("🔄 开始从JSON文件迁移作品到数据库...")
        
        # 读取JSON备份文件
        json_file = 'gallery_data.json.backup'
        if not os.path.exists(json_file):
            print(f"❌ 找不到文件: {json_file}")
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            artworks_data = json.load(f)
        
        print(f"📊 找到 {len(artworks_data)} 个作品需要迁移")
        
        # 获取默认用户（如果没有用户，创建一个默认用户）
        default_user = User.query.filter_by(username='王洪宇').first()
        if not default_user:
            # 查找任何现有用户
            default_user = User.query.first()
            if not default_user:
                print("❌ 数据库中没有用户，请先创建用户账户")
                return
        
        print(f"👤 使用用户: {default_user.nickname} (ID: {default_user.id})")
        
        migrated_count = 0
        skipped_count = 0
        
        for artwork_data in artworks_data:
            # 检查是否已存在（根据原JSON的ID作为session_id）
            session_id = artwork_data['id']
            existing = Artwork.query.filter_by(session_id=session_id).first()
            
            if existing:
                print(f"⏭️  跳过已存在的作品: {artwork_data['title']} (ID: {session_id})")
                skipped_count += 1
                continue
            
            # 解析创建时间
            created_at = datetime.fromisoformat(artwork_data['created_at'])
            
            # 创建新的作品记录
            artwork = Artwork(
                session_id=session_id,
                title=artwork_data['title'],
                user_id=default_user.id
            )
            
            # 设置基本信息
            artwork.description = artwork_data.get('description', '')
            artwork.status = 'completed'
            artwork.is_public = True
            artwork.created_at = created_at
            
            # 设置分类
            category_map = {
                'characters': 'characters',
                'animals': 'animals', 
                'objects': 'objects',
                'nature': 'nature'
            }
            artwork.style_type = category_map.get(artwork_data.get('category'), 'other')
            
            # 设置文件路径（从gallery路径转换为creation_sessions路径）
            if artwork_data.get('generated_image'):
                # 从 "gallery/xxx/generated_xxx.png" 转换为 "generated_xxx.png"
                image_path = artwork_data['generated_image']
                if image_path.startswith('gallery/'):
                    filename = os.path.basename(image_path)
                    artwork.colored_image = filename
                    
                    # 复制文件到新的路径结构
                    old_path = f"static/{image_path}"
                    new_dir = f"static/creation_sessions/{session_id}"
                    new_path = f"{new_dir}/{filename}"
                    
                    # 创建目录
                    os.makedirs(new_dir, exist_ok=True)
                    
                    # 复制文件（如果源文件存在）
                    if os.path.exists(old_path):
                        import shutil
                        shutil.copy2(old_path, new_path)
                        print(f"📁 复制图片: {old_path} → {new_path}")
                    else:
                        print(f"⚠️  源图片文件不存在: {old_path}")
            
            # 设置3D模型文件
            if artwork_data.get('model_file'):
                model_path = artwork_data['model_file']
                if model_path.startswith('gallery/'):
                    filename = os.path.basename(model_path)
                    artwork.model_3d = filename
                    
                    # 复制3D模型文件
                    old_path = f"static/{model_path}"
                    new_dir = f"static/creation_sessions/{session_id}"
                    new_path = f"{new_dir}/{filename}"
                    
                    if os.path.exists(old_path):
                        import shutil
                        shutil.copy2(old_path, new_path)
                        print(f"🎯 复制3D模型: {old_path} → {new_path}")
                    else:
                        print(f"⚠️  源3D模型文件不存在: {old_path}")
            
            # 设置统计数据
            artwork.view_count = artwork_data.get('views', 0)
            artwork.vote_count = artwork_data.get('likes', 0)
            
            # 保存到数据库
            db.session.add(artwork)
            print(f"✅ 迁移作品: {artwork.title} (类型: {artwork.style_type})")
            migrated_count += 1
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"\n🎉 迁移完成!")
            print(f"✅ 成功迁移: {migrated_count} 个作品")
            print(f"⏭️  跳过重复: {skipped_count} 个作品")
            
            # 验证迁移结果
            total_artworks = Artwork.query.count()
            public_artworks = Artwork.query.filter_by(is_public=True).count()
            print(f"📊 数据库中总作品数: {total_artworks}")
            print(f"🌐 公开作品数: {public_artworks}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 迁移失败: {str(e)}")

if __name__ == '__main__':
    migrate_artworks_from_json()