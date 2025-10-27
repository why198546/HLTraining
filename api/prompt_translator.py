"""
AI提示词翻译服务
使用Gemini API将中文提示词转换为英文，避免内容安全过滤问题
"""

import os
import google.genai as genai
from typing import Optional
import re

class PromptTranslator:
    """提示词翻译器"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('NANO_BANANA_API_KEY')
        print(f"🔑 API密钥检查: GEMINI_API_KEY={'存在' if os.getenv('GEMINI_API_KEY') else '不存在'}")
        print(f"🔑 API密钥检查: NANO_BANANA_API_KEY={'存在' if os.getenv('NANO_BANANA_API_KEY') else '不存在'}")
        print(f"🔑 最终使用的API密钥: {'已设置' if self.api_key else '未设置'}")
        
        if not self.api_key:
            raise ValueError("未找到GEMINI_API_KEY或NANO_BANANA_API_KEY环境变量")
        
        # 初始化Gemini客户端
        self.client = genai.Client(api_key=self.api_key)
        
        print("✅ AI提示词翻译服务初始化成功")
    
    def is_chinese_text(self, text: str) -> bool:
        """检测文本是否包含中文字符"""
        import re
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def extract_dialogue_content(self, text: str) -> tuple:
        """提取对话内容，返回(是否包含对话, 非对话部分, 对话部分列表)"""
        import re
        
        print(f"🔍 [DEBUG] 开始提取对话内容: '{text}'")
        
        # 匹配"说道/写道/喊道/问道/答道等："或"："后面的引号内容
        # 支持中文引号""和英文引号""
        dialogue_pattern = r'([说写喊问答叫唱念读]道[:：])\s*["\'""\'\'](.*?)["\'""\'\'"]'
        
        print(f"🔍 [DEBUG] 使用正则表达式: {dialogue_pattern}")
        print(f"🔍 [DEBUG] 输入文本字符详情: {[ord(c) for c in text]}")
        
        # 额外调试：测试简化的正则
        simple_pattern = r'说道[:：]\s*"(.*?)"'
        simple_matches = re.findall(simple_pattern, text)
        print(f"🔍 [DEBUG] 简化正则匹配: {simple_matches}")
        
        dialogues = []
        dialogue_matches = list(re.finditer(dialogue_pattern, text))
        
        print(f"🔍 [DEBUG] 正则匹配结果数量: {len(dialogue_matches)}")
        
        for i, match in enumerate(dialogue_matches):
            print(f"🔍 [DEBUG] 匹配 {i+1}: '{match.group(0)}'")
            print(f"    引导词: '{match.group(1)}'")
            print(f"    对话内容: '{match.group(2)}'")
        
        if not dialogue_matches:
            print(f"🔍 [DEBUG] 未找到对话内容，返回原文本")
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
            
            dialogue_info = {
                'full_match': match.group(0),
                'intro': chinese_intro,
                'english_intro': english_intro,
                'content': match.group(2),
                'start': match.start(),
                'end': match.end()
            }
            dialogues.append(dialogue_info)
            
            print(f"🔍 [DEBUG] 对话信息: {dialogue_info}")
        
        # 移除对话内容，只保留非对话部分用于翻译
        non_dialogue_text = text
        # 先按位置排序，从后往前删除，避免位置偏移
        sorted_dialogues = sorted(dialogues, key=lambda x: x['start'], reverse=True)
        
        print(f"🔍 [DEBUG] 原始文本: '{text}'")
        
        for dialogue in sorted_dialogues:
            print(f"🔍 [DEBUG] 移除对话: 位置 {dialogue['start']}-{dialogue['end']}, 内容: '{dialogue['full_match']}'")
            non_dialogue_text = non_dialogue_text[:dialogue['start']] + non_dialogue_text[dialogue['end']:]
            print(f"🔍 [DEBUG] 移除后文本: '{non_dialogue_text}'")
        
        # 清理非对话文本中的多余空格和标点
        non_dialogue_text = re.sub(r'\s*[，,]\s*', ' ', non_dialogue_text)  # 移除孤立的逗号
        non_dialogue_text = re.sub(r'\s+', ' ', non_dialogue_text)  # 合并多个空格
        
        print(f"🔍 [DEBUG] 清理后的非对话文本: '{non_dialogue_text.strip()}'")
        print(f"🔍 [DEBUG] 提取的对话列表: {dialogues}")
        
        return True, non_dialogue_text.strip(), dialogues
    
    def translate_to_english(self, chinese_prompt: str) -> str:
        """
        将中文提示词翻译为适合视频生成的英文描述
        
        Args:
            chinese_prompt: 中文提示词
            
        Returns:
            英文提示词
        """
        try:
            print(f"\n🌐 [DEBUG] 开始翻译中文提示词: '{chinese_prompt}'")
            
            # 如果已经是英文，直接返回
            if not self.is_chinese_text(chinese_prompt):
                print("   ℹ️ [DEBUG] 检测到英文内容，无需翻译")
                return chinese_prompt
            
            print(f"   ✅ [DEBUG] 确认包含中文，需要翻译")
            
            # 检测是否包含对话内容
            print(f"   🔍 [DEBUG] 调用对话内容提取函数...")
            has_dialogue, non_dialogue_text, dialogues = self.extract_dialogue_content(chinese_prompt)
            
            print(f"   📊 [DEBUG] 对话检测结果:")
            print(f"       是否包含对话: {has_dialogue}")
            print(f"       非对话文本: '{non_dialogue_text}'")
            print(f"       对话数量: {len(dialogues)}")
            
            if has_dialogue:
                print(f"   🗣️ [DEBUG] 检测到对话内容，将保持对话原样: {len(dialogues)}个对话")
                
                # 只翻译非对话部分
                if non_dialogue_text and self.is_chinese_text(non_dialogue_text):
                    print(f"   📝 [DEBUG] 准备翻译非对话部分: '{non_dialogue_text}'")
                    translated_non_dialogue = self._translate_text_with_gemini(non_dialogue_text)
                    print(f"   ✅ [DEBUG] 非对话部分翻译完成: '{translated_non_dialogue}'")
                else:
                    translated_non_dialogue = non_dialogue_text
                    print(f"   ℹ️ [DEBUG] 非对话部分无需翻译: '{translated_non_dialogue}'")
                
                # 重新组合翻译后的非对话部分和原始对话
                result = translated_non_dialogue
                print(f"   🔧 [DEBUG] 开始重新组合文本，基础部分: '{result}'")
                
                for i, dialogue in enumerate(dialogues):
                    dialogue_part = f" {dialogue['english_intro']}: \"{dialogue['content']}\""
                    print(f"   🔧 [DEBUG] 添加对话 {i+1}: '{dialogue_part}'")
                    
                    if result:
                        result += dialogue_part
                    else:
                        result = f"{dialogue['english_intro']}: \"{dialogue['content']}\""
                    
                    print(f"   🔧 [DEBUG] 当前结果: '{result}'")
                
                print(f"   ✅ [DEBUG] 对话处理完成，最终结果: '{result.strip()}'")
                return result.strip()
            else:
                print(f"   ℹ️ [DEBUG] 没有对话内容，直接翻译整个文本")
                # 没有对话，正常翻译
                return self._translate_text_with_gemini(chinese_prompt)
                
        except Exception as e:
            print(f"   ❌ [DEBUG] 翻译异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._simple_translation_fallback(chinese_prompt)
    
    def _translate_text_with_gemini(self, text: str) -> str:
        """使用Gemini API翻译文本"""
        print(f"   🤖 [DEBUG] 准备调用Gemini API")
        print(f"       输入文本: '{text}'")
        
        # 构建翻译提示词
        translation_prompt = f"""
请将以下中文文本翻译成英文，要求：
1. 只翻译给定的文本内容，不要添加任何额外内容
2. 不要补充或推测任何未提供的信息
3. 使用适合AI视频生成的专业术语
4. 保持动作描述的准确性和流畅性
5. 避免可能触发内容安全过滤器的词汇
6. 使用积极正面的表达方式
7. 只返回翻译结果，不要解释

需要翻译的中文文本：{text}

英文翻译："""

        print(f"   🤖 [DEBUG] 发送给Gemini的完整提示词:")
        print(f"       {translation_prompt}")

        # 调用Gemini API进行翻译
        try:
            print(f"   🌐 [DEBUG] 正在调用Gemini API...")
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',  # 使用正确的模型名称
                contents=translation_prompt
            )
            
            print(f"   📥 [DEBUG] Gemini API响应:")
            print(f"       response对象: {response}")
            print(f"       response.text: {response.text if response else 'None'}")
            
            if response and response.text:
                english_prompt = response.text.strip()
                
                print(f"   🧹 [DEBUG] 原始响应文本: '{english_prompt}'")
                
                # 清理翻译结果
                english_prompt = self._clean_translation(english_prompt)
                
                print(f"   ✅ [DEBUG] 清理后翻译结果: '{english_prompt}'")
                return english_prompt
            else:
                print("   ❌ [DEBUG] 翻译失败：无响应内容")
                return text
        except Exception as e:
            print(f"   ❌ [DEBUG] Gemini API调用异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return text
    
    def _clean_translation(self, text: str) -> str:
        """清理翻译结果"""
        # 移除可能的引号
        text = text.strip('"\'')
        
        # 移除换行符
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        # 移除常见的前缀
        prefixes_to_remove = [
            "英文翻译：",
            "Translation:",
            "English:",
            "英文："
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def translate_with_fallback(self, prompt: str, max_retries: int = 2) -> str:
        """
        带重试机制的翻译
        
        Args:
            prompt: 原始提示词
            max_retries: 最大重试次数
            
        Returns:
            翻译后的英文提示词
        """
        if not self.is_chinese_text(prompt):
            return prompt
        
        for attempt in range(max_retries + 1):
            try:
                result = self.translate_to_english(prompt)
                if result and result != prompt:  # 翻译成功且有变化
                    return result
            except Exception as e:
                print(f"   翻译尝试 {attempt + 1} 失败: {e}")
                if attempt == max_retries:
                    break
        
        # 如果翻译失败，返回简化的英文描述
        print("   🔄 使用备用翻译策略")
        return self._simple_translation_fallback(prompt)
    
    def _simple_translation_fallback(self, chinese_prompt: str) -> str:
        """简单的备用翻译策略"""
        
        # 检测是否包含对话内容
        has_dialogue, non_dialogue_text, dialogues = self.extract_dialogue_content(chinese_prompt)
        
        if has_dialogue:
            print(f"   🗣️ 备用翻译检测到对话内容: {len(dialogues)}个对话")
            
            # 只翻译非对话部分
            if non_dialogue_text and self.is_chinese_text(non_dialogue_text):
                translated_non_dialogue = self._translate_non_dialogue_fallback(non_dialogue_text)
            else:
                translated_non_dialogue = non_dialogue_text
            
            # 重新组合翻译后的非对话部分和原始对话
            result = translated_non_dialogue
            for dialogue in dialogues:
                if result:
                    result += f" {dialogue['english_intro']}: \"{dialogue['content']}\""
                else:
                    result = f"{dialogue['english_intro']}: \"{dialogue['content']}\""
            
            return result.strip()
        else:
            # 没有对话，使用原来的备用翻译逻辑
            return self._translate_non_dialogue_fallback(chinese_prompt)
    
    def _translate_non_dialogue_fallback(self, chinese_prompt: str) -> str:
        """翻译非对话内容的备用方法"""
        # 基本的中英文映射
        basic_translations = {
            # 人物
            '小女孩': 'little girl',
            '小男孩': 'little boy', 
            '孩子': 'child',
            '妈妈': 'mother',
            '爸爸': 'father',
            '老师': 'teacher',
            '学生': 'student',
            '医生': 'doctor',
            '警察': 'police officer',
            '朋友': 'friend',
            '家人': 'family',
            '爷爷': 'grandfather',
            '奶奶': 'grandmother',
            '哥哥': 'brother',
            '姐姐': 'sister',
            '叔叔': 'uncle',
            '阿姨': 'aunt',
            '角色': 'character',
            '人物': 'person',
            # 特殊角色
            '奥特曼': 'Ultraman',
            '超人': 'superhero',
            '英雄': 'hero',
            '战士': 'warrior',
            # 动物
            '小猫': 'kitten',
            '小狗': 'puppy',
            '猫咪': 'cat',
            '狗狗': 'dog',
            '小鸟': 'bird',
            '蝴蝶': 'butterfly',
            '兔子': 'rabbit',
            '熊猫': 'panda',
            '大象': 'elephant',
            '狮子': 'lion',
            '老虎': 'tiger',
            '猴子': 'monkey',
            '松鼠': 'squirrel',
            '小鱼': 'fish',
            '海豚': 'dolphin',
            '怪兽': 'monster',
            '小怪兽': 'little monster',
            '动物': 'animal',
            '猫': 'cat',
            '狗': 'dog',
            '鸟': 'bird',
            '鸟儿': 'bird',
            # 动作
            '跑步': 'running',
            '走路': 'walking',
            '跳跃': 'jumping',
            '飞翔': 'flying',
            '游泳': 'swimming',
            '唱歌': 'singing',
            '跳舞': 'dancing',
            '学习': 'studying',
            '读书': 'reading',
            '写字': 'writing',
            '画画': 'drawing',
            '玩耍': 'playing',
            '休息': 'resting',
            '睡觉': 'sleeping',
            '探险': 'exploring',
            '发射': 'shooting',
            '打败': 'defeating',
            '击败': 'defeating',
            '对着': 'facing',
            '微笑': 'smiling',
            '挥手': 'waving',
            '坐下': 'sitting',
            '站立': 'standing',
            # 物品和技能
            '光线': 'beam',
            '淬斯蒂姆光线': 'Zestium beam',
            '激光': 'laser',
            '能量': 'energy',
            '屏幕': 'screen',
            '休息': 'resting',
            '睡觉': 'sleeping',
            '探险': 'exploring',
            # 场景词汇
            '花园': 'garden',
            '公园': 'park',
            '房子': 'house',
            '树': 'tree',
            '花': 'flower',
            '草地': 'grass',
            '天空': 'sky',
            '云': 'cloud',
            '太阳': 'sun',
            '月亮': 'moon',
            '星星': 'star',
            '森林': 'forest',
            # 形容词
            '温柔': 'gentle',
            '美丽': 'beautiful',
            '可爱': 'cute',
            '神秘': 'mysterious',
            # 副词
            '慢慢': 'slowly',
            '快速': 'quickly',
            '轻柔': 'softly',
            '优雅': 'gracefully',
            '然后': 'then',
            '接着': 'then',
            '突然': 'suddenly',
            '轻轻': 'gently',
            # 介词和助词（需要移除的）
            '在': ' in ',
            '里': '',
            '的': '',
            '了': '',
            '着': '',
            '地': '',
            '儿': '',  # 鸟儿 -> 鸟
            '咪': '',  # 猫咪 -> 猫
            '。': '',  # 移除中文句号
            '，': ',',  # 中文逗号转英文逗号
        }
        
        # 按长度排序，先替换长词汇，避免部分匹配问题
        sorted_translations = sorted(basic_translations.items(), key=lambda x: len(x[0]), reverse=True)
        
        result = chinese_prompt
        for chinese, english in sorted_translations:
            if chinese in result:
                if english:  # 如果有英文对应词
                    result = result.replace(chinese, f' {english} ')
                else:  # 如果是需要移除的助词
                    result = result.replace(chinese, ' ')
        
        # 清理多余空格
        result = ' '.join(result.split())
        
        # 检查翻译效果 - 如果大部分都翻译成功了，就进行后处理
        chinese_chars = len([c for c in result if '\u4e00' <= c <= '\u9fff'])
        total_meaningful_chars = len([c for c in result if c.isalnum() or '\u4e00' <= c <= '\u9fff'])
        
        if total_meaningful_chars > 0:
            chinese_ratio = chinese_chars / total_meaningful_chars
            # 如果中文字符比例小于20%，说明翻译比较成功
            if chinese_ratio < 0.2:
                # 移除残留的中文字符
                result = ''.join(c if not ('\u4e00' <= c <= '\u9fff') else ' ' for c in result)
                result = ' '.join(result.split())
                
                # 优化语法：处理 "in playing" -> "playing" 等情况
                result = self._fix_grammar(result)
                
                # 添加冠词使其更自然
                result = self._add_articles(result)
                return result
        
        # 如果还包含太多中文，使用基于内容类型的描述作为最后的备用方案
        if self.is_chinese_text(result):
            # 检测内容类型，提供更精确的描述
            if '猫' in chinese_prompt or '猫咪' in chinese_prompt:
                if '玩' in chinese_prompt:
                    return "a cute cat playing"
                else:
                    return "a cute cat"
            elif '鸟' in chinese_prompt:
                if '飞' in chinese_prompt:
                    return "beautiful bird flying in sky"
                else:
                    return "beautiful bird"
            elif '狗' in chinese_prompt:
                return "a cute dog playing"
            elif any(word in chinese_prompt for word in ['小人', '角色', '人物']):
                if '跳舞' in chinese_prompt:
                    return "character dancing in garden"
                elif '玩' in chinese_prompt:
                    return "character playing"
                else:
                    return "character in beautiful scene"
            else:
                return "character in a beautiful and peaceful scene"
        
        return result
    
    def _fix_grammar(self, text: str) -> str:
        """修复常见的语法问题"""
        # 处理 "in playing" -> "playing" 的情况
        text = text.replace(' in playing', ' playing')
        text = text.replace(' in running', ' running')
        text = text.replace(' in jumping', ' jumping')
        text = text.replace(' in dancing', ' dancing')
        text = text.replace(' in flying', ' flying')
        text = text.replace(' in swimming', ' swimming')
        text = text.replace(' in walking', ' walking')
        text = text.replace(' in sitting', ' sitting')
        text = text.replace(' in standing', ' standing')
        text = text.replace(' in sleeping', ' sleeping')
        
        # 处理其他常见问题
        text = text.replace(' in garden dancing', ' dancing in garden')
        text = text.replace(' in park running', ' running in park')
        text = text.replace(' in sky flying', ' flying in sky')
        
        return text
    
    def _add_articles(self, text: str) -> str:
        """为翻译结果添加适当的冠词"""
        words = text.split()
        if not words:
            return text
        
        result = []
        i = 0
        while i < len(words):
            word = words[i]
            
            # 检查是否需要添加冠词
            needs_article = False
            
            # 如果是形容词后面跟名词，或者句子开头是名词
            if word in ['cat', 'dog', 'bird', 'character', 'person']:
                # 检查前面是否已经有冠词或形容词
                if i == 0:  # 句子开头
                    needs_article = True
                elif i > 0:
                    prev_word = words[i-1]
                    # 如果前面不是冠词、形容词或介词，就需要添加冠词
                    if prev_word not in ['a', 'an', 'the', 'cute', 'beautiful', 'small', 'big', 'in', 'on', 'at']:
                        needs_article = True
                    # 如果前面是形容词，检查形容词前面是否有冠词
                    elif prev_word in ['cute', 'beautiful', 'small', 'big'] and (i == 1 or words[i-2] not in ['a', 'an', 'the']):
                        # 在形容词前面插入冠词
                        result.insert(-1, 'a')
                        needs_article = False
            
            if needs_article:
                result.append('a')
            
            result.append(word)
            i += 1
        
        # 后处理：调整词序，确保语法正确
        final_result = []
        i = 0
        while i < len(result):
            word = result[i]
            
            # 处理 "cute a cat" -> "a cute cat" 的情况
            if (i < len(result) - 2 and 
                word in ['cute', 'beautiful', 'small', 'big'] and 
                result[i + 1] == 'a' and 
                result[i + 2] in ['cat', 'dog', 'bird', 'character', 'person']):
                final_result.extend(['a', word, result[i + 2]])
                i += 3
            else:
                final_result.append(word)
                i += 1
        
        return ' '.join(final_result)

# 全局翻译器实例
_translator = None

def get_translator():
    """获取翻译器实例"""
    global _translator
    if _translator is None:
        try:
            _translator = PromptTranslator()
        except Exception as e:
            print(f"❌ 翻译器初始化失败: {e}")
            _translator = None
    return _translator

def translate_prompt(prompt: str) -> str:
    """翻译提示词的便捷函数"""
    translator = get_translator()
    if translator:
        return translator.translate_with_fallback(prompt)
    else:
        # 翻译器不可用时的备用策略
        print("⚠️ 翻译器不可用，使用备用翻译策略")
        
        # 创建一个没有API的翻译器实例，只用于备用翻译
        fallback_translator = PromptTranslator.__new__(PromptTranslator)
        
        # 检查是否是中文
        if fallback_translator.is_chinese_text(prompt):
            return fallback_translator._simple_translation_fallback(prompt)
        else:
            return prompt