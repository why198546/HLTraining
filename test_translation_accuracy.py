#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试具体的翻译准确性
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import PromptTranslator

def test_translation_accuracy():
    """测试翻译准确性"""
    
    # 创建翻译器实例（测试备用功能）
    translator = PromptTranslator.__new__(PromptTranslator)
    
    test_cases = [
        {
            "prompt": "可爱的猫咪在玩耍",
            "expected": "a cute cat playing",
            "description": "简单的猫咪描述"
        },
        {
            "prompt": "小人在花园里跳舞",
            "expected": "character dancing in garden",
            "description": "角色动作描述"
        },
        {
            "prompt": "美丽的鸟儿在天空飞翔",
            "expected": "beautiful bird flying in sky",
            "description": "动物动作描述"
        }
    ]
    
    print("翻译准确性测试")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["prompt"]
        expected = test_case["expected"]
        
        # 测试当前的备用翻译
        result = translator._translate_non_dialogue_fallback(original)
        
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        print(f"当前结果: {result}")
        print(f"期望结果: {expected}")
        
        # 简单的准确性检查
        original_words = original.replace('的', '').replace('在', '').replace('里', '')
        expected_words = expected.split()
        result_words = result.lower().split()
        
        matches = 0
        for word in expected_words:
            if word in result_words or any(word in rw for rw in result_words):
                matches += 1
        
        accuracy = matches / len(expected_words) * 100
        print(f"匹配度: {accuracy:.1f}%")
        
        if accuracy >= 80:
            print("✅ 翻译准确")
        else:
            print("❌ 翻译需要优化")
        
        print("-" * 40)

if __name__ == "__main__":
    test_translation_accuracy()