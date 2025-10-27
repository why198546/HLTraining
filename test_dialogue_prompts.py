#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试包含对话引导词的prompt翻译效果
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def test_dialogue_prompts():
    """测试包含对话的prompt"""
    
    test_cases = [
        {
            "prompt": '小女孩在花园里玩耍，突然说道："妈妈，快来看这朵美丽的花！"',
            "description": "小女孩说道 - 简单对话"
        },
        {
            "prompt": '老师在黑板上写道："今天我们学习画画"，学生们都很兴奋',
            "description": "老师写道 - 教学场景"
        },
        {
            "prompt": '小猫咪看到主人回家，高兴地喊道："喵喵喵！"然后跑过去',
            "description": "小猫喊道 - 动物表达"
        },
        {
            "prompt": '医生检查完病人后，温和地说道："你的身体很健康，不用担心。"',
            "description": "医生说道 - 专业场景"
        },
        {
            "prompt": '孩子问道："为什么天空是蓝色的？"妈妈耐心地解释',
            "description": "孩子问道 - 好奇提问"
        },
        {
            "prompt": '歌手在舞台上唱道："这是一首关于梦想的歌"，观众热烈鼓掌',
            "description": "歌手唱道 - 艺术表演"
        },
        {
            "prompt": '爷爷慢慢地念道："从前有一个美丽的公主..."，孙子认真听着',
            "description": "爷爷念道 - 讲故事"
        },
        {
            "prompt": '小人在森林里迷路了，大声叫道："有人吗？请帮帮我！"',
            "description": "角色叫道 - 求助场景"
        }
    ]
    
    print("包含对话引导词的prompt翻译测试")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["prompt"]
        
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        
        # 使用完整的翻译功能
        result = translate_prompt(original)
        
        print(f"翻译结果: {result}")
        
        # 检查对话是否被保护
        import re
        dialogue_matches = re.findall(r'["""\'\'](.*?)["""\'\'"]', original)
        
        if dialogue_matches:
            all_preserved = True
            for dialogue in dialogue_matches:
                if dialogue not in result:
                    all_preserved = False
                    print(f"❌ 对话内容丢失: \"{dialogue}\"")
            
            if all_preserved:
                print("✅ 对话内容完全保护")
            
            # 检查引导词是否保留
            guide_words = re.findall(r'([说写喊问答叫唱念读]道)', original)
            if guide_words:
                guide_preserved = all(word in result for word in guide_words)
                if guide_preserved:
                    print("✅ 引导词完全保留")
                else:
                    print("⚠️ 部分引导词可能丢失")
        else:
            print("ℹ️ 未检测到对话内容")
        
        # 检查非对话部分是否被翻译
        has_chinese_non_dialogue = False
        non_dialogue_text = original
        for match in re.finditer(r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]', original):
            non_dialogue_text = non_dialogue_text.replace(match.group(0), '')
        
        if re.search(r'[\u4e00-\u9fff]', non_dialogue_text):
            has_chinese_non_dialogue = True
        
        if has_chinese_non_dialogue:
            # 检查是否有英文翻译
            has_english = bool(re.search(r'[a-zA-Z]', result))
            if has_english:
                print("✅ 非对话部分已翻译为英文")
            else:
                print("⚠️ 非对话部分未翻译")
        
        print("-" * 60)

if __name__ == "__main__":
    test_dialogue_prompts()