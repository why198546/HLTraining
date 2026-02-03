"""
添加feedback_templates字段到users表
用于存储教师自定义的AI点评模板
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db
import sqlalchemy as sa

def upgrade():
    """添加feedback_templates字段"""
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = sa.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'feedback_templates' in columns:
                print('✓ feedback_templates字段已存在，无需添加')
                return
            
            # 添加新字段
            with db.engine.connect() as conn:
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN feedback_templates JSON NULL
                '''))
                conn.commit()
            
            print('✓ 成功添加 feedback_templates 字段到 users 表')
            
        except Exception as e:
            print(f'✗ 迁移失败: {e}')
            raise

def downgrade():
    """删除feedback_templates字段"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    DROP COLUMN feedback_templates
                '''))
                conn.commit()
            
            print('✓ 成功删除 feedback_templates 字段')
            
        except Exception as e:
            print(f'✗ 回滚失败: {e}')
            raise

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
