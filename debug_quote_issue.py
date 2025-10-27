#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 测试文本
test_text = '奥特曼发射泽斯蒂姆光线，打败了怪兽。对着屏幕说道："王备小怪兽，你相信光么？"'

print(f"测试文本: {test_text}")
print(f"文本长度: {len(test_text)}")

# 检查引号字符
quote_chars = ['"', '"', '"', "'", "'"]
for i, char in enumerate(test_text):
    if char in quote_chars:
        print(f"位置 {i}: '{char}' (Unicode: {ord(char)})")

print("\n--- 测试不同的正则表达式 ---")

# 原始正则
pattern1 = r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]'
matches1 = re.findall(pattern1, test_text)
print(f"原始正则: {pattern1}")
print(f"匹配结果: {matches1}")

# 简化正则 - 只匹配英文引号
pattern2 = r'([说写喊问答叫唱念读]道[:：])\s*"(.*?)"'
matches2 = re.findall(pattern2, test_text)
print(f"英文引号正则: {pattern2}")
print(f"匹配结果: {matches2}")

# 测试具体的"说道："部分
pattern3 = r'说道[:：]\s*"(.*?)"'
matches3 = re.findall(pattern3, test_text)
print(f"说道正则: {pattern3}")
print(f"匹配结果: {matches3}")

# 最简单的测试
if '说道："' in test_text:
    print("✅ 文本确实包含 '说道：\"'")
else:
    print("❌ 文本不包含 '说道：\"'")