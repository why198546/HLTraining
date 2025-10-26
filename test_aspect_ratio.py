#!/usr/bin/env python3
"""
测试新的高宽比功能
"""

import requests
import json
import time

def test_aspect_ratio_functionality():
    """测试高宽比功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试高宽比功能...")
    
    # 测试不同的高宽比
    test_cases = [
        {
            "prompt": "一只可爱的小猫咪在花园里玩耍",
            "aspect_ratio": "1:1",
            "expected": "正方形"
        },
        {
            "prompt": "美丽的山水风景画",
            "aspect_ratio": "16:9", 
            "expected": "宽屏"
        },
        {
            "prompt": "高大的树木",
            "aspect_ratio": "9:16",
            "expected": "竖屏"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['expected']} ({test_case['aspect_ratio']})")
        print(f"Prompt: {test_case['prompt']}")
        
        # 准备表单数据
        data = {
            'prompt': test_case['prompt'],
            'style': 'cute',
            'color_preference': 'colorful',
            'expert_mode': 'false',
            'aspect_ratio': test_case['aspect_ratio']
        }
        
        try:
            print("🚀 发送生成请求...")
            response = requests.post(f"{base_url}/generate-image", data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 测试用例 {i} 成功!")
                    print(f"生成的图片: {result.get('image_path', 'N/A')}")
                    print(f"高宽比: {test_case['aspect_ratio']} - {test_case['expected']}")
                else:
                    print(f"❌ 测试用例 {i} 失败: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ 测试用例 {i} HTTP错误: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试用例 {i} 异常: {str(e)}")
        
        # 等待一下避免API限制
        if i < len(test_cases):
            print("⏳ 等待3秒...")
            time.sleep(3)
    
    print("\n🎉 高宽比功能测试完成!")

if __name__ == "__main__":
    test_aspect_ratio_functionality()