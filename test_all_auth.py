#!/usr/bin/env python3
"""完整测试：验证所有认证相关页面都正常工作"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
import time

def test_all_auth_pages():
    """测试所有认证相关页面"""
    with app.app_context():
        with app.test_client() as client:
            # 获取测试用户
            user = User.query.filter_by(username='test').first()
            if not user:
                print("❌ 测试用户不存在")
                return False
            
            # 模拟登录
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            print("✅ 模拟用户登录成功")
            
            tests = [
                ('/auth/profile', 'Profile页面', '个人资料'),
                ('/auth/my-artworks', 'My Artworks页面', '我的作品'),
                (f'/auth/parent-dashboard/{user.verification_token}', '家长控制台', '孩子的作品')
            ]
            
            all_passed = True
            
            for url, name, expected_content in tests:
                print(f"\n🔍 测试 {name}...")
                try:
                    response = client.get(url)
                    
                    if response.status_code == 200:
                        print(f"✅ {name} 加载成功")
                        
                        content = response.data.decode('utf-8')
                        
                        if expected_content in content:
                            print(f"✅ {name} 内容正确")
                        else:
                            print(f"❌ {name} 内容缺失")
                            all_passed = False
                        
                        # 检查是否有错误信息
                        if any(error in content for error in ['TypeError', '500 Internal Server Error', 'BuildError', 'UndefinedError']):
                            print(f"❌ {name} 包含错误信息")
                            all_passed = False
                        else:
                            print(f"✅ {name} 无错误信息")
                            
                    else:
                        print(f"❌ {name} 访问失败，状态码: {response.status_code}")
                        all_passed = False
                        
                except Exception as e:
                    print(f"❌ {name} 测试失败: {e}")
                    all_passed = False
            
            return all_passed

if __name__ == "__main__":
    print("🚀 开始完整认证系统测试...")
    success = test_all_auth_pages()
    if success:
        print("\n🎉 所有认证页面测试通过！系统完全可用！")
    else:
        print("\n❌ 还有页面存在问题！")