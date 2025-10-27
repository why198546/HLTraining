#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的奥特曼prompt
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.prompt_translator import translate_prompt

def test_new_ultraman_prompt():
    """测试新的奥特曼prompt"""
    
    print("=" * 80)
    print("🧪 测试新的奥特曼Prompt")
    print("=" * 80)
    
    test_prompt = '奥特曼发射泽斯蒂姆光线，打败了怪兽。对着屏幕说道："王备小怪兽，你相信光么？"'
    
    print("🔤 原始Prompt:")
    print(f"   {test_prompt}")
    print()
    
    print("🌐 开始翻译...")
    result = translate_prompt(test_prompt)
    print()
    
    print("✅ 翻译结果:")
    print(f"   {result}")
    print()
    
    print("🔍 详细分析:")
    print("-" * 50)
    
    # 检查各个部分的翻译
    analysis = [
        ("奥特曼", "Ultraman", "Ultraman" in result),
        ("发射", "shooting", "shooting" in result),
        ("泽斯蒂姆光线", "Zestium beam/beam", "beam" in result),
        ("打败", "defeating", "defeating" in result),
        ("怪兽", "monster", "monster" in result),
        ("对着屏幕", "facing screen", "facing screen" in result),
        ("说道", "saying in Chinese", "saying in Chinese" in result),
        ("对话内容", "王备小怪兽，你相信光么？", "王备小怪兽，你相信光么？" in result)
    ]
    
    success_count = 0
    for chinese, english, is_correct in analysis:
        status = "✅" if is_correct else "❌"
        success_count += 1 if is_correct else 0
        print(f"{status} {chinese} → {english}")
    
    print()
    print(f"📊 翻译准确率: {success_count}/{len(analysis)} ({success_count/len(analysis)*100:.1f}%)")
    print()
    
    # 对比不同版本的光线名称
    print("🔧 光线名称对比:")
    print("-" * 30)
    print("  之前: 淬斯蒂姆光线 → Zestium beam")
    print("  现在: 泽斯蒂姆光线 → ?")
    
    if "泽斯蒂姆" in result:
        print("  ⚠️  新光线名称未添加到词典，保持中文")
    elif "beam" in result:
        print("  ✅ 被翻译为通用的 beam")
    else:
        print("  ❓ 光线翻译状态未知")
    
    print()
    print("📤 最终用于视频生成的Prompt:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return result

if __name__ == "__main__":
    test_new_ultraman_prompt()