"""
添加tokens_reward字段到courses表
用于记录完成课程后奖励的token数量
"""
import sys
import os

# 动态获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from auth.models import db
from app import create_app

def add_tokens_reward_column():
    """添加tokens_reward字段到courses表"""
    try:
        app = create_app()
        with app.app_context():
            from sqlalchemy import text, inspect
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('courses')]
            
            if 'tokens_reward' not in columns:
                print("📊 正在添加 tokens_reward 列到 courses 表...")
                
                with db.engine.begin() as conn:
                    # 添加列，默认值为0
                    conn.execute(text('ALTER TABLE courses ADD COLUMN tokens_reward INTEGER DEFAULT 0'))
                
                print("✅ tokens_reward 列添加成功！")
            else:
                print("ℹ️  tokens_reward 列已存在，跳过")
                
            # 验证 - 重新创建inspector以获取最新列信息
            from sqlalchemy import inspect as new_inspect
            inspector = new_inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('courses')]
            
            if 'tokens_reward' in columns:
                print("✅ 验证成功：tokens_reward 字段已存在于courses表中")
            else:
                print("❌ 验证失败：tokens_reward 字段未能成功添加")
                
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        raise

if __name__ == '__main__':
    print("=" * 60)
    print("数据库迁移：添加 tokens_reward 字段到 courses 表")
    print("=" * 60)
    add_tokens_reward_column()
    print("=" * 60)
    print("迁移完成")
    print("=" * 60)
