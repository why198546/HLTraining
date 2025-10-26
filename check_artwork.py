#!/usr/bin/env python3
"""
检查特定作品的详细信息
"""

import sys
sys.path.append('.')

from app import app
from models import db, Artwork

def check_specific_artwork():
    """检查特定作品的详细信息"""
    with app.app_context():
        # 查找这个作品
        artwork = Artwork.query.filter_by(title='AI创作 10-25 19:51').first()
        
        if artwork:
            print(f"📋 作品详细信息:")
            print(f"   ID: {artwork.id}")
            print(f"   会话ID: {artwork.session_id}")
            print(f"   标题: {artwork.title}")
            print(f"   彩色图片文件名: {artwork.colored_image}")
            print(f"   状态: {artwork.status}")
            print(f"   创建时间: {artwork.created_at}")
            
            # 检查预期的文件路径
            expected_dir = f"static/creation_sessions/{artwork.session_id}"
            expected_file = f"{expected_dir}/{artwork.colored_image}"
            print(f"   预期目录: {expected_dir}")
            print(f"   预期文件: {expected_file}")
            
            # 检查文件是否存在
            import os
            if os.path.exists(expected_dir):
                print(f"   ✅ 目录存在")
                if os.path.exists(expected_file):
                    print(f"   ✅ 文件存在")
                else:
                    print(f"   ❌ 文件不存在")
                    # 列出目录内容
                    if os.path.isdir(expected_dir):
                        files = os.listdir(expected_dir)
                        print(f"   目录内容: {files}")
            else:
                print(f"   ❌ 目录不存在")
        else:
            print("❌ 找不到这个作品")

if __name__ == '__main__':
    check_specific_artwork()