#!/usr/bin/env python
"""
数据库升级脚本 - 添加缺失的用户表字段
修复 image_token_remaining 和游客系统相关字段
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db

def upgrade():
    """执行数据库升级"""
    app = create_app()
    
    with app.app_context():
        print("🔧 开始数据库升级...")
        
        # 检查现有字段
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"📋 当前users表字段: {columns}")
        
        # 需要添加的字段
        fields_to_add = {
            'image_token_remaining': 'INTEGER DEFAULT 50',
            'is_enrolled': 'BOOLEAN DEFAULT 0',
            'daily_token_amount': 'INTEGER DEFAULT 0',
            'trial_end_date': 'DATETIME',
            'last_token_grant_date': 'DATE',
            'course_type': 'VARCHAR(50)'
        }
        
        with db.engine.connect() as conn:
            for field_name, field_type in fields_to_add.items():
                if field_name not in columns:
                    print(f"📝 添加字段: {field_name} ({field_type})")
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"))
                        conn.commit()
                        print(f"✅ {field_name} 添加成功")
                    except Exception as e:
                        print(f"❌ {field_name} 添加失败: {e}")
                        conn.rollback()
                else:
                    print(f"⏭️ {field_name} 字段已存在，跳过")
        
        print("\n🎉 数据库升级完成！")
        print("\n请验证以下内容：")
        print("1. 访问 http://localhost:5000 检查应用是否正常运行")
        print("2. 登录用户账号查看token显示是否正常")
        print("3. 检查游客试用功能是否正常")

if __name__ == '__main__':
    upgrade()
