import re

ART_TERMINOLOGY_MAPPING = {
    r'3头身比例': '3-head proportion (childlike proportions - head is 1/3 of total body height, typical for young children)',
    r'3\.5头身比例': '3.5-head proportion (cute young character - head is 2/7 of total height, typical for pre-teens)',
    r'4头身比例': '4-head proportion (young character - head is 1/4 of total height)',
}

def enhance_art_terminology(prompt):
    if not prompt:
        return prompt
    
    enhanced = prompt
    for pattern, replacement in ART_TERMINOLOGY_MAPPING.items():
        if re.search(pattern, enhanced, re.IGNORECASE):
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
            print(f'✓ 替换: {pattern}')
    
    return enhanced

# 测试
test1 = '一个10岁的男孩，4头身比例，穿蓝色T恤'
test2 = '一个12岁的女孩，3.5头身比例，穿粉色连衣裙'

print('测试1:')
print(f'输入: {test1}')
result1 = enhance_art_terminology(test1)
print(f'输出: {result1}\n')

print('测试2:')
print(f'输入: {test2}')
result2 = enhance_art_terminology(test2)
print(f'输出: {result2}')
