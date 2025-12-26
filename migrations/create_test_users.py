#!/usr/bin/env python
"""
创建 10 个测试用户脚本：
- 1 admin (password: admin123)
- 2 teachers (password: 123456)
- 3 formal students (password: 123456)
- 4 prospective/visitor students (password: 123456)

运行：
    python migrations/create_test_users.py
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db, User

USERS = [
    # username, nickname, parent_email, password, role
    ("test_admin", "Admin", "parent_admin@example.com", "admin123", "admin"),
    ("teacher1", "Teacher A", "parent_teacher1@example.com", "123456", "teacher"),
    ("teacher2", "Teacher B", "parent_teacher2@example.com", "123456", "teacher"),
    ("student1", "Student One", "parent_student1@example.com", "123456", "student"),
    ("student2", "Student Two", "parent_student2@example.com", "123456", "student"),
    ("student3", "Student Three", "parent_student3@example.com", "123456", "student"),
    ("visitor1", "Prospect One", "parent_visitor1@example.com", "123456", "visitor"),
    ("visitor2", "Prospect Two", "parent_visitor2@example.com", "123456", "visitor"),
    ("visitor3", "Prospect Three", "parent_visitor3@example.com", "123456", "visitor"),
    ("visitor4", "Prospect Four", "parent_visitor4@example.com", "123456", "visitor"),
]


def create_users():
    app = create_app()
    with app.app_context():
        created = []
        for username, nickname, parent_email, password, role in USERS:
            existing = User.query.filter_by(username=username).first()
            if existing:
                print(f"⏭️ 用户已存在，跳过: {username}")
                continue

            user = User(username=username, nickname=nickname, parent_email=parent_email, password=password, role=role)

            # ensure created_at exists
            if not getattr(user, 'created_at', None):
                user.created_at = datetime.utcnow()

            db.session.add(user)
            try:
                db.session.commit()
                created.append(username)
                print(f"✅ 已创建用户: {username} (role={role})")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 创建用户失败: {username} -> {e}")

        print('\nSummary:')
        print(f'Created: {len(created)} new users')
        if created:
            print(', '.join(created))


if __name__ == '__main__':
    create_users()
