"""
数据库迁移：添加游客系统和每日token赠送功能
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

from app import create_app
from auth.models import User, db


def migrate():
    app = create_app()
    
    with app.app_context():
        print("开始数据库迁移：添加游客系统字段...")
        
        # 添加新字段
        try:
            # 1. 每日token赠送数量（游客10，正式学生30，未报名学生0，教师和管理员不需要）
            db.session.execute('ALTER TABLE users ADD COLUMN daily_token_amount INTEGER DEFAULT 0')
            print("✓ 添加字段: daily_token_amount")
        except Exception as e:
            print(f"字段 daily_token_amount 可能已存在: {e}")
        
        try:
            # 2. 试用结束日期（游客有7天试用期）
            db.session.execute('ALTER TABLE users ADD COLUMN trial_end_date DATETIME')
            print("✓ 添加字段: trial_end_date")
        except Exception as e:
            print(f"字段 trial_end_date 可能已存在: {e}")
        
        try:
            # 3. 上次token赠送日期（用于判断是否需要今日赠送）
            db.session.execute('ALTER TABLE users ADD COLUMN last_token_grant_date DATE')
            print("✓ 添加字段: last_token_grant_date")
        except Exception as e:
            print(f"字段 last_token_grant_date 可能已存在: {e}")
        
        try:
            # 4. 课程类型（用于记录通过哪个二维码注册）
            db.session.execute('ALTER TABLE users ADD COLUMN course_type VARCHAR(50)')
            print("✓ 添加字段: course_type")
        except Exception as e:
            print(f"字段 course_type 可能已存在: {e}")
        
        db.session.commit()
        print("\n数据迁移完成！")
        
        # 更新现有用户的数据
        print("\n更新现有用户数据...")
        users = User.query.all()
        for user in users:
            # 根据角色设置每日token数量
            if user.role == 'teacher' or user.role == 'admin':
                user.daily_token_amount = 0  # 教师和管理员无限制
            elif user.role == 'student':
                if user.is_enrolled:
                    user.daily_token_amount = 30  # 正式学生每天30
                else:
                    user.daily_token_amount = 0   # 未报名学生不赠送
            elif user.role == 'visitor':
                user.daily_token_amount = 10  # 游客每天10
                if not user.trial_end_date:
                    user.trial_end_date = datetime.now() + timedelta(days=7)
            else:
                user.daily_token_amount = 0
        
        db.session.commit()
        print(f"✓ 更新了 {len(users)} 个用户的数据")
        
        print("\n迁移完成！")
        print("\n角色说明：")
        print("- visitor: 游客（自行注册，每天10 token，7天试用）")
        print("- student（未报名）: 体验课学生（+50 token）")
        print("- student（已报名）: 正式学生（每天30 token，可用3D+视频）")
        print("- teacher: 教师（无限token）")
        print("- admin: 管理员（管理一切）")

if __name__ == '__main__':
    migrate()
