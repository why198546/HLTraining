#!/usr/bin/env python3
"""
测试我的作品页面功能
"""

import requests
import json

def test_my_artworks():
    """测试我的作品页面"""
    base_url = "http://127.0.0.1:8080"
    
    # 创建session来保持登录状态
    session = requests.Session()
    
    print("🔍 测试我的作品页面功能...")
    
    # 1. 首先登录
    print("1. 尝试登录...")
    login_data = {
        'username': 'why',
        'password': '123456'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    print(f"   登录响应状态: {login_response.status_code}")
    
    if login_response.status_code == 302:
        print("   ✅ 登录成功，重定向到主页")
    
    # 2. 测试我的作品页面
    print("2. 访问我的作品页面...")
    artworks_response = session.get(f"{base_url}/auth/my-artworks")
    print(f"   我的作品页面状态: {artworks_response.status_code}")
    
    if artworks_response.status_code == 200:
        print("   ✅ 我的作品页面加载成功")
        # 检查页面内容是否包含关键词
        if "测试作品" in artworks_response.text:
            print("   ✅ 发现测试作品")
        if "推荐" in artworks_response.text or "featured" in artworks_response.text:
            print("   ✅ 推荐功能显示正常")
    else:
        print(f"   ❌ 我的作品页面加载失败: {artworks_response.status_code}")
        print(f"   错误内容: {artworks_response.text[:200]}...")
    
    # 3. 测试用户资料页面
    print("3. 访问用户资料页面...")
    profile_response = session.get(f"{base_url}/auth/profile")
    print(f"   用户资料页面状态: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        print("   ✅ 用户资料页面加载成功")
    else:
        print(f"   ❌ 用户资料页面加载失败: {profile_response.status_code}")
        print(f"   错误内容: {profile_response.text[:200]}...")
    
    # 4. 测试作品画廊页面
    print("4. 访问作品画廊页面...")
    gallery_response = session.get(f"{base_url}/gallery")
    print(f"   作品画廊页面状态: {gallery_response.status_code}")
    
    if gallery_response.status_code == 200:
        print("   ✅ 作品画廊页面加载成功")
        if "测试作品" in gallery_response.text:
            print("   ✅ 发现推荐作品展示")
    else:
        print(f"   ❌ 作品画廊页面加载失败: {gallery_response.status_code}")
        print(f"   错误内容: {gallery_response.text[:200]}...")
    
    print("\n🎉 测试完成！")

if __name__ == '__main__':
    test_my_artworks()