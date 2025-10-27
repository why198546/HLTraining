#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试备用翻译功能的实际效果
"""

import sys
import os

def test_fallback_translation_integration():
    """测试备用翻译功能的集成效果"""
    
    sys.path.append('/Users/hongyuwang/code/HLTraining')
    
    # 导入翻译器
    from api.prompt_translator import PromptTranslator
    
    # 创建翻译器实例但不初始化（模拟API不可用的情况）
    translator = PromptTranslator.__new__(PromptTranslator)
    
    test_cases = [
        {
            "prompt": "小人在花园里跳舞",
            "description": "正常的中文prompt"
        },
        {
            "prompt": "角色击败敌人", 
            "description": "包含敏感词的prompt"
        },
        {
            "prompt": "可爱的猫咪在玩耍",
            "description": "动物相关prompt"
        },
        {
            "prompt": "愤怒的战士拿着武器",
            "description": "多个敏感词的prompt"
        },
        {
            "prompt": "A character dancing in the garden",
            "description": "英文prompt（不需要翻译）"
        }
    ]
    
    print("备用翻译功能集成测试")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["prompt"]
        
        # 测试中文检测
        is_chinese = translator.is_chinese_text(original)
        
        if is_chinese:
            translated = translator._simple_translation_fallback(original)
        else:
            translated = original
            
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        print(f"是否包含中文: {is_chinese}")
        print(f"翻译结果: {translated}")
        
        # 检查翻译质量
        if is_chinese:
            # 对于中文，检查是否成功转换为安全的英文描述
            if translator.is_chinese_text(translated):
                print("⚠️ 翻译后仍包含中文")
            else:
                print("✅ 成功转换为英文")
        else:
            # 对于英文，应该保持不变
            if translated == original:
                print("✅ 英文内容保持不变")
            else:
                print("⚠️ 英文内容被意外修改")
        
        print("-" * 40)

if __name__ == "__main__":
    test_fallback_translation_integration()