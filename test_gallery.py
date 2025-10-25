#!/usr/bin/env python3
"""
简单的gallery测试
"""
import requests
import json

def test_gallery():
    """测试gallery页面"""
    try:
        response = requests.get('http://127.0.0.1:8080/gallery', timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Gallery页面加载成功")
            if "测试作品" in response.text:
                print("✅ 找到测试作品")
            print(f"响应长度: {len(response.text)} 字符")
        else:
            print(f"❌ Gallery页面错误: {response.status_code}")
            print(f"错误内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")

if __name__ == '__main__':
    test_gallery()