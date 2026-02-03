"""
添加module_templates字段到User模型
用于存储教师自定义的模块级提示词模板
"""
import sys
import os

# 动态获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from auth.models import db, User
from app import create_app

def add_module_templates_column():
    """添加module_templates字段"""
    try:
        app = create_app()
        with app.app_context():
            # 使用SQLAlchemy的原生方式检查列是否存在
            from sqlalchemy import text, inspect
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'module_templates' not in columns:
                print("📊 正在添加 module_templates 列...")
                
                # SQLite不支持ADD COLUMN IF NOT EXISTS，但我们已经检查过了
                with db.engine.begin() as conn:
                    conn.execute(text('ALTER TABLE users ADD COLUMN module_templates TEXT'))
                
                print("✅ module_templates 列添加成功！")
            else:
                print("ℹ️  module_templates 列已存在，跳过")
                
            # 验证 - 重新创建inspector以获取最新列信息
            from sqlalchemy import inspect as new_inspect
            inspector = new_inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'module_templates' in columns:
                print("✅ 验证成功：module_templates 字段已存在于数据库中")
            else:
                print("❌ 验证失败：module_templates 字段未能成功添加")
                
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        raise

if __name__ == '__main__':
    print("=" * 60)
    print("数据库迁移：添加 module_templates 字段")
    print("=" * 60)
    add_module_templates_column()
    print("=" * 60)
    print("迁移完成")
    print("=" * 60)
