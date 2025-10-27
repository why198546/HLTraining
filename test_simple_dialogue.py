#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_dialogue_detection():
    """测试对话检测功能"""
    from api.prompt_translator import PromptTranslator
    
    # 测试提示词
    test_prompt = '奥特曼发射捷德力姆光线，击败了怪兽。他转向镜头说道："无礼的怪兽，你拥抱光明吗？"'
    
    print(f"测试提示词: {test_prompt}")
    
    # 创建翻译器实例（不初始化API）
    translator = PromptTranslator.__new__(PromptTranslator)
    
    # 测试对话检测
    has_dialogue, non_dialogue_text, dialogues = translator.extract_dialogue_content(test_prompt)
    
    print(f"是否包含对话: {has_dialogue}")
    print(f"非对话部分: {non_dialogue_text}")
    print(f"对话数量: {len(dialogues)}")
    
    for i, dialogue in enumerate(dialogues):
        print(f"对话{i+1}: {dialogue}")

if __name__ == "__main__":
    test_dialogue_detection()