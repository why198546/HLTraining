"""
数据库迁移脚本：添加权限管理系统
添加字段：
- User.image_token_remaining: 图片生成令牌
- User.is_enrolled: 是否报名上课
创建表：
- CourseProgress: 课程进度追踪
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import CourseProgress, User, db


def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            # 添加新列到 users 表
            print("添加权限管理字段到users表...")
            with db.engine.connect() as conn:
                # 检查列是否已存在
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'image_token_remaining' not in columns:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN image_token_remaining INTEGER DEFAULT 50"))
                    conn.commit()
                    print("  ✓ 添加 image_token_remaining 列")
                else:
                    print("  - image_token_remaining 列已存在")
                
                if 'is_enrolled' not in columns:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN is_enrolled BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("  ✓ 添加 is_enrolled 列")
                else:
                    print("  - is_enrolled 列已存在")
            
            # 创建CourseProgress表
            print("创建CourseProgress表...")
            db.create_all()
            print("  ✓ CourseProgress 表已创建")
            
            # 为现有用户设置默认值
            print("为现有用户设置默认值...")
            users = User.query.all()
            for user in users:
                if user.image_token_remaining is None:
                    user.image_token_remaining = 50
                if user.is_enrolled is None:
                    user.is_enrolled = False
            
            db.session.commit()
            print(f"✓ 迁移成功完成！")
            print(f"  - 更新了 {len(users)} 个用户的权限设置")
            print("  - CourseProgress 表已创建")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
