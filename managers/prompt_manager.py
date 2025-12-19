"""提示词相关业务逻辑管理器"""
import re


class PromptManager:
    """提示词管理器"""
    
    @staticmethod
    def detect_and_split_multi_generation(prompt, forced_intent=None):
        """检测并拆分多图生成命令
        
        支持的格式：
        1. "3张 小猫照片" - 数量+描述
        2. "小猫, 小狗, 小鸟" - 逗号分隔
        3. "小猫 and 小狗 and 小鸟" - and连接
        
        Args:
            prompt: 用户输入的提示词
            forced_intent: 强制意图（'multi'表示多图模式）
            
        Returns:
            dict: 包含意图和任务列表的字典
                {
                    'intent': 'multi_generate' | 'generate' | 'chat',
                    'tasks': [{'description': str, 'prompt': str}, ...],
                    'response': str
                }
        """
        # 如果强制指定为多图模式，使用本地解析
        if forced_intent == 'multi':
            result = PromptManager._parse_multi_generation_local(prompt)
            if result['count'] > 0:
                tasks = [{'description': result['description'], 'prompt': result['description']} 
                        for _ in range(result['count'])]
                return {
                    'intent': 'multi_generate',
                    'tasks': tasks,
                    'response': f"收到！我将为你生成 {result['count']} 张图片：{result['description']}"
                }
        
        # 其他检测逻辑...（可以保留原有的AI检测逻辑，这里简化）
        return {
            'intent': 'generate',
            'tasks': [],
            'response': ''
        }
    
    @staticmethod
    def _parse_multi_generation_local(prompt):
        """本地解析多图生成提示词
        
        Args:
            prompt: 用户输入
            
        Returns:
            dict: {'count': int, 'description': str}
        """
        # 中文数字映射
        chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '两': 2, '俩': 2
        }
        
        # 模式1: "数字+量词+描述" (如: "3张小猫", "五个苹果")
        pattern1 = r'^([一二三四五六七八九十两俩\d]+)[张个幅份](.+)$'
        
        # 模式2: "数字+描述" (如: "3小猫", "五苹果")
        pattern2 = r'^([一二三四五六七八九十两俩\d]+)(.+)$'
        
        # 模式3: "描述+数字+量词" (如: "小猫3张", "苹果五个")
        pattern3 = r'^(.+?)([一二三四五六七八九十两俩\d]+)[张个幅份]$'
        
        patterns = [
            {'regex': pattern1, 'countIndex': 1, 'descIndex': 2},
            {'regex': pattern2, 'countIndex': 1, 'descIndex': 2},
            {'regex': pattern3, 'countIndex': 2, 'descIndex': 1}
        ]
        
        for pattern in patterns:
            match = re.match(pattern['regex'], prompt.strip())
            if match:
                count_str = match[pattern['countIndex']]
                description = match[pattern['descIndex']].strip()
                
                # 转换数量
                count = chinese_nums.get(count_str, None)
                if count is None:
                    try:
                        count = int(count_str)
                    except:
                        continue
                
                if count and description:
                    return {'count': count, 'description': description}
        
        # 如果没有匹配到明确的格式，返回0
        return {'count': 0, 'description': prompt}
    
    @staticmethod
    def add_default_nationality(prompt):
        """为人物提示词添加默认国籍
        
        如果提示词中包含人物但未指定国籍，默认添加"中国人形象"
        
        Args:
            prompt: 原始提示词
            
        Returns:
            str: 处理后的提示词
        """
        if not prompt:
            return prompt
        
        # 检测是否已包含国籍
        has_nationality = bool(re.search(
            r'外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|'
            r'意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾',
            prompt, re.IGNORECASE
        ))
        
        # 检测是否包含人物
        has_person = bool(re.search(
            r'人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师',
            prompt
        ))
        
        # 如果有人物但没有国籍，且不包含"中国"，则添加
        if not has_nationality and has_person and '中国' not in prompt:
            prompt = '中国人形象，' + prompt
            print(f"✅ 自动添加中国人形象，新提示词: {prompt}")
        
        return prompt
