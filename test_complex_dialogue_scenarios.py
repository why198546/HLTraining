#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试复杂对话场景的prompt翻译效果
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def test_complex_dialogue_scenarios():
    """测试复杂对话场景"""
    
    complex_test_cases = [
        {
            "prompt": '小女孩说道："今天天气真好！"然后妈妈回答道："是的，我们去公园玩吧。"',
            "description": "多个对话 - 母女对话"
        },
        {
            "prompt": '可爱的猫咪在花园里玩耍，看到蝴蝶时喊道："喵！"然后追着蝴蝶跑',
            "description": "动物对话 + 动作描述"
        },
        {
            "prompt": '老师写道："2+2=4"，学生高兴地说道："我知道答案！"老师微笑着点头',
            "description": "教学场景 - 师生互动"
        },
        {
            "prompt": '角色击败敌人后，胜利地喊道："正义必胜！"然后帮助受伤的村民',
            "description": "包含敏感词 + 对话"
        },
        {
            "prompt": '歌手在舞台上唱道："这是我的梦想之歌"，观众们齐声喊道："太棒了！"',
            "description": "艺术表演 - 双重对话"
        },
        {
            "prompt": '小人在森林里探险，突然问道："这是什么声音？"然后小心翼翼地前进',
            "description": "冒险场景 + 自问"
        }
    ]
    
    print("复杂对话场景prompt翻译测试")
    print("=" * 70)
    
    for i, test_case in enumerate(complex_test_cases, 1):
        original = test_case["prompt"]
        
        print(f"\n测试用例 {i}: {test_case['description']}")
        print(f"原文: {original}")
        
        # 使用完整的翻译功能
        result = translate_prompt(original)
        
        print(f"翻译结果: {result}")
        
        # 分析对话保护情况
        import re
        dialogue_matches = re.findall(r'["""\'\'](.*?)["""\'\'"]', original)
        guide_words = re.findall(r'([说写喊问答叫唱念读]道)', original)
        
        print(f"检测到 {len(dialogue_matches)} 个对话, {len(guide_words)} 个引导词")
        
        # 检查对话保护
        if dialogue_matches:
            protected_count = 0
            for dialogue in dialogue_matches:
                if dialogue in result:
                    protected_count += 1
                else:
                    print(f"❌ 对话内容丢失: \"{dialogue}\"")
            
            print(f"✅ 对话保护率: {protected_count}/{len(dialogue_matches)} ({protected_count/len(dialogue_matches)*100:.1f}%)")
        
        # 检查引导词保护
        if guide_words:
            preserved_count = 0
            for word in guide_words:
                if word in result:
                    preserved_count += 1
            
            print(f"✅ 引导词保护率: {preserved_count}/{len(guide_words)} ({preserved_count/len(guide_words)*100:.1f}%)")
        
        # 检查翻译质量
        non_dialogue_parts = []
        temp_text = original
        for match in re.finditer(r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]', original):
            temp_text = temp_text.replace(match.group(0), ' [DIALOGUE] ')
        
        # 移除标点符号，检查是否有中文
        clean_text = re.sub(r'[，。！？；：]', '', temp_text)
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', clean_text))
        has_english = bool(re.search(r'[a-zA-Z]', result))
        
        if has_chinese and has_english:
            print("✅ 非对话部分成功翻译")
        elif not has_chinese:
            print("ℹ️ 原文主要为对话内容")
        else:
            print("⚠️ 非对话部分翻译可能不完整")
        
        print("-" * 60)

if __name__ == "__main__":
    test_complex_dialogue_scenarios()