#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试对话内容保护功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import re

def debug_dialogue_extraction():
    """调试对话提取功能"""
    
    print("=" * 80)
    print("🔍 对话内容保护调试")
    print("=" * 80)
    
    # 测试各种引号格式
    test_cases = [
        '奥特曼发射淬斯蒂姆光线，打败了怪兽。对着屏幕说道："王爷小怪兽，你相信光么？"',
        '角色说道："你好世界"',
        '角色说道："你好世界"',  # 不同的引号
        '角色说道:"你好世界"',   # 英文引号
        '角色说道：\"你好世界\"', # 转义引号
        '角色问道："这是什么？"',
        '小明写道："今天很开心"'
    ]
    
    # 当前的正则表达式
    dialogue_pattern = r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]'
    
    print("📝 当前正则表达式:")
    print(f"   {dialogue_pattern}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 测试用例 {i}:")
        print(f"   文本: {test_case}")
        
        # 尝试匹配
        matches = list(re.finditer(dialogue_pattern, test_case))
        
        if matches:
            print(f"   ✅ 匹配成功: {len(matches)}个对话")
            for j, match in enumerate(matches):
                print(f"      对话{j+1}: 引导词='{match.group(1)}' 内容='{match.group(2)}'")
        else:
            print(f"   ❌ 匹配失败")
            
            # 尝试分析问题
            print("   🔍 问题分析:")
            
            # 检查是否有引导词
            guide_words = re.findall(r'[说写喊问答叫唱念读]道', test_case)
            if guide_words:
                print(f"      找到引导词: {guide_words}")
            else:
                print("      未找到引导词")
            
            # 检查引号类型
            quote_types = []
            if '"' in test_case: quote_types.append('中文左引号"')
            if '"' in test_case: quote_types.append('中文右引号"')
            if '"' in test_case: quote_types.append('英文引号"')
            if "'" in test_case: quote_types.append("英文单引号'")
            if '\\"' in test_case: quote_types.append('转义双引号\\"')
            
            if quote_types:
                print(f"      找到引号类型: {quote_types}")
            else:
                print("      未找到引号")
        
        print()
    
    # 测试改进的正则表达式
    print("🔧 改进方案测试:")
    print("-" * 50)
    
    # 更全面的引号匹配
    improved_pattern = r'([说写喊问答叫唱念读]道[:：]?)\s*["""\'\'\"](.*?)["""\'\'\""]'
    
    print(f"改进正则: {improved_pattern}")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 改进测试 {i}: {test_case}")
        
        matches = list(re.finditer(improved_pattern, test_case))
        
        if matches:
            print(f"   ✅ 改进匹配成功: {len(matches)}个对话")
            for j, match in enumerate(matches):
                print(f"      对话{j+1}: 引导词='{match.group(1)}' 内容='{match.group(2)}'")
        else:
            print(f"   ❌ 改进匹配仍失败")
        print()

if __name__ == "__main__":
    debug_dialogue_extraction()