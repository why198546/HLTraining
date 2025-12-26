"""测试token-grant API"""
import sys
sys.path.insert(0, '/Users/hongyuwang/code/HLTraining')

from app import create_app

app = create_app()

with app.app_context():
    # 模拟登录的管理员
    from auth.models import User
    admin = User.query.filter_by(role='admin').first()
    
    if not admin:
        print("❌ 没有找到管理员用户")
        sys.exit(1)
    
    print(f"✅ 找到管理员: {admin.username}")
    
    # 测试API
    with app.test_client() as client:
        # 先登录
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id
        
        # 调用API
        response = client.get('/admin/token-grant/stats?period=day')
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.data)
            print(f"✅ API调用成功")
            print(f"   success: {data.get('success')}")
            print(f"   period: {data.get('period')}")
            print(f"   total_stats: {data.get('total_stats')}")
            print(f"   trend_data条数: {len(data.get('trend_data', []))}")
            print(f"   source_distribution条数: {len(data.get('source_distribution', []))}")
            print(f"   recent_grants条数: {len(data.get('recent_grants', []))}")
        else:
            print(f"❌ API调用失败")
            print(response.data.decode('utf-8')[:500])
