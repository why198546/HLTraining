"""验证数据库迁移"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.chdir(project_root)

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import inspect

from app import create_app
from auth.models import db

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    print("✅ Users表所有字段：")
    for col in sorted(columns):
        print(f"  - {col}")
    
    print(f"\n✅ feedback_templates字段存在: {'feedback_templates' in columns}")
