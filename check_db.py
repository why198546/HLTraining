import sqlite3

conn = sqlite3.connect('D:/Code/HLTraining/instance/hltraining.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 查看所有用户
try:
    cursor.execute("SELECT id, username, nickname, privacy_settings FROM users ORDER BY id DESC LIMIT 5")
    users = cursor.fetchall()
    print(f"\n最近的5个用户:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Nickname: {user[2]}, Privacy: {user[3]}")
except Exception as e:
    print(f"查询错误: {e}")

conn.close()
