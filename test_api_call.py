#!/usr/bin/env python3
"""
直接测试API调用，检查提示词传递
"""

import requests
import json

def test_api_call():
    """测试API调用"""
    print("🧪 测试API调用...")
    
    url = "http://localhost:8080/api/generate"
    
    # 测试数据
    data = {
        'prompt': '一个勇敢的奥特曼战士，身穿银色和红色战斗服，胸前有彩色计时器，双手摆出战斗姿势，背景是蓝天白云',
        'style': 'cute',
        'color_preference': 'colorful',
        'expert_mode': 'false',
        'aspect_ratio': '9:16'
    }
    
    print(f"📝 发送请求: {data}")
    
    try:
        response = requests.post(url, data=data)
        print(f"🔍 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 响应结果: {result}")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_api_call()