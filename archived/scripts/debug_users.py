from app import create_app
from auth.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"{'ID':<5} | {'Username':<15} | {'Nickname':<15} | {'Role':<10} | {'Tokens':<10}")
    print("-" * 65)
    for u in users:
        print(f"{u.id:<5} | {u.username:<15} | {u.nickname:<15} | {u.role:<10} | {u.image_token_remaining:<10}")
