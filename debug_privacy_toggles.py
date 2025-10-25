#!/usr/bin/env python3
"""
调试隐私设置滑块问题
"""

import requests
import time
import sys
from bs4 import BeautifulSoup

def debug_privacy_toggles():
    """调试隐私设置滑块"""
    print("🔍 开始调试隐私设置滑块问题...")
    print("=" * 50)
    
    try:
        # 等待服务器启动
        time.sleep(2)
        
        # 测试服务器连接
        print("🔗 测试服务器连接...")
        response = requests.get("http://127.0.0.1:8080", timeout=5)
        print(f"服务器响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ 服务器无法访问")
            return False
        
        # 获取登录页面
        print("🔐 获取登录页面...")
        login_response = requests.get("http://127.0.0.1:8080/auth/login", timeout=5)
        
        if login_response.status_code != 200:
            print("❌ 无法访问登录页面")
            return False
            
        # 创建会话并登录
        session = requests.Session()
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # 尝试登录
        login_data = {
            'csrf_token': csrf_token,
            'username': 'testuser',
            'password': 'password123'
        }
        
        login_submit = session.post("http://127.0.0.1:8080/auth/login", data=login_data)
        print(f"登录提交状态码: {login_submit.status_code}")
        
        # 获取个人资料页面
        print("📄 获取个人资料页面...")
        profile_response = session.get("http://127.0.0.1:8080/auth/profile")
        print(f"个人资料页面状态码: {profile_response.status_code}")
        
        if profile_response.status_code != 200:
            print("❌ 无法访问个人资料页面")
            return False
            
        # 解析页面内容
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # 检查隐私设置字段
        print("\n🔍 检查隐私设置字段...")
        privacy_fields = ['show_in_gallery', 'show_age', 'allow_parent_reports']
        
        for field_name in privacy_fields:
            print(f"\n📋 检查字段: {field_name}")
            
            # 查找checkbox
            checkbox = soup.find('input', {'name': field_name})
            if checkbox:
                field_id = checkbox.get('id', '无ID')
                field_type = checkbox.get('type', '无类型')
                field_checked = checkbox.has_attr('checked')
                field_style = checkbox.get('style', '无样式')
                
                print(f"  ✅ 复选框找到:")
                print(f"     ID: {field_id}")
                print(f"     类型: {field_type}")
                print(f"     选中状态: {field_checked}")
                print(f"     样式: {field_style}")
                
                # 查找对应的label
                label = soup.find('label', {'for': field_id})
                if label:
                    label_class = label.get('class', [])
                    print(f"  ✅ 标签找到:")
                    print(f"     类: {label_class}")
                    print(f"     内容: {label.get_text()[:50]}...")
                else:
                    print(f"  ❌ 未找到对应标签 (for='{field_id}')")
                    
                    # 查找所有相关标签
                    all_labels = soup.find_all('label')
                    toggle_labels = [l for l in all_labels if 'toggle-switch' in l.get('class', [])]
                    print(f"  🔍 找到 {len(toggle_labels)} 个切换开关标签")
                    
            else:
                print(f"  ❌ 未找到复选框 (name='{field_name}')")
        
        # 检查JavaScript函数
        print("\n🔧 检查JavaScript函数...")
        page_content = profile_response.text
        
        if 'initPrivacyToggles' in page_content:
            print("  ✅ 找到 initPrivacyToggles 函数")
        else:
            print("  ❌ 未找到 initPrivacyToggles 函数")
            
        if 'updateToggleState' in page_content:
            print("  ✅ 找到 updateToggleState 函数")
        else:
            print("  ❌ 未找到 updateToggleState 函数")
            
        # 检查CSS样式
        print("\n🎨 检查CSS样式...")
        if 'toggle-switch' in page_content:
            print("  ✅ 找到切换开关CSS样式")
        else:
            print("  ❌ 未找到切换开关CSS样式")
        
        # 输出原始HTML片段用于调试
        print("\n📝 隐私设置HTML片段:")
        privacy_section = soup.find('div', class_='privacy-section')
        if privacy_section:
            print(str(privacy_section)[:500] + "...")
        else:
            print("❌ 未找到隐私设置区域")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return False
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = debug_privacy_toggles()
    sys.exit(0 if success else 1)