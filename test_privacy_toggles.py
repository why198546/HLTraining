#!/usr/bin/env python3
"""
隐私设置切换开关功能测试
测试隐藏复选框输入框，使用切换开关样式
"""

import requests
import re
from bs4 import BeautifulSoup
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_privacy_toggles():
    """测试隐私设置切换开关功能"""
    base_url = "http://127.0.0.1:8080"
    session = requests.Session()
    
    print("🧪 开始隐私设置切换开关测试...")
    print("=" * 50)
    
    try:
        # 步骤1: 登录
        print("🔐 步骤1: 登录用户...")
        login_url = f"{base_url}/auth/login"
        login_response = session.get(login_url)
        
        if login_response.status_code != 200:
            print(f"❌ 获取登录页面失败: {login_response.status_code}")
            return False
            
        # 解析登录表单
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # 提交登录表单
        login_data = {
            'csrf_token': csrf_token,
            'username': 'testuser',
            'password': 'password123'
        }
        
        login_submit = session.post(login_url, data=login_data)
        print(f"登录状态码: {login_submit.status_code}")
        
        # 步骤2: 访问个人资料页面
        print("📄 步骤2: 获取个人资料页面...")
        profile_url = f"{base_url}/auth/profile"
        profile_response = session.get(profile_url)
        print(f"资料页面状态码: {profile_response.status_code}")
        
        if profile_response.status_code != 200:
            print("❌ 无法访问个人资料页面")
            return False
        
        # 步骤3: 解析页面，检查隐私设置结构
        print("🔍 步骤3: 检查隐私设置HTML结构...")
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # 检查隐私设置表单
        privacy_form = soup.find('form', class_='privacy-form')
        if not privacy_form:
            print("❌ 未找到隐私设置表单")
            return False
        else:
            print("✅ 找到隐私设置表单")
        
        # 检查隐私字段
        privacy_fields = ['show_in_gallery', 'show_age', 'allow_parent_reports']
        field_status = {}
        
        for field_name in privacy_fields:
            checkbox = soup.find('input', {'name': field_name})
            label = soup.find('label', {'for': field_name})
            
            if checkbox:
                # 检查是否有隐藏样式
                style = checkbox.get('style', '')
                is_hidden = 'display: none' in style or 'display:none' in style
                field_status[field_name] = {
                    'checkbox_found': True,
                    'checkbox_hidden': is_hidden,
                    'label_found': bool(label),
                    'current_value': checkbox.get('checked') is not None
                }
                print(f"  📋 {field_name}:")
                print(f"     复选框: {'隐藏' if is_hidden else '可见'}")
                print(f"     标签: {'存在' if label else '缺失'}")
                print(f"     当前值: {field_status[field_name]['current_value']}")
            else:
                field_status[field_name] = {
                    'checkbox_found': False,
                    'checkbox_hidden': False,
                    'label_found': bool(label),
                    'current_value': False
                }
                print(f"  ❌ {field_name}: 未找到复选框")
        
        # 步骤4: 检查CSS和JavaScript
        print("🎨 步骤4: 检查CSS样式和JavaScript...")
        
        # 检查切换开关CSS
        css_found = False
        js_found = False
        
        page_content = profile_response.text
        if 'toggle-switch' in page_content:
            css_found = True
            print("✅ 找到切换开关CSS样式")
        else:
            print("❌ 未找到切换开关CSS样式")
        
        if 'initPrivacyToggles' in page_content:
            js_found = True
            print("✅ 找到隐私切换JavaScript函数")
        else:
            print("❌ 未找到隐私切换JavaScript函数")
        
        # 步骤5: 测试表单提交
        print("📤 步骤5: 测试隐私设置更新...")
        
        # 获取CSRF令牌
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            csrf_value = csrf_token['value']
            
            # 准备更新数据
            privacy_data = {
                'csrf_token': csrf_value,
                'form_type': 'privacy',
                'show_in_gallery': 'y',  # 模拟开启
                'show_age': '',          # 模拟关闭
                'allow_parent_reports': 'y'  # 模拟开启
            }
            
            # 提交隐私设置更新
            privacy_submit = session.post(profile_url, data=privacy_data)
            print(f"隐私设置更新状态码: {privacy_submit.status_code}")
            
            if privacy_submit.status_code == 200:
                print("✅ 隐私设置表单提交成功")
            else:
                print(f"❌ 隐私设置表单提交失败: {privacy_submit.status_code}")
        else:
            print("❌ 未找到CSRF令牌")
        
        # 汇总结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        
        all_fields_ok = all(
            status['checkbox_found'] and status['checkbox_hidden'] and status['label_found']
            for status in field_status.values()
        )
        
        if all_fields_ok and css_found and js_found:
            print("✅ 所有测试通过！隐私设置切换开关功能正常")
            print("   - 所有复选框已正确隐藏")
            print("   - 切换开关标签正常显示")
            print("   - CSS样式已加载")
            print("   - JavaScript功能已实现")
            return True
        else:
            print("❌ 部分测试失败，需要检查以下问题:")
            if not all_fields_ok:
                print("   - 隐私字段结构有问题")
            if not css_found:
                print("   - CSS样式缺失")
            if not js_found:
                print("   - JavaScript功能缺失")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_privacy_toggles()
    sys.exit(0 if success else 1)