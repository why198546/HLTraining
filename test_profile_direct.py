#!/usr/bin/env python3
"""测试家长控制台按钮在个人资料页面的显示"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import User
import time

def test_profile_parent_dashboard_button():
    """测试个人资料页面的家长控制台按钮"""
    with app.app_context():
        with app.test_client() as client:
            # 测试why用户（现在应该有验证令牌了）
            user = User.query.filter_by(username='why').first()
            if not user:
                print("❌ why用户不存在")
                return False
            
            print(f"✅ 找到用户: {user.username}")
            print(f"✅ 验证令牌: {user.verification_token}")
            
            # 模拟登录why用户
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            print("✅ 模拟用户登录成功")
            
            try:
                response = client.get('/auth/profile')
                print(f"📄 Profile页面状态码: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.data.decode('utf-8')
                    
                    # 检查是否包含可用的家长控制台按钮
                    if '家长控制台（不可用）' in content:
                        print("❌ 仍然显示'家长控制台（不可用）'")
                        print("检查验证令牌是否正确传递...")
                        
                        # 检查模板中是否正确获取到verification_token
                        if f'parent-dashboard/{user.verification_token}' in content:
                            print("✅ 验证令牌在模板中存在")
                        else:
                            print("❌ 验证令牌在模板中不存在")
                        
                        return False
                        
                    elif '家长控制台' in content and '不可用' not in content:
                        print("✅ 显示可用的家长控制台按钮")
                        
                        # 验证链接是否正确
                        if f'parent-dashboard/{user.verification_token}' in content:
                            print("✅ 家长控制台链接正确")
                        else:
                            print("❌ 家长控制台链接不正确")
                            
                        return True
                        
                    else:
                        print("❌ 未找到家长控制台按钮")
                        return False
                        
                else:
                    print(f"❌ Profile页面加载失败，状态码: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == "__main__":
    print("🚀 开始测试家长控制台按钮...")
    success = test_profile_parent_dashboard_button()
    if success:
        print("\n🎉 家长控制台按钮测试通过！")
    else:
        print("\n❌ 家长控制台按钮测试失败！")