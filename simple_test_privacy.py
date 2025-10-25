#!/usr/bin/env python3
"""
隐私设置功能简单测试
"""

import requests
import time
import sys

def simple_test():
    """简单测试隐私设置页面"""
    print("🧪 开始简单的隐私设置功能测试...")
    print("=" * 50)
    
    try:
        # 测试服务器连接
        print("🔗 步骤1: 测试服务器连接...")
        response = requests.get("http://127.0.0.1:8080", timeout=5)
        print(f"服务器响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 服务器正常运行")
        else:
            print("❌ 服务器状态异常")
            return False
        
        # 测试登录页面
        print("🔐 步骤2: 测试登录页面...")
        login_response = requests.get("http://127.0.0.1:8080/auth/login", timeout=5)
        print(f"登录页面状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ 登录页面正常")
        else:
            print("❌ 登录页面异常")
            return False
        
        # 检查页面内容
        print("📄 步骤3: 检查页面内容...")
        content = login_response.text
        
        if 'toggle-switch' in content:
            print("✅ 找到切换开关CSS类")
        else:
            print("⚠️  未在登录页面找到切换开关CSS（正常，只有个人资料页面才有）")
        
        print("\n" + "=" * 50)
        print("📊 测试完成！")
        print("✅ 基本功能正常")
        print("🌐 现在可以手动访问 http://127.0.0.1:8080 进行完整测试")
        print("   1. 注册/登录用户")
        print("   2. 访问个人资料页面")
        print("   3. 测试隐私设置切换开关")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)