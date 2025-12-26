#!/usr/bin/env python3
"""测试相机功能 - 包含登录"""

import requests
from bs4 import BeautifulSoup

# 创建session保持登录状态
session = requests.Session()

# 先获取登录页面的CSRF token
login_page = session.get('http://localhost:8088/auth/login')
soup = BeautifulSoup(login_page.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})

print("请提供登录信息：")
print("如果你有测试账号，我可以用来登录测试")
print("或者你可以直接在浏览器中登录后，手动测试相机按钮")
print("\n按Ctrl+C取消\n")

username = input("用户名: ")
password = input("密码: ")

# 登录
login_data = {
    'username': username,
    'password': password,
    'remember': 'y'
}

if csrf_token:
    login_data['csrf_token'] = csrf_token.get('value')

response = session.post('http://localhost:8088/auth/login', data=login_data, allow_redirects=True)

if 'sunguo' in response.url or response.status_code == 200:
    print("✅ 登录成功！")
    
    # 访问课程页面
    lesson_page = session.get('http://localhost:8088/sunguo-class/character')
    soup = BeautifulSoup(lesson_page.text, 'html.parser')
    
    # 检查相机按钮
    camera_buttons = soup.find_all('button', class_='camera-input-btn')
    print(f"\n📷 找到相机按钮: {len(camera_buttons)} 个")
    
    # 检查模态框
    modal = soup.find('div', id='camera-modal')
    print(f"📦 找到模态框: {'是' if modal else '否'}")
    
    # 检查JS文件
    scripts = soup.find_all('script', src=True)
    camera_js = [s.get('src') for s in scripts if 'camera-input.js' in s.get('src')]
    print(f"📜 找到camera-input.js: {'是' if camera_js else '否'}")
    
    if camera_buttons and modal and camera_js:
        print("\n✅ 所有必要元素都在页面中！")
        print("如果点击按钮没反应，请检查浏览器控制台的JavaScript错误")
    else:
        print("\n❌ 缺少必要元素！")
        if not camera_buttons:
            print("  - 缺少相机按钮")
        if not modal:
            print("  - 缺少模态框")
        if not camera_js:
            print("  - 缺少JavaScript文件引用")
else:
    print(f"❌ 登录失败: {response.status_code}")
    print(response.text[:500])
