#!/usr/bin/env python3
"""直接测试profile页面是否有form错误"""

import requests
import time

# 给Flask一些时间启动
time.sleep(2)

# 测试基本连通性
try:
    response = requests.get("http://127.0.0.1:8080/", timeout=5)
    print(f"✅ Flask服务器运行正常，状态码: {response.status_code}")
except Exception as e:
    print(f"❌ Flask服务器连接失败: {e}")
    exit(1)

# 测试登录页面
try:
    response = requests.get("http://127.0.0.1:8080/auth/login", timeout=5)
    print(f"✅ 登录页面访问正常，状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 登录页面访问失败: {e}")
    exit(1)

# 测试profile页面（应该重定向）
try:
    response = requests.get("http://127.0.0.1:8080/auth/profile", timeout=5, allow_redirects=False)
    print(f"✅ Profile页面重定向正常，状态码: {response.status_code}")
    print(f"重定向地址: {response.headers.get('Location', '无')}")
except Exception as e:
    print(f"❌ Profile页面访问失败: {e}")

print("\n现在请手动在浏览器中：")
print("1. 访问 http://127.0.0.1:8080/auth/login")
print("2. 使用用户名 'test' 和密码 'test123' 登录")
print("3. 访问 http://127.0.0.1:8080/auth/profile")
print("4. 查看是否有错误信息")
print("\n如果有错误，请报告错误信息！")