"""添加canvas_projects表的数据库迁移脚本"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db


def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            # 导入模型以确保表结构被注册
            from models.canvas_project import CanvasProject
            
            print("开始创建canvas_projects表...")
            
            # 创建所有表（如果不存在）
            db.create_all()
            
            print("✓ canvas_projects表创建成功！")
            print("\n表结构：")
            print("- id: 主键")
            print("- user_id: 用户ID (外键)")
            print("- title: 项目标题")
            print("- project_type: 项目类型 (sketch/infinite)")
            print("- description: 项目描述")
            print("- thumbnail: 缩略图 (Base64)")
            print("- canvas_data: 画布数据 (JSON)")
            print("- width: 画布宽度")
            print("- height: 画布高度")
            print("- created_at: 创建时间")
            print("- updated_at: 更新时间")
            print("- last_opened_at: 最后打开时间")
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
