#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除没有生成图片的作品项目
"""

from app import app, db
from models import Artwork
import os

def cleanup_empty_artworks():
    """清除没有任何图片的作品"""
    with app.app_context():
        # 查找没有任何图片的作品
        empty_artworks = Artwork.query.filter(
            db.and_(
                Artwork.colored_image.is_(None),
                Artwork.figurine_image.is_(None),
                Artwork.model_3d.is_(None),
                Artwork.video_file.is_(None)
            )
        ).all()
        
        print(f"\n📊 找到 {len(empty_artworks)} 个没有生成图片的作品")
        
        if not empty_artworks:
            print("✅ 没有需要清除的空作品")
            return
        
        # 显示要删除的作品列表
        print("\n将要删除的作品:")
        for artwork in empty_artworks:
            print(f"  - ID: {artwork.id}, 标题: {artwork.title}, "
                  f"Session: {artwork.session_id}, 创建时间: {artwork.created_at}, "
                  f"用户ID: {artwork.user_id}")
        
        # 确认删除
        confirm = input(f"\n⚠️  确认删除这 {len(empty_artworks)} 个空作品? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ 取消删除操作")
            return
        
        # 执行删除
        deleted_count = 0
        for artwork in empty_artworks:
            try:
                # 删除可能存在的原始简笔画文件
                if artwork.original_sketch and os.path.exists(artwork.original_sketch):
                    os.remove(artwork.original_sketch)
                    print(f"  🗑️  删除文件: {artwork.original_sketch}")
                
                db.session.delete(artwork)
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除作品 {artwork.id} 失败: {str(e)}")
        
        # 提交事务
        try:
            db.session.commit()
            print(f"\n✅ 成功删除 {deleted_count} 个空作品")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 删除失败: {str(e)}")

def cleanup_empty_artworks_auto():
    """自动清除没有任何图片的作品（不需要确认）"""
    with app.app_context():
        # 查找没有任何图片的作品
        empty_artworks = Artwork.query.filter(
            db.and_(
                Artwork.colored_image.is_(None),
                Artwork.figurine_image.is_(None),
                Artwork.model_3d.is_(None),
                Artwork.video_file.is_(None)
            )
        ).all()
        
        print(f"\n📊 找到 {len(empty_artworks)} 个没有生成图片的作品")
        
        if not empty_artworks:
            print("✅ 没有需要清除的空作品")
            return 0
        
        # 执行删除
        deleted_count = 0
        for artwork in empty_artworks:
            try:
                # 删除可能存在的原始简笔画文件
                if artwork.original_sketch and os.path.exists(artwork.original_sketch):
                    os.remove(artwork.original_sketch)
                
                db.session.delete(artwork)
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除作品 {artwork.id} 失败: {str(e)}")
        
        # 提交事务
        try:
            db.session.commit()
            print(f"✅ 成功删除 {deleted_count} 个空作品")
            return deleted_count
        except Exception as e:
            db.session.rollback()
            print(f"❌ 删除失败: {str(e)}")
            return 0

if __name__ == '__main__':
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自动模式，不需要确认
        cleanup_empty_artworks_auto()
    else:
        # 交互模式，需要确认
        cleanup_empty_artworks()
