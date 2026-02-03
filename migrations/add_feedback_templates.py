"""
数据库迁移脚本：为User表添加feedback_templates字段
执行方式：python migrations/add_feedback_templates.py
"""

import os
import sys

# 确保可以导入项目模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.chdir(project_root)

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from auth.models import db


def migrate():
    """添加feedback_templates字段到users表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'feedback_templates' not in columns:
                print("🔧 开始迁移：添加feedback_templates字段...")
                
                # 添加字段
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        ALTER TABLE users 
                        ADD COLUMN feedback_templates JSON NULL
                    """))
                    conn.commit()
                
                print("✅ 迁移完成：feedback_templates字段已添加")
            else:
                print("ℹ️  字段已存在，无需迁移")
                
        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
