#!/usr/bin/env python3
"""
创建松果币消耗记录表
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db, TokenUsageLog

def create_token_usage_log_table():
    """创建token_usage_logs表"""
    app = create_app()
    
    with app.app_context():
        # 创建表
        db.create_all()
        print("✅ TokenUsageLog表创建成功")

if __name__ == '__main__':
    create_token_usage_log_table()
