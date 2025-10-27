#!/usr/bin/env python3

# 模拟 translate_to_english 方法的逻辑
import re

def is_chinese_text(text: str) -> bool:
    """检测文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def extract_dialogue_content(text: str):
    """提取对话内容，返回(是否包含对话, 非对话部分, 对话部分列表)"""
    
    # 匹配"说道/写道/喊道/问道/答道等："或"："后面的引号内容
    # 支持中文引号""和英文引号""
    dialogue_pattern = r'([说写喊问答叫唱念读]道[:：])\s*["""\'\'](.*?)["""\'\'"]'
    
    dialogues = []
    dialogue_matches = list(re.finditer(dialogue_pattern, text))
    
    if not dialogue_matches:
        return False, text, []
    
    # 中文引导词到英文的映射
    guide_word_mapping = {
        '说道': 'saying in Chinese',
        '写道': 'writing in Chinese',
        '喊道': 'shouting in Chinese',
        '问道': 'asking in Chinese',
        '答道': 'answering in Chinese',
        '叫道': 'calling in Chinese',
        '唱道': 'singing in Chinese',
        '念道': 'reciting in Chinese',
        '读道': 'reading in Chinese'
    }
    
    # 提取对话内容
    for match in dialogue_matches:
        chinese_intro = match.group(1)
        # 移除可能的冒号
        clean_intro = chinese_intro.replace(':', '').replace('：', '')
        english_intro = guide_word_mapping.get(clean_intro, f'{clean_intro} in Chinese')
        
        dialogues.append({
            'full_match': match.group(0),
            'intro': chinese_intro,
            'english_intro': english_intro,
            'content': match.group(2),
            'start': match.start(),
            'end': match.end()
        })
    
    # 移除对话内容，只保留非对话部分用于翻译
    non_dialogue_text = text
    # 先按位置排序，从后往前删除，避免位置偏移
    sorted_dialogues = sorted(dialogues, key=lambda x: x['start'], reverse=True)
    for dialogue in sorted_dialogues:
        non_dialogue_text = non_dialogue_text[:dialogue['start']] + non_dialogue_text[dialogue['end']:]
    
    # 清理非对话文本中的多余空格和标点
    non_dialogue_text = re.sub(r'\s*[，,]\s*', ' ', non_dialogue_text)  # 移除孤立的逗号
    non_dialogue_text = re.sub(r'\s+', ' ', non_dialogue_text)  # 合并多个空格
    
    return True, non_dialogue_text.strip(), dialogues

def mock_translate_text_with_gemini(text: str) -> str:
    """模拟Gemini API翻译 - 这里会翻译所有内容"""
    print(f"🤖 模拟Gemini API收到翻译请求: '{text}'")
    
    # 模拟Gemini会翻译所有内容，包括对话
    if "勇敢的怪兽啊，你相信光吗？" in text:
        return "Ultraman unleashes the Zestium Ray, defeating the Kaiju. Looking directly at the camera, he says: \"Oh brave Kaiju, do you believe in light?\""
    else:
        return "Ultraman unleashes the Zestium Ray, defeating the Kaiju. Looking directly at the camera, he"

def translate_to_english(chinese_prompt: str) -> str:
    """模拟 translate_to_english 方法"""
    print(f"\n🌐 开始翻译中文提示词: {chinese_prompt}")
    
    # 如果已经是英文，直接返回
    if not is_chinese_text(chinese_prompt):
        print("   ℹ️ 检测到英文内容，无需翻译")
        return chinese_prompt
    
    # 检测是否包含对话内容
    has_dialogue, non_dialogue_text, dialogues = extract_dialogue_content(chinese_prompt)
    
    if has_dialogue:
        print(f"   🗣️ 检测到对话内容，将保持对话原样: {len(dialogues)}个对话")
        print(f"   📝 非对话部分: '{non_dialogue_text}'")
        
        # 只翻译非对话部分
        if non_dialogue_text and is_chinese_text(non_dialogue_text):
            print(f"   📤 发送给Gemini API翻译: '{non_dialogue_text}'")
            translated_non_dialogue = mock_translate_text_with_gemini(non_dialogue_text)
            print(f"   📥 Gemini API返回: '{translated_non_dialogue}'")
        else:
            translated_non_dialogue = non_dialogue_text
        
        # 重新组合翻译后的非对话部分和原始对话
        result = translated_non_dialogue
        for dialogue in dialogues:
            if result:
                result += f" {dialogue['english_intro']}: \"{dialogue['content']}\""
            else:
                result = f"{dialogue['english_intro']}: \"{dialogue['content']}\""
        
        print(f"   ✅ 对话处理完成: {result}")
        return result.strip()
    else:
        # 没有对话，正常翻译
        print(f"   📤 没有对话，发送整个文本给Gemini API: '{chinese_prompt}'")
        return mock_translate_text_with_gemini(chinese_prompt)

if __name__ == "__main__":
    test_prompt = '奥特曼发出泽斯蒂姆光线，击败了怪兽。面对镜头，他说道："勇敢的怪兽啊，你相信光吗？"'
    
    print('=== 测试对话保护功能 ===')
    print(f'原始提示词: {test_prompt}')
    
    result = translate_to_english(test_prompt)
    print(f'\n🎯 最终翻译结果: {result}')
    
    # 检查对话是否被保护
    if "勇敢的怪兽啊，你相信光吗？" in result:
        print("✅ 对话内容已保护，未被翻译")
    else:
        print("❌ 对话内容被错误翻译了！")