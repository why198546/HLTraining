#!/usr/bin/env python
"""
数据库迁移管理脚本
使用Flask-Migrate管理数据库结构变更
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hltraining.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 导入数据库模型
from auth.models import db, User, Artwork, CreationSession

# 初始化数据库和迁移
db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    print("数据库迁移管理工具已初始化")
    print(f"数据库: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\n可用命令:")
    print("  flask db init          # 初始化迁移仓库（仅首次使用）")
    print("  flask db migrate -m '' # 生成迁移脚本")
    print("  flask db upgrade       # 应用迁移到数据库")
    print("  flask db downgrade     # 回滚迁移")
    print("  flask db current       # 查看当前版本")
    print("  flask db history       # 查看迁移历史")
