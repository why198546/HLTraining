#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
端到端测试：完整的视频生成翻译流程
"""

import sys
import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_video_generation_with_translation():
    """测试完整的视频生成翻译流程"""
    
    # 测试用例
    test_cases = [
        {
            "prompt": "小人在花园里跳舞",
            "description": "正常的中文prompt"
        },
        {
            "prompt": "可爱的猫咪在玩耍",
            "description": "动物相关prompt"
        },
        {
            "prompt": "角色击败敌人",
            "description": "包含敏感词的prompt"
        },
        {
            "prompt": "A character dancing in the garden",
            "description": "英文prompt（应该不翻译）"
        }
    ]
    
    print("端到端视频生成翻译测试")
    print("=" * 50)
    
    # 假设Flask应用运行在8080端口
    base_url = "http://localhost:8080"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原始prompt: {test_case['prompt']}")
        
        # 构建请求数据
        data = {
            "session_id": "test_session_123",
            "image_url": "https://example.com/test_image.jpg",
            "prompt": test_case["prompt"],
            "aspect_ratio": "16:9",
            "duration": 8,
            "quality": "720p",
            "motion_intensity": "medium"
        }
        
        try:
            # 发送请求到api/generate-video端点
            response = requests.post(
                f"{base_url}/api/generate-video",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 请求成功")
                print(f"服务器响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: Flask服务器未运行在 {base_url}")
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")
        except Exception as e:
            print(f"❌ 其他错误: {str(e)}")
        
        print("-" * 40)

def check_flask_server():
    """检查Flask服务器状态"""
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    print("检查Flask服务器状态...")
    if check_flask_server():
        print("✅ Flask服务器正在运行")
        test_video_generation_with_translation()
    else:
        print("❌ Flask服务器未运行")
        print("请先启动Flask服务器：")
        print("python app.py")