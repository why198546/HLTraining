#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试对话内容保护功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import PromptTranslator

def test_dialogue_protection():
    """测试对话内容保护功能"""
    
    # 创建翻译器实例但不初始化（测试备用功能）
    translator = PromptTranslator.__new__(PromptTranslator)
    
    test_cases = [
        {
            "prompt": "小人在花园里跳舞，他说道："今天天气真好！"",
            "description": "包含说道的对话"
        },
        {
            "prompt": "角色击败敌人后，喊道："胜利了！"然后开心地跳舞",
            "description": "包含喊道的对话和敏感词"
        },
        {
            "prompt": "老师写道："请认真完成作业"，学生们认真听着",
            "description": "包含写道的对话"
        },
        {
            "prompt": "小女孩问道："妈妈，我们什么时候回家？"妈妈温柔地回答",
            "description": "包含问道的对话"
        },
        {
            "prompt": "歌手唱道："这是一首美丽的歌"，观众们热烈鼓掌",
            "description": "包含唱道的对话"
        },
        {
            "prompt": "小人在花园里跳舞",
            "description": "不包含对话的普通prompt"
        },
        {
            "prompt": "A character dancing in the garden saying \"Hello world!\"",
            "description": "英文prompt with dialogue"
        }
    ]
    
    print("对话内容保护功能测试")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["prompt"]
        
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        
        # 测试对话检测
        has_dialogue, non_dialogue_text, dialogues = translator.extract_dialogue_content(original)
        
        print(f"是否包含对话: {has_dialogue}")
        if has_dialogue:
            print(f"非对话部分: '{non_dialogue_text}'")
            print(f"对话列表:")
            for j, dialogue in enumerate(dialogues):
                print(f"  对话{j+1}: {dialogue['intro']} \"{dialogue['content']}\"")
        
        # 测试翻译结果
        if translator.is_chinese_text(original):
            translated = translator._simple_translation_fallback(original)
        else:
            translated = original
            
        print(f"翻译结果: {translated}")
        
        # 验证对话是否被保护
        if has_dialogue:
            all_dialogues_preserved = True
            for dialogue in dialogues:
                if dialogue['content'] not in translated:
                    all_dialogues_preserved = False
                    print(f"❌ 对话内容丢失: \"{dialogue['content']}\"")
            
            if all_dialogues_preserved:
                print("✅ 所有对话内容都被保护")
            else:
                print("❌ 部分对话内容丢失")
        else:
            print("ℹ️ 无对话内容需要保护")
        
        print("-" * 50)

if __name__ == "__main__":
    test_dialogue_protection()