#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
返回翻译后的prompt - 用于用户确认
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def show_translation_result():
    """显示翻译结果供用户确认"""
    
    print("=" * 80)
    print("📋 Prompt翻译结果确认")
    print("=" * 80)
    
    # 从用户描述中推测的原始prompt
    original_prompt = '奥特曼发射淬斯蒂姆光线，打败了怪兽。对着屏幕说道："王爷小怪兽，你相信光么？"'
    
    print("🔤 原始中文Prompt:")
    print(f"   {original_prompt}")
    print()
    
    print("🌐 开始翻译...")
    result = translate_prompt(original_prompt)
    print()
    
    print("✅ 翻译后的英文Prompt:")
    print(f"   {result}")
    print()
    
    print("🔍 翻译效果分析:")
    print("-" * 50)
    
    # 检查对话保护
    if "王爷小怪兽，你相信光么？" in result:
        print("✅ 对话内容保护: 中文对话完整保留")
        print(f"   保护内容: \"王爷小怪兽，你相信光么？\"")
    else:
        print("❌ 对话内容保护: 中文对话可能被翻译")
    
    # 检查引导词翻译
    if "saying in Chinese" in result:
        print("✅ 引导词翻译: 说道 → saying in Chinese")
    else:
        print("❌ 引导词翻译: 未正确翻译")
    
    # 检查非对话部分翻译
    non_dialogue_parts = ["奥特曼", "淬斯蒂姆光线", "怪兽", "屏幕"]
    translated_parts = []
    for part in non_dialogue_parts:
        if part not in result:  # 如果中文不在结果中，说明被翻译了
            translated_parts.append(part)
    
    if translated_parts:
        print(f"✅ 非对话翻译: {len(translated_parts)}/{len(non_dialogue_parts)}个中文词汇被翻译")
    else:
        print("⚠️ 非对话翻译: 部分中文词汇可能未翻译")
    
    print()
    print("📤 最终用于视频生成的Prompt:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return result

if __name__ == "__main__":
    final_prompt = show_translation_result()
    
    print("\n🎬 接下来可以使用此Prompt生成视频")
    print("   请确认翻译结果是否符合预期")
    print("   如有问题请告诉我具体需要调整的地方")