#!/usr/bin/env python3
"""
修复缺失文件的作品
"""

import sys
sys.path.append('.')

from app import app
from models import db, Artwork

def fix_missing_files():
    """修复缺失文件的作品"""
    with app.app_context():
        print("🔧 修复缺失文件的作品...")
        
        # 查找这个有问题的作品
        artwork = Artwork.query.filter_by(title='AI创作 10-25 19:51').first()
        
        if artwork:
            print(f"📋 处理作品: {artwork.title}")
            
            # 检查文件是否存在
            import os
            expected_dir = f"static/creation_sessions/{artwork.session_id}"
            expected_file = f"{expected_dir}/{artwork.colored_image}"
            
            if not os.path.exists(expected_file):
                print(f"   ❌ 文件不存在: {expected_file}")
                print(f"   🔄 设置为不公开显示...")
                
                # 设置为不公开
                artwork.is_public = False
                db.session.commit()
                
                print(f"   ✅ 已设置为不公开显示")
            else:
                print(f"   ✅ 文件存在，无需处理")
        
        # 检查所有作品的文件完整性
        print(f"\n🔍 检查所有作品的文件完整性...")
        all_artworks = Artwork.query.filter_by(is_public=True).all()
        fixed_count = 0
        
        for artwork in all_artworks:
            file_urls = artwork.get_file_urls()
            has_valid_file = False
            
            # 检查彩色图片
            if artwork.colored_image:
                file_path = f"static/creation_sessions/{artwork.session_id}/{artwork.colored_image}"
                if os.path.exists(file_path):
                    has_valid_file = True
            
            # 检查手办图片
            if artwork.figurine_image:
                file_path = f"static/creation_sessions/{artwork.session_id}/{artwork.figurine_image}"
                if os.path.exists(file_path):
                    has_valid_file = True
            
            # 检查原始简笔画
            if artwork.original_sketch:
                file_path = f"static/creation_sessions/{artwork.session_id}/{artwork.original_sketch}"
                if os.path.exists(file_path):
                    has_valid_file = True
            
            if not has_valid_file:
                print(f"   ❌ 作品 '{artwork.title}' 没有有效文件，设置为不公开")
                artwork.is_public = False
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"\n✅ 修复完成，共处理 {fixed_count} 个问题作品")
        else:
            print(f"\n✅ 所有公开作品的文件都正常")
        
        # 统计最终结果
        public_artworks = Artwork.query.filter_by(is_public=True).count()
        total_artworks = Artwork.query.count()
        print(f"\n📊 最终统计:")
        print(f"   公开作品: {public_artworks}")
        print(f"   总作品数: {total_artworks}")

if __name__ == '__main__':
    fix_missing_files()