#!/usr/bin/env python3
"""测试脚本，检查profile页面是否正常工作"""

import requests
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8080"

# 创建一个session来保持cookies
session = requests.Session()

try:
    # 1. 尝试访问profile页面（应该会被重定向到登录页面）
    print("1. 访问profile页面（未登录）...")
    response = session.get(urljoin(BASE_URL, "/auth/profile"))
    print(f"状态码: {response.status_code}")
    print(f"最终URL: {response.url}")
    
    # 2. 访问登录页面获取表单
    print("\n2. 获取登录页面...")
    login_response = session.get(urljoin(BASE_URL, "/auth/login"))
    print(f"登录页面状态码: {login_response.status_code}")
    
    # 3. 尝试使用测试账号登录（如果存在的话）
    print("\n3. 尝试登录...")
    
    login_data = {
        'username': 'test',
        'password': 'test123'
    }
    
    login_post = session.post(urljoin(BASE_URL, "/auth/login"), data=login_data)
    print(f"登录POST状态码: {login_post.status_code}")
    print(f"登录后URL: {login_post.url}")
    
    # 4. 再次尝试访问profile页面
    print("\n4. 再次访问profile页面（登录后）...")
    profile_response = session.get(urljoin(BASE_URL, "/auth/profile"))
    print(f"Profile页面状态码: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        print("✅ Profile页面加载成功！")
        # 检查页面内容是否包含表单
        if 'form' in profile_response.text.lower() or 'nickname' in profile_response.text.lower():
            print("✅ 页面包含表单元素")
        else:
            print("❌ 页面似乎缺少表单元素")
    else:
        print(f"❌ Profile页面访问失败，状态码: {profile_response.status_code}")
        if profile_response.text:
            print("错误内容前100字符:")
            print(profile_response.text[:100])

except Exception as e:
    print(f"❌ 测试过程中发生错误: {e}")