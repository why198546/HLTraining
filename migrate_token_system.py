#!/usr/bin/env python
"""
数据库迁移脚本 - 添加月度充值和过期币相关的表
"""
import os
import sys
import sqlite3
from pathlib import Path

# 确保脚本可以导入项目模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from app import create_app
from auth.models import db, MonthlyTokenGrant, TokenExpiry

def migrate_database():
    """创建新的数据库表"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 开始数据库迁移...")
            
            # 创建新表
            db.create_all()
            
            print("✅ 数据库迁移成功！")
            print("\n已创建的新表：")
            print("  - monthly_token_grants: 月度充值记录表")
            print("  - token_expiries: 过期币追踪表")
            
            # 显示表结构
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'monthly_token_grants' in tables:
                print("\n✓ monthly_token_grants 表结构：")
                for col in inspector.get_columns('monthly_token_grants'):
                    print(f"    - {col['name']}: {col['type']}")
            
            if 'token_expiries' in tables:
                print("\n✓ token_expiries 表结构：")
                for col in inspector.get_columns('token_expiries'):
                    print(f"    - {col['name']}: {col['type']}")
            
            print("\n📝 迁移说明：")
            print("  1. 教师和管理员每月1日自动获得1000松果币（不过期）")
            print("  2. 游客通过二维码获得的币在30天内未使用会失效")
            print("  3. 系统每天凌晨1:00检查过期币并清除")
            print("  4. 系统每月1日凌晨2:00为教师/管理员自动充值")
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
