#!/usr/bin/env python
"""
移除age字段并创建测试用户
因为现在使用birth_date动态计算年龄
"""
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db, User

USERS = [
    # username, nickname, age, parent_email, password, role
    ("test_admin", "管理员", 35, "parent_admin@example.com", "admin123", "admin"),
    ("teacher1", "张老师", 30, "parent_teacher1@example.com", "123456", "teacher"),
    ("teacher2", "李老师", 28, "parent_teacher2@example.com", "123456", "teacher"),
    ("student1", "小明", 12, "parent_student1@example.com", "123456", "student"),
    ("student2", "小红", 11, "parent_student2@example.com", "123456", "student"),
    ("student3", "小刚", 13, "parent_student3@example.com", "123456", "student"),
    ("visitor1", "小华", 10, "parent_visitor1@example.com", "123456", "visitor"),
    ("visitor2", "小丽", 12, "parent_visitor2@example.com", "123456", "visitor"),
    ("visitor3", "小强", 11, "parent_visitor3@example.com", "123456", "visitor"),
    ("visitor4", "小美", 13, "parent_visitor4@example.com", "123456", "visitor"),
]


def remove_age_column():
    """删除age字段（SQLite需要重建表）"""
    print("🔧 开始移除age字段...")
    
    app = create_app()
    with app.app_context():
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            # 检查age字段是否存在
            result = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'age' not in columns:
                print("✅ age字段已经不存在，跳过删除步骤")
                return
            
            print("📋 当前字段列表:")
            for col in columns:
                print(f"   - {col}")
            
            # SQLite不支持DROP COLUMN，需要重建表
            print("\n⚠️  SQLite不支持直接删除列，需要重建表")
            print("📝 创建临时表...")
            
            conn.execute(text("""
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
                    created_at DATETIME,
                    last_login DATETIME,
                    role VARCHAR(20) DEFAULT 'student',
                    color_preference VARCHAR(20) DEFAULT 'vibrant',
                    privacy_settings JSON,
                    image_token_remaining INTEGER DEFAULT 50,
                    is_enrolled BOOLEAN DEFAULT 0,
                    daily_token_amount INTEGER DEFAULT 0,
                    trial_end_date DATETIME,
                    last_token_grant_date DATE,
                    course_type VARCHAR(50)
                )
            """))
            conn.commit()
            
            print("📤 复制数据到新表...")
            conn.execute(text("""
                INSERT INTO users_new 
                SELECT id, username, nickname, birth_date, gender, contact_phone, 
                       mailing_address, parent_email, avatar_url, password_hash, 
                       is_verified, verification_token, created_at, last_login, role,
                       color_preference, privacy_settings, image_token_remaining, 
                       is_enrolled, daily_token_amount, trial_end_date, 
                       last_token_grant_date, course_type
                FROM users
            """))
            conn.commit()
            
            print("🗑️  删除旧表...")
            conn.execute(text("DROP TABLE users"))
            conn.commit()
            
            print("♻️  重命名新表...")
            conn.execute(text("ALTER TABLE users_new RENAME TO users"))
            conn.commit()
            
            print("✅ age字段已成功移除！\n")


def create_users():
    """创建测试用户"""
    print("👥 开始创建测试用户...")
    
    app = create_app()
    with app.app_context():
        created = []
        for username, nickname, age, parent_email, password, role in USERS:
            existing = User.query.filter_by(username=username).first()
            if existing:
                print(f"⏭️  用户已存在，跳过: {username}")
                continue

            # 根据年龄计算出生日期
            birth_date = date.today() - timedelta(days=age*365)
            
            user = User(
                username=username, 
                nickname=nickname, 
                parent_email=parent_email, 
                password=password, 
                birth_date=birth_date,
                role=role
            )

            db.session.add(user)
            try:
                db.session.commit()
                created.append(username)
                print(f"✅ 已创建用户: {username} (role={role}, age={age})")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 创建用户失败: {username} -> {e}")

        print(f'\n📊 汇总: 成功创建 {len(created)} 个用户')
        if created:
            print(f'   {", ".join(created)}')


if __name__ == '__main__':
    remove_age_column()
    create_users()
