"""
直接使用SQLite添加游客系统字段
"""

import os
import sqlite3

db_path = 'instance/hltraining.db'

if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查现有字段
cursor.execute("PRAGMA table_info(users)")
existing_columns = [row[1] for row in cursor.fetchall()]
print("现有字段:", existing_columns)

# 需要添加的字段
new_columns = {
    'daily_token_amount': 'INTEGER DEFAULT 0',
    'trial_end_date': 'DATETIME',
    'last_token_grant_date': 'DATE',
    'course_type': 'VARCHAR(50)'
}

# 添加缺失的字段
for column_name, column_type in new_columns.items():
    if column_name not in existing_columns:
        try:
            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
            cursor.execute(sql)
            print(f"✅ 添加字段: {column_name}")
        except sqlite3.OperationalError as e:
            print(f"❌ 添加字段 {column_name} 失败: {e}")
    else:
        print(f"⏭️  字段已存在: {column_name}")

conn.commit()
conn.close()

print("\n迁移完成！")
