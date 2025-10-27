#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试改进的备用翻译功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import PromptTranslator

def test_fallback_translation():
    """测试备用翻译功能"""
    # 直接测试备用翻译方法，不需要API密钥
    translator = PromptTranslator.__new__(PromptTranslator)
    
    # 测试不同类型的中文prompt
    test_cases = [
        "小人在花园里跳舞",
        "可爱的猫咪在玩耍", 
        "人物快速跑步",
        "角色击败敌人",  # 包含敏感词
        "美丽的鸟儿在天空飞翔",
        "神秘的角色在森林里探险",  # 包含不在字典中的词汇
        "愤怒的战士拿着武器"  # 多个敏感词
    ]
    
    print("测试备用翻译功能:")
    print("=" * 50)
    
    for prompt in test_cases:
        result = translator._simple_translation_fallback(prompt)
        print(f"原文: {prompt}")
        print(f"翻译: {result}")
        print("-" * 30)

if __name__ == "__main__":
    test_fallback_translation()