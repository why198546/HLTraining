"""添加project_type等新字段到canvas_projects表"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db


def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始添加新字段到canvas_projects表...")
            
            # 获取数据库连接
            connection = db.engine.connect()
            
            # 检查并添加project_type列
            try:
                connection.execute(db.text("""
                    ALTER TABLE canvas_projects 
                    ADD COLUMN project_type VARCHAR(20) DEFAULT 'infinite'
                """))
                print("✓ 添加 project_type 列成功")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    print("- project_type 列已存在，跳过")
                else:
                    raise
            
            # 检查并添加width列
            try:
                connection.execute(db.text("""
                    ALTER TABLE canvas_projects 
                    ADD COLUMN width INTEGER DEFAULT 512
                """))
                print("✓ 添加 width 列成功")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    print("- width 列已存在，跳过")
                else:
                    raise
            
            # 检查并添加height列
            try:
                connection.execute(db.text("""
                    ALTER TABLE canvas_projects 
                    ADD COLUMN height INTEGER DEFAULT 512
                """))
                print("✓ 添加 height 列成功")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    print("- height 列已存在，跳过")
                else:
                    raise
            
            # 检查并添加last_opened_at列
            try:
                connection.execute(db.text("""
                    ALTER TABLE canvas_projects 
                    ADD COLUMN last_opened_at DATETIME
                """))
                print("✓ 添加 last_opened_at 列成功")
            except Exception as e:
                if 'duplicate column name' in str(e).lower():
                    print("- last_opened_at 列已存在，跳过")
                else:
                    raise
            
            connection.commit()
            connection.close()
            
            print("\n✅ 数据库迁移完成！")
            print("\n更新现有记录的project_type...")
            
            # 将现有记录的project_type设为'infinite'
            from auth.models import CanvasProject
            projects = CanvasProject.query.filter(
                CanvasProject.project_type == None
            ).all()
            
            for project in projects:
                project.project_type = 'infinite'
            
            db.session.commit()
            print(f"✓ 更新了 {len(projects)} 条记录")
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
