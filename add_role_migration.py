#!/usr/bin/env python3
"""
添加用户角色字段的数据库迁移脚本
为现有用户设置默认角色为'student'
"""

from app import app
from models import db, User

def add_role_column():
    """为用户表添加role字段并设置默认值"""
    try:
        with app.app_context():
            # 检查role字段是否已存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'role' not in columns:
                print("添加role字段到users表...")
                # 使用SQLAlchemy添加列
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'student'"))
                    conn.commit()
                print("✅ role字段添加成功")
            else:
                print("ℹ️  role字段已存在")
            
            # 为现有用户设置默认角色
            users_without_role = User.query.filter(
                (User.role == None) | (User.role == '')
            ).all()
            
            if users_without_role:
                print(f"为 {len(users_without_role)} 个用户设置默认角色...")
                for user in users_without_role:
                    user.role = 'student'
                
                db.session.commit()
                print("✅ 默认角色设置完成")
            else:
                print("ℹ️  所有用户都已有角色")
                
            print("🎉 数据库迁移完成!")
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    add_role_column()