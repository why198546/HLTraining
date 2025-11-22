"""
语音转录文本智能标点符号优化
使用通义千问API为语音转录文本添加标点符号，提高可读性
"""

import os
import requests
from openai import OpenAI

def add_punctuation_to_text(text):
    """
    为语音转录文本添加智能标点符号
    
    Args:
        text: 原始语音转录文本（无标点或标点不全）
    
    Returns:
        添加了标点符号的优化文本
    """
    if not text or len(text.strip()) < 2:
        return text
    
    # 如果文本已经有足够的标点符号，直接返回
    punctuation_count = sum(1 for c in text if c in '，。！？、；：""''（）')
    if punctuation_count / len(text) > 0.1:  # 如果标点符号占比超过10%，认为已经有标点
        return text
    
    # 首先尝试使用AI优化
    try:
        # 使用通义千问API
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            print("提示: 未设置DASHSCOPE_API_KEY，使用简单规则优化")
            return add_punctuation_simple(text)
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # 构建提示词
        prompt = f"""请为下面的语音转录文本添加合适的标点符号，使其更易读。注意：
1. 根据语义和语气添加逗号、句号、问号、感叹号等
2. 保持原文内容不变，只添加标点符号
3. 不要添加任何解释或额外的文字
4. 直接返回优化后的文本

原文：
{text}

优化后的文本："""
        
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的文本标点符号优化助手，擅长为语音转录文本添加合适的标点符号。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,  # 较低的温度以保持一致性
            max_tokens=500,
            timeout=5  # 5秒超时
        )
        
        optimized_text = completion.choices[0].message.content.strip()
        
        # 移除可能的引号包裹
        if optimized_text.startswith('"') and optimized_text.endswith('"'):
            optimized_text = optimized_text[1:-1]
        if optimized_text.startswith('"') and optimized_text.endswith('"'):
            optimized_text = optimized_text[1:-1]
        
        print(f"AI标点优化成功: {text[:30]}... -> {optimized_text[:30]}...")
        return optimized_text
        
    except Exception as e:
        print(f"AI标点优化失败，使用简单规则: {str(e)}")
        # 如果API调用失败，降级到简单规则
        return add_punctuation_simple(text)


def add_punctuation_simple(text):
    """
    简单的标点符号添加规则（备用方案）
    基于常见的语气词和停顿词添加标点
    """
    if not text:
        return text
    
    import re
    
    result = text
    
    # 1. 在常见连接词/转折词后添加逗号
    connectors = ['然后', '接着', '所以', '因此', '但是', '不过', '而且', '或者', '可是', '于是', '还有', '另外', '其实', '后面']
    for word in connectors:
        # 只在词后面还有内容且没有标点的情况下添加逗号
        result = re.sub(f'{word}(?=[^，。！？、；]{2,})', f'{word}，', result)
    
    # 2. 处理疑问句
    # 疑问词开头 + 内容 -> 添加问号
    question_starters = ['什么', '怎么', '为什么', '哪里', '谁', '如何', '怎样', '为啥', '咋']
    for word in question_starters:
        if word in result:
            # 找到疑问词到句尾，添加问号
            result = re.sub(f'({word}[^？。！，]{{3,}})', r'\1？', result)
    
    # 句尾疑问语气词
    result = re.sub(r'([^？。！，]{2,})(吗|呢)([^？]|$)', r'\1\2？', result)
    
    # 3. 处理感叹句
    exclamation_words = ['哇塞', '太好了', '真棒', '厉害', '太酷了', '牛']
    for word in exclamation_words:
        if word in result:
            result = re.sub(f'({word}[^！。？，]*?)([^！。？，]{{2,}}|$)', r'\1！', result)
    
    # 4. 在"了"后面加逗号或句号（根据后续内容判断）
    result = re.sub(r'了([^。！？，]{3,})', r'了，\1', result)
    
    # 5. 处理"吧"结尾
    result = re.sub(r'([^。！？]{2,})吧([^。！？]|$)', r'\1吧。', result)
    
    # 6. 清理多余的标点
    result = re.sub(r'[。！？]{2,}', '。', result)
    result = re.sub(r'，{2,}', '，', result)
    result = re.sub(r'[。！？]，', '。', result)  # 句号后的逗号删除
    
    # 7. 如果结尾没有标点，添加句号
    if result and result[-1] not in '。！？，、；：':
        result += '。'
    
    return result
