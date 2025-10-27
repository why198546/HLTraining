#!/usr/bin/env python3
import re

def extract_dialogue_content(text: str):
    # 匹配"说道/写道/喊道/问道/答道等："或"："后面的引号内容
    # 支持中文引号""和英文引号""
    dialogue_pattern = r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]'
    
    dialogues = []
    dialogue_matches = list(re.finditer(dialogue_pattern, text))
    
    print(f'正则表达式: {dialogue_pattern}')
    print(f'匹配结果数量: {len(dialogue_matches)}')
    
    for i, match in enumerate(dialogue_matches):
        print(f'匹配 {i+1}: {match.group(0)}')
        print(f'  引导词: {match.group(1)}')
        print(f'  内容: {match.group(2)}')
    
    return len(dialogue_matches) > 0

if __name__ == "__main__":
    test_prompt = '奥特曼发出泽斯蒂姆光线，击败了怪兽。面对镜头，他说道："勇敢的怪兽啊，你相信光吗？"'
    print('测试文本:', test_prompt)
    print('结果:', extract_dialogue_content(test_prompt))