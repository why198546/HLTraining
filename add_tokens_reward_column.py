#!/usr/bin/env python
"""
添加 tokens_reward 列到 courses 表
解决：sqlalchemy.exc.OperationalError: no such column: courses.tokens_reward
"""

import os
import sqlite3
from pathlib import Path

def add_tokens_reward_column():
    """添加 tokens_reward 列到 courses 表"""
    
    # 找到数据库文件
    db_path = None
    possible_paths = [
        'instance/hltraining.db',
        'instance/app.db',
        'hltraining.db',
        'app.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ 无法找到数据库文件")
        print(f"搜索路径: {possible_paths}")
        return False
    
    print(f"📂 找到数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(courses)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'tokens_reward' in columns:
            print("✓ tokens_reward 列已存在，无需添加")
            conn.close()
            return True
        
        # 添加列
        print("⚙️  添加 tokens_reward 列...")
        cursor.execute("""
            ALTER TABLE courses 
            ADD COLUMN tokens_reward INTEGER DEFAULT 0
        """)
        
        conn.commit()
        print("✅ 成功添加 tokens_reward 列")
        
        # 验证
        cursor.execute("PRAGMA table_info(courses)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        if 'tokens_reward' in columns:
            print(f"✓ 列类型: {columns['tokens_reward']}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == '__main__':
    success = add_tokens_reward_column()
    if success:
        print("\n✨ 数据库迁移完成！")
        print("🚀 现在可以重启服务了")
    else:
        print("\n❌ 数据库迁移失败")
        exit(1)
