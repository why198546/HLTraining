#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试具体的翻译案例
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def test_specific_cases():
    """测试具体的翻译案例"""
    
    test_cases = [
        {
            "prompt": "可爱的猫咪在玩耍",
            "expected": "a cute cat playing",
            "description": "你提到的具体例子"
        },
        {
            "prompt": "小人在花园里跳舞",
            "expected": "character dancing in garden",
            "description": "角色动作描述"
        },
        {
            "prompt": "美丽的鸟儿在天空飞翔",
            "expected": "beautiful bird flying in sky",
            "description": "动物飞行描述"
        },
        {
            "prompt": "可爱的小狗在公园里跑步",
            "expected": "cute puppy running in park",
            "description": "小狗跑步描述"
        },
        {
            "prompt": "角色击败敌人后开心地跳舞",
            "expected": "character meeting friend then dancing happily",
            "description": "包含敏感词的描述"
        }
    ]
    
    print("具体翻译案例测试")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["prompt"]
        expected = test_case["expected"]
        
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        print(f"期望结果: {expected}")
        
        # 使用完整的翻译功能（会使用备用翻译）
        result = translate_prompt(original)
        
        print(f"实际结果: {result}")
        
        # 检查关键词是否都包含
        expected_words = expected.lower().replace('a ', '').replace('an ', '').replace('the ', '').split()
        result_words = result.lower().replace('a ', '').replace('an ', '').replace('the ', '').split()
        
        matches = 0
        for word in expected_words:
            if word in result_words:
                matches += 1
        
        accuracy = matches / len(expected_words) * 100 if expected_words else 0
        print(f"关键词匹配度: {accuracy:.1f}%")
        
        if accuracy >= 80:
            print("✅ 翻译质量良好")
        elif accuracy >= 60:
            print("⚠️ 翻译可以接受")
        else:
            print("❌ 翻译需要改进")
        
        print("-" * 50)

if __name__ == "__main__":
    test_specific_cases()