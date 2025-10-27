#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试翻译功能是否正确集成到Flask应用中
"""

import sys
import os
import requests
import json

def test_translation_integration():
    """测试翻译功能集成"""
    
    # 创建一个简单的测试端点来验证翻译
    test_cases = [
        {
            "prompt": "小人在花园里跳舞",
            "expected_contains": ["character", "garden", "danc"]
        },
        {
            "prompt": "角色击败敌人", 
            "expected_contains": ["character", "friend"]  # 敏感词应该被替换
        },
        {
            "prompt": "A character dancing in the garden",
            "expected_contains": ["character", "dancing", "garden"]  # 英文不应该翻译
        }
    ]
    
    print("翻译功能集成测试")
    print("=" * 50)
    
    # 直接测试translate_prompt函数
    sys.path.append('/Users/hongyuwang/code/HLTraining')
    
    try:
        from api.prompt_translator import translate_prompt
        
        for i, test_case in enumerate(test_cases, 1):
            original = test_case["prompt"]
            translated = translate_prompt(original)
            
            print(f"\n测试用例 {i}:")
            print(f"原文: {original}")
            print(f"翻译: {translated}")
            
            # 检查翻译结果
            success = True
            for expected in test_case["expected_contains"]:
                if expected.lower() not in translated.lower():
                    success = False
                    print(f"❌ 缺少预期词汇: {expected}")
            
            if success:
                print("✅ 翻译结果符合预期")
            else:
                print("❌ 翻译结果不符合预期")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ 翻译功能测试失败: {str(e)}")

if __name__ == "__main__":
    test_translation_integration()