#!/usr/bin/env python3
"""
更新用户表结构，将 birth_date 和 gender 字段改为可选
"""

import sqlite3
import sys
import os

def update_schema(db_path):
    """更新数据库表结构"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("users 表不存在")
            conn.close()
            return False
        
        print("开始更新用户表结构...")
        
        # SQLite 不支持直接修改列的约束，需要重建表
        # 1. 创建临时表
        cursor.execute("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                username VARCHAR(20) UNIQUE NOT NULL,
                nickname VARCHAR(50) NOT NULL,
                birth_date DATE,
                gender VARCHAR(10),
                contact_phone VARCHAR(20),
                mailing_address TEXT,
                parent_email VARCHAR(120) NOT NULL,
                avatar_url VARCHAR(200) DEFAULT 'default_avatar.png',
                password_hash VARCHAR(255) NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                verification_token VARCHAR(100) UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                role VARCHAR(20) DEFAULT 'student',
                color_preference VARCHAR(20) DEFAULT 'vibrant',
                privacy_settings JSON
            )
        """)
        
        # 2. 复制数据
        cursor.execute("""
            INSERT INTO users_new 
            SELECT * FROM users
        """)
        
        # 3. 删除旧表
        cursor.execute("DROP TABLE users")
        
        # 4. 重命名新表
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        # 5. 重建索引
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)")
        
        conn.commit()
        print("✅ 用户表结构更新成功！")
        print("   - birth_date 字段已改为可选")
        print("   - gender 字段已改为可选")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    # 默认数据库路径
    db_path = 'instance/hltraining.db'
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"数据库路径: {db_path}")
    success = update_schema(db_path)
    sys.exit(0 if success else 1)
