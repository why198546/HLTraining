#!/usr/bin/env python3
"""
完整测试我的作品页面的所有功能
"""

import requests
import json
import time

def test_artwork_functionality():
    """测试作品页面的完整功能"""
    base_url = "http://localhost:8080"
    
    # 创建session保持登录状态
    session = requests.Session()
    
    print("🔐 步骤1: 测试登录...")
    
    # 登录
    login_data = {
        'username': 'why',
        'password': 'password123'
    }
    
    try:
        login_response = session.post(f"{base_url}/auth/login", 
                                    data=login_data, 
                                    allow_redirects=True)
        
        if login_response.status_code == 200:
            print("✅ 登录成功")
            
            # 测试我的作品页面是否能正常加载
            print("\n📄 步骤2: 测试我的作品页面...")
            profile_response = session.get(f"{base_url}/auth/my-artworks")
            
            if profile_response.status_code == 200:
                print("✅ 我的作品页面加载成功")
                
                # 检查页面是否包含预期的内容
                content = profile_response.text
                if '我的作品' in content:
                    print("✅ 页面标题正确")
                else:
                    print("❌ 页面标题未找到")
                
                if 'artwork-card' in content or '还没有创作作品' in content:
                    print("✅ 页面结构正常")
                else:
                    print("❌ 页面结构异常")
                
                # 测试作品API
                print("\n🎨 步骤3: 测试作品API...")
                
                # 测试获取作品详情API
                artwork_response = session.get(f"{base_url}/api/artwork/1")
                
                if artwork_response.status_code == 200:
                    artwork_data = artwork_response.json()
                    print(f"✅ 作品API正常 - 作品: {artwork_data.get('title', '未知')}")
                    
                    # 测试隐私设置API
                    privacy_response = session.post(f"{base_url}/api/artwork/1/privacy",
                                                  json={'is_public': False})
                    
                    if privacy_response.status_code == 200:
                        privacy_data = privacy_response.json()
                        print("✅ 隐私设置API正常")
                    else:
                        print(f"❌ 隐私设置API失败: {privacy_response.status_code}")
                        
                elif artwork_response.status_code == 404:
                    print("ℹ️  作品不存在（如果没有作品这是正常的）")
                else:
                    print(f"❌ 作品API失败: {artwork_response.status_code}")
                    print(f"响应: {artwork_response.text}")
                
                # 测试删除API（不实际删除，只测试响应）
                print("\n🗑️  步骤4: 测试删除API（模拟）...")
                
                # 测试删除不存在的作品
                delete_response = session.delete(f"{base_url}/api/artwork/9999")
                
                if delete_response.status_code == 404:
                    print("✅ 删除API正确处理不存在的作品")
                else:
                    print(f"❌ 删除API响应异常: {delete_response.status_code}")
                
                print("\n🎯 步骤5: 测试JavaScript功能...")
                
                # 检查页面是否包含必要的JavaScript函数
                js_functions = ['viewArtwork', 'deleteArtwork', 'shareArtwork', 'featureArtwork']
                missing_functions = []
                
                for func in js_functions:
                    if f'function {func}' in content:
                        print(f"✅ JavaScript函数 {func} 存在")
                    else:
                        missing_functions.append(func)
                        print(f"❌ JavaScript函数 {func} 缺失")
                
                if not missing_functions:
                    print("✅ 所有JavaScript函数都存在")
                else:
                    print(f"❌ 缺失的JavaScript函数: {', '.join(missing_functions)}")
                
                # 检查是否有模态框
                if 'artwork-modal' in content:
                    print("✅ 作品详情模态框存在")
                else:
                    print("❌ 作品详情模态框缺失")
                
            else:
                print(f"❌ 我的作品页面加载失败: {profile_response.status_code}")
                return False
                
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    print("\n" + "="*60)
    print("🏁 测试总结")
    print("="*60)
    print("所有基本功能已经测试完成。")
    print("如果看到 ✅ 表示功能正常")
    print("如果看到 ❌ 表示需要进一步检查")
    print("\n💡 要完整测试作品功能，请:")
    print("1. 在浏览器中访问 http://localhost:8080/auth/login")
    print("2. 使用 why/password123 登录")
    print("3. 访问我的作品页面测试按钮功能")
    print("="*60)
    
    return True

if __name__ == "__main__":
    print("🧪 开始测试我的作品页面功能\n")
    test_artwork_functionality()