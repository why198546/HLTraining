#!/usr/bin/env python3
import sys
import os

# 添加项目路径
sys.path.append('/Users/hongyuwang/code/HLTraining')

# 模拟翻译器类的对话提取功能
import re

class TestTranslator:
    def extract_dialogue_content(self, text: str):
        """提取对话内容，返回(是否包含对话, 非对话部分, 对话部分列表)"""
        import re
        
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

    def _simple_translation_fallback(self, chinese_prompt: str):
        """简单的备用翻译策略"""
        
        # 检测是否包含对话内容
        has_dialogue, non_dialogue_text, dialogues = self.extract_dialogue_content(chinese_prompt)
        
        if has_dialogue:
            print(f"   🗣️ 备用翻译检测到对话内容: {len(dialogues)}个对话")
            
            # 模拟翻译非对话部分
            translated_non_dialogue = "Ultraman unleashes the Zestium Ray, defeating the Kaiju. Looking directly at the camera"
            
            # 重新组合翻译后的非对话部分和原始对话
            result = translated_non_dialogue
            for dialogue in dialogues:
                if result:
                    result += f", he {dialogue['english_intro']}: \"{dialogue['content']}\""
                else:
                    result = f"{dialogue['english_intro']}: \"{dialogue['content']}\""
            
            return result.strip()
        else:
            # 没有对话，返回简单翻译
            return "Ultraman unleashes the Zestium Ray, defeating the Kaiju. Looking directly at the camera"

if __name__ == "__main__":
    translator = TestTranslator()
    test_prompt = '奥特曼发出泽斯蒂姆光线，击败了怪兽。面对镜头，他说道："勇敢的怪兽啊，你相信光吗？"'
    
    print('原始提示词:', test_prompt)
    
    has_dialogue, non_dialogue, dialogues = translator.extract_dialogue_content(test_prompt)
    print(f'是否包含对话: {has_dialogue}')
    print(f'非对话部分: "{non_dialogue}"')
    print(f'对话部分: {dialogues}')
    
    result = translator._simple_translation_fallback(test_prompt)
    print(f'最终结果: {result}')