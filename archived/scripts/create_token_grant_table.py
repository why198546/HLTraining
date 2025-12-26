"""创建token_grant_logs表"""
import sys
sys.path.insert(0, '/Users/hongyuwang/code/HLTraining')

from app import create_app
from auth.models import db, TokenGrantLog

app = create_app()

with app.app_context():
    # 创建token_grant_logs表
    db.create_all()
    print("✅ token_grant_logs表创建成功！")
    
    # 验证表是否创建
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'token_grant_logs' in tables:
        print("✅ 表已存在于数据库中")
        
        # 显示表结构
        columns = inspector.get_columns('token_grant_logs')
        print("\n表结构：")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("❌ 表创建失败")
