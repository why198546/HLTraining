#!/usr/bin/env python3
"""
完整测试：验证编辑资料保存后页面显示是否更新
"""

import requests
import time
import re

BASE_URL = "http://localhost:8080"

def test_complete_profile_flow():
    """测试完整的个人资料编辑流程"""
    
    session = requests.Session()
    
    try:
        print("🔐 步骤1: 登录用户...")
        login_data = {
            'username': 'why',
            'password': 'test123'
        }
        
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=True)
        print(f"登录状态码: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ 登录失败")
            return False
            
        print("📄 步骤2: 获取个人资料页面...")
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        print(f"资料页面状态码: {profile_response.status_code}")
        
        if profile_response.status_code != 200:
            print("❌ 无法访问资料页面")
            return False
            
        # 提取当前昵称
        content = profile_response.text
        nickname_match = re.search(r'<h1>([^<]+)</h1>', content)
        current_nickname = nickname_match.group(1) if nickname_match else "未知"
        print(f"📝 当前昵称: {current_nickname}")
        
        # 生成新昵称
        import time
        new_nickname = f"新昵称_{int(time.time()) % 1000}"
        print(f"📝 准备更新为: {new_nickname}")
        
        print("✏️ 步骤3: 提交资料更新...")
        
        # 提取CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', content)
        csrf_token = csrf_match.group(1) if csrf_match else ''
        
        if not csrf_token:
            print("❌ 无法找到CSRF token")
            return False
            
        edit_data = {
            'csrf_token': csrf_token,
            'form_type': 'profile',
            'nickname': new_nickname,
            'age': '12',
            'bio': '测试个人简介',
            'color_preference': 'vibrant'
        }
        
        edit_response = session.post(f"{BASE_URL}/auth/profile", data=edit_data, allow_redirects=True)
        print(f"编辑提交状态码: {edit_response.status_code}")
        
        print("🔍 步骤4: 验证更新结果...")
        
        # 重新获取页面
        time.sleep(1)  # 等待一秒确保数据库更新完成
        updated_response = session.get(f"{BASE_URL}/auth/profile")
        updated_content = updated_response.text
        
        # 检查新昵称是否显示
        updated_nickname_match = re.search(r'<h1>([^<]+)</h1>', updated_content)
        updated_nickname = updated_nickname_match.group(1) if updated_nickname_match else "未知"
        
        print(f"📝 更新后显示的昵称: {updated_nickname}")
        
        if updated_nickname == new_nickname:
            print("✅ 成功！昵称已正确更新并显示")
            
            # 检查年龄是否也更新了
            age_match = re.search(r'· (\d+)岁', updated_content)
            updated_age = age_match.group(1) if age_match else "未知"
            print(f"📝 更新后显示的年龄: {updated_age}岁")
            
            return True
        else:
            print(f"❌ 失败！昵称未能正确更新")
            print(f"   期望: {new_nickname}")
            print(f"   实际: {updated_nickname}")
            
            # 输出一些调试信息
            print("\n🔍 调试信息:")
            if '资料更新成功' in updated_content:
                print("   ✅ 找到成功提示消息")
            else:
                print("   ❌ 没有找到成功提示消息")
                
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 开始完整的个人资料编辑测试...")
    print("=" * 50)
    
    success = test_complete_profile_flow()
    
    print("=" * 50)
    if success:
        print("🎉 测试通过！编辑资料功能正常工作，页面显示正确更新")
    else:
        print("❌ 测试失败！需要进一步检查问题")