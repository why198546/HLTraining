"""
更新所有现有用户的privacy_settings字段，使用新的键名
"""
import sqlite3
import json

conn = sqlite3.connect('D:/Code/HLTraining/instance/hltraining.db')
cursor = conn.cursor()

# 获取所有用户
cursor.execute("SELECT id, username, privacy_settings FROM users")
users = cursor.fetchall()

print(f"找到 {len(users)} 个用户，开始更新...")

for user_id, username, privacy_json in users:
    if privacy_json:
        try:
            privacy = json.loads(privacy_json)
            
            # 保留show_in_gallery
            new_privacy = {
                'show_in_gallery': privacy.get('show_in_gallery', True),
                'show_age': privacy.get('show_age', False),  # 新字段，默认False
                'allow_parent_reports': privacy.get('parental_controls', privacy.get('allow_sharing', True))  # 从旧字段迁移
            }
            
            new_privacy_json = json.dumps(new_privacy)
            cursor.execute("UPDATE users SET privacy_settings = ? WHERE id = ?", (new_privacy_json, user_id))
            print(f"✅ 更新用户 {username} (ID: {user_id})")
            print(f"   旧值: {privacy_json}")
            print(f"   新值: {new_privacy_json}")
        except Exception as e:
            print(f"❌ 更新用户 {username} 失败: {e}")
    else:
        # 如果没有privacy_settings，设置默认值
        default_privacy = {
            'show_in_gallery': True,
            'show_age': False,
            'allow_parent_reports': True
        }
        default_privacy_json = json.dumps(default_privacy)
        cursor.execute("UPDATE users SET privacy_settings = ? WHERE id = ?", (default_privacy_json, user_id))
        print(f"✅ 为用户 {username} (ID: {user_id}) 设置默认值")

conn.commit()
conn.close()

print("\n✨ 数据库迁移完成！")
