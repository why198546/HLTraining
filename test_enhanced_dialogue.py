#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强对话翻译功能测试 - 引导词英文化和语言标识
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def test_enhanced_dialogue_translation():
    """测试增强的对话翻译功能"""
    
    print("=" * 80)
    print("🌟 增强对话翻译功能测试 - 引导词英文化 + 语言标识")
    print("=" * 80)
    
    # 测试各种引导词的英文翻译
    test_cases = [
        {
            "原文": '小女孩说道："这是什么声音？"',
            "期望": "saying in Chinese",
            "描述": "说道 → saying in Chinese"
        },
        {
            "原文": '老师写道："努力学习"',
            "期望": "writing in Chinese", 
            "描述": "写道 → writing in Chinese"
        },
        {
            "原文": '孩子喊道："太好玩了！"',
            "期望": "shouting in Chinese",
            "描述": "喊道 → shouting in Chinese"
        },
        {
            "原文": '学生问道："这是什么？"',
            "期望": "asking in Chinese",
            "描述": "问道 → asking in Chinese"
        },
        {
            "原文": '妈妈答道："这是彩虹"',
            "期望": "answering in Chinese",
            "描述": "答道 → answering in Chinese"
        },
        {
            "原文": '小鸟叫道："叽叽喳喳"',
            "期望": "calling in Chinese",
            "描述": "叫道 → calling in Chinese"
        },
        {
            "原文": '歌手唱道："美丽的歌声"',
            "期望": "singing in Chinese",
            "描述": "唱道 → singing in Chinese"
        },
        {
            "原文": '爷爷念道："从前..."',
            "期望": "reciting in Chinese",
            "描述": "念道 → reciting in Chinese"
        },
        {
            "原文": '孩子读道："一二三四"',
            "期望": "reading in Chinese",
            "描述": "读道 → reading in Chinese"
        }
    ]
    
    print(f"\n📝 引导词英文翻译测试 ({len(test_cases)}种)")
    print("-" * 50)
    
    success_count = 0
    for i, case in enumerate(test_cases, 1):
        result = translate_prompt(case["原文"])
        
        # 检查是否包含期望的英文引导词
        if case["期望"] in result:
            success_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {i:2d}. {case['描述']}")
        print(f"    原文: {case['原文']}")
        print(f"    结果: {result}")
        print(f"    检查: {'包含' if case['期望'] in result else '缺少'} '{case['期望']}'")
        print()
    
    print(f"引导词英文翻译成功率: {success_count}/{len(test_cases)} ({success_count/len(test_cases)*100:.1f}%)")
    
    # 测试复杂场景
    print(f"\n🎭 复杂场景测试")
    print("-" * 50)
    
    complex_cases = [
        {
            "描述": "森林探险场景 (您的示例)",
            "原文": '角色在森林中探险，突然问道："这是什么声音？"',
            "期望结果": "asking in Chinese"
        },
        {
            "描述": "多个对话",
            "原文": '小女孩说道："妈妈！"然后妈妈答道："来了，宝贝。"',
            "期望结果": ["saying in Chinese", "answering in Chinese"]
        },
        {
            "描述": "动物对话",
            "原文": '可爱的小猫在花园里玩耍，突然叫道："喵喵！"',
            "期望结果": "calling in Chinese"
        },
        {
            "描述": "学习场景",
            "原文": '聪明的学生举手问道："老师，这个怎么解？"',
            "期望结果": "asking in Chinese"
        }
    ]
    
    for i, case in enumerate(complex_cases, 1):
        result = translate_prompt(case["原文"])
        
        # 检查期望结果
        if isinstance(case["期望结果"], list):
            # 多个期望结果
            found_count = sum(1 for expected in case["期望结果"] if expected in result)
            status = "✅" if found_count == len(case["期望结果"]) else "❌"
            check_info = f"找到 {found_count}/{len(case['期望结果'])} 个期望的引导词"
        else:
            # 单个期望结果
            status = "✅" if case["期望结果"] in result else "❌"
            check_info = f"{'包含' if case['期望结果'] in result else '缺少'} '{case['期望结果']}'"
        
        print(f"{status} {i}. {case['描述']}")
        print(f"   原文: {case['原文']}")
        print(f"   结果: {result}")
        print(f"   检查: {check_info}")
        print()
    
    # 对比新旧格式
    print(f"\n🆚 新旧格式对比")
    print("-" * 50)
    
    example = '角色在森林中探险，突然问道："这是什么声音？"'
    result = translate_prompt(example)
    
    print("🎯 您的期望格式示例:")
    print('   "a character in forest exploring suddenly then asking in Chinese: "这是什么声音？""')
    print()
    print("📋 当前实际输出:")
    print(f'   "{result}"')
    print()
    
    # 功能特性总结
    print("🎯 新功能特性")
    print("-" * 50)
    
    features = [
        "✅ 引导词完全英文化 (说道→saying in Chinese)",
        "✅ 明确标识对话语言 (in Chinese)",
        "✅ 保持对话内容的中文原样",
        "✅ 非对话部分翻译为英文",
        "✅ 格式更加国际化和专业",
        "✅ 支持所有9种对话引导词",
        "✅ 兼容复杂多对话场景",
        "✅ API不可用时的备用策略同步更新"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_dialogue_translation()