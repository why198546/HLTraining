from app import create_app
from auth.models import User, db

app = create_app()

with app.app_context():
    students = User.query.filter_by(role='student').all()
    print('学生令牌情况:')
    print('-' * 60)
    for s in students:
        print(f'ID: {s.id:2d} | 用户名: {s.username:12s} | 昵称: {s.nickname:6s} | 令牌: {s.image_token_remaining}')
