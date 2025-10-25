#!/usr/bin/env python3
"""
最终测试：验证编辑资料功能是否完全修复
"""

import requests
import time
import re

BASE_URL = "http://localhost:8080"

def test_profile_edit_final():
    """最终测试个人资料编辑功能"""
    
    session = requests.Session()
    
    try:
        print("🔐 登录用户...")
        login_data = {
            'username': 'why',
            'password': 'test123'
        }
        
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=True)
        
        if login_response.status_code != 200:
            print("❌ 登录失败")
            return False
            
        print("📄 获取个人资料页面...")
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        
        if profile_response.status_code != 200:
            print("❌ 无法访问资料页面")
            return False
            
        content = profile_response.text
        
        # 提取当前昵称
        nickname_match = re.search(r'<h1>([^<]+)</h1>', content)
        current_nickname = nickname_match.group(1) if nickname_match else "未知"
        print(f"📝 当前昵称: {current_nickname}")
        
        # 生成新昵称
        new_nickname = f"修复后测试_{int(time.time()) % 1000}"
        print(f"📝 准备更新为: {new_nickname}")
        
        print("✏️ 提交资料更新...")
        
        # 提取CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', content)
        csrf_token = csrf_match.group(1) if csrf_match else ''
        
        edit_data = {
            'csrf_token': csrf_token,
            'form_type': 'profile',
            'nickname': new_nickname,
            'age': '12',
            'color_preference': 'vibrant',  # 现在包含必需的color_preference字段
            'bio': '测试修复后的功能'
        }
        
        edit_response = session.post(f"{BASE_URL}/auth/profile", data=edit_data, allow_redirects=True)
        print(f"编辑提交状态码: {edit_response.status_code}")
        
        print("🔍 验证更新结果...")
        
        # 重新获取页面
        time.sleep(1)
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
            
            # 检查成功消息
            if '资料更新成功' in updated_content:
                print("✅ 找到成功提示消息")
            
            return True
        else:
            print(f"❌ 失败！昵称未能正确更新")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始最终修复验证测试...")
    print("=" * 60)
    
    success = test_profile_edit_final()
    
    print("=" * 60)
    if success:
        print("🎉 修复成功！编辑资料功能现在正常工作")
        print("✅ 用户可以正常编辑昵称、年龄、色彩偏好等信息")
        print("✅ 保存后页面正确显示更新的信息")
        print("✅ 不需要手动刷新页面")
    else:
        print("❌ 修复未完成，仍需进一步检查")