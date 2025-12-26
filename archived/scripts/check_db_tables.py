import sqlite3

for db_name in ['instance/site.db', 'instance/hltraining.db']:
    print(f"\n检查 {db_name}:")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [row[0] for row in cursor.fetchall()]
    print(f'  数据库表: {tables}')

    if 'users' in tables:
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f'  users表字段: {columns}')
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f'  users数量: {count}')
    
    conn.close()
