#!/usr/bin/env python3

import re

def test_dialogue_pattern(text):
    dialogue_pattern = r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]'
    
    print(f'测试文本: {text}')
    print(f'正则表达式: {dialogue_pattern}')
    
    matches = list(re.finditer(dialogue_pattern, text))
    print(f'匹配数量: {len(matches)}')
    
    for i, match in enumerate(matches):
        print(f'匹配 {i+1}: "{match.group(0)}"')
        print(f'  引导词: "{match.group(1)}"')
        print(f'  内容: "{match.group(2)}"')
    print()

if __name__ == "__main__":
    # 测试实际的浏览器输入
    browser_text = '奥特曼发射泽斯蒂姆光线，打败了怪兽。对着屏幕说道："王备小怪兽，你相信光么？"'
    print("=== 测试浏览器实际输入 ===")
    test_dialogue_pattern(browser_text)
    
    print("="*50)
    
    # 测试我们之前成功的文本
    test_text = '奥特曼发出泽斯蒂姆光线，击败了怪兽。面对镜头，他说道："勇敢的怪兽啊，你相信光吗？"'
    print("=== 测试之前成功的文本 ===")
    test_dialogue_pattern(test_text)