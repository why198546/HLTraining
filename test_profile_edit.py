#!/usr/bin/env python3
"""
测试用户资料编辑功能是否正常工作
"""

import requests
import time

BASE_URL = "http://localhost:8080"

def test_profile_edit():
    """测试个人资料编辑功能"""
    
    # 创建一个会话
    session = requests.Session()
    
    try:
        # 1. 登录
        print("🔐 登录用户...")
        login_data = {
            'username': 'why',
            'password': 'test123'
        }
        
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"登录状态码: {login_response.status_code}")
        
        if login_response.status_code != 200 and login_response.status_code != 302:
            print("❌ 登录失败")
            return False
            
        # 2. 获取当前资料页面
        print("\n📄 获取当前资料页面...")
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        print(f"资料页面状态码: {profile_response.status_code}")
        
        if profile_response.status_code != 200:
            print("❌ 无法访问资料页面")
            return False
            
        # 检查当前昵称
        content = profile_response.text
        if '小画家' in content:
            print("✅ 找到当前昵称: 小画家")
            new_nickname = "测试画家"
        else:
            print("✅ 当前昵称不是小画家")
            new_nickname = "小画家"
            
        # 3. 提交编辑表单
        print(f"\n✏️ 更新昵称为: {new_nickname}")
        
        # 从页面中提取CSRF token
        import re
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', content)
        csrf_token = csrf_match.group(1) if csrf_match else ''
        
        edit_data = {
            'csrf_token': csrf_token,
            'form_type': 'profile',
            'nickname': new_nickname,
            'age': '12',
            'bio': '',
            'color_preference': 'blue'
        }
        
        edit_response = session.post(f"{BASE_URL}/auth/profile", data=edit_data)
        print(f"编辑提交状态码: {edit_response.status_code}")
        
        # 4. 检查更新后的页面
        print("\n🔍 验证更新结果...")
        updated_response = session.get(f"{BASE_URL}/auth/profile")
        updated_content = updated_response.text
        
        if new_nickname in updated_content:
            print(f"✅ 昵称成功更新为: {new_nickname}")
            print("✅ 编辑资料功能正常工作！")
            return True
        else:
            print(f"❌ 昵称未能更新，仍然显示旧内容")
            # 打印一些调试信息
            print("页面内容中的用户信息部分:")
            import re
            user_info_match = re.search(r'<h1>([^<]+)</h1>', updated_content)
            if user_info_match:
                print(f"当前显示的昵称: {user_info_match.group(1)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试用户资料编辑功能...")
    success = test_profile_edit()
    
    if success:
        print("\n🎉 测试通过！用户资料编辑功能正常工作")
    else:
        print("\n❌ 测试失败！需要进一步检查代码")