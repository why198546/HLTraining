"""直接测试token-grant API并捕获错误"""
import sys
import os
sys.path.insert(0, '/Users/hongyuwang/code/HLTraining')
os.chdir('/Users/hongyuwang/code/HLTraining')

from app import create_app
from flask_login import login_user

app = create_app()

with app.app_context():
    with app.test_request_context():
        # 获取管理员用户
        from auth.models import User
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            print("❌ 没有找到管理员用户")
            sys.exit(1)
        
        print(f"✅ 找到管理员: {admin.username}")
        
        # 模拟登录
        from flask_login import LoginManager
        login_manager = LoginManager()
        login_manager.init_app(app)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # 创建测试客户端并登录
        with app.test_client() as client:
            # 登录
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
            
            # 调用API
            print("\n正在调用 /admin/token-grant/stats?period=day...")
            response = client.get('/admin/token-grant/stats?period=day')
            
            print(f"\n状态码: {response.status_code}")
            
            if response.status_code == 200:
                import json
                data = json.loads(response.data)
                print(f"✅ API调用成功")
                print(f"\n返回数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ API调用失败")
                print(f"\n响应内容:")
                print(response.data.decode('utf-8'))
