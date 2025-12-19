"""
测试智能助手多图生成功能
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# 导入需要的依赖
import re


def detect_and_split_multi_generation(prompt, forced_intent=None):
    """智能检测并拆解多张图片生成请求"""
    
    # 如果强制意图不是生成，则不处理
    if forced_intent and forced_intent != 'generate':
        return {'is_multi': False}
    
    prompt_lower = prompt.lower()
    tasks = []
    
    # 模式1: "画3张xxx" 或 "生成5个yyy"
    patterns = [
        r'(?:画|生成|创作|做)\s*([\d一二三四五六七八九十]+)\s*(?:张|个|幅)\s*(.+)',
        r'(.+?)\s*，?\s*(?:画|生成|创作)\s*([\d一二三四五六七八九十]+)\s*(?:张|个|幅)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            # 提取数量和描述
            groups = match.groups()
            if len(groups) == 2:
                # 判断哪个是数量，哪个是描述
                if groups[0] and any(char.isdigit() or char in '一二三四五六七八九十' for char in groups[0]):
                    count_str, description = groups[0], groups[1]
                else:
                    description, count_str = groups[0], groups[1]
                
                # 转换中文数字
                chinese_nums = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                count = chinese_nums.get(count_str, None)
                if count is None:
                    try:
                        count = int(count_str)
                    except:
                        continue
                
                # 限制最多生成10张
                count = min(count, 10)
                description = description.strip('，。 ')
                
                if count > 1 and description:
                    tasks = [{'prompt': description, 'index': i+1} for i in range(count)]
                    return {
                        'is_multi': True,
                        'tasks': tasks,
                        'message': f'好的！我将为你生成{count}张"{description}"的图片，请稍等...'
                    }
    
    # 模式2: "画一个xxx，一个yyy，一个zzz" 或 "xxx、yyy、zzz"
    # 中文逗号、顿号、分号分隔
    if any(sep in prompt for sep in ['，', '、', '；', ';']):
        # 移除生成关键词
        cleaned = prompt
        for kw in ['画', '生成', '创作', '做一个', '做一张', '帮我', '给我', '我想要']:
            cleaned = cleaned.replace(kw, '')
        
        # 分割
        items = re.split(r'[，、；;]', cleaned)
        items = [item.strip() for item in items if item.strip() and len(item.strip()) > 1]
        
        # 如果有2个以上的项目，且每个都不太长（不是长句）
        if len(items) >= 2 and all(len(item) < 30 for item in items):
            tasks = [{'prompt': item, 'index': i+1} for i, item in enumerate(items)]
            return {
                'is_multi': True,
                'tasks': tasks,
                'message': f'好的！我将为你生成{len(items)}张不同的图片，请稍等...'
            }
    
    # 模式3: "画xxx和yyy" (只有2-3个且用"和"连接)
    if '和' in prompt:
        cleaned = prompt
        for kw in ['画', '生成', '创作', '做', '帮我', '给我', '我想要']:
            cleaned = cleaned.replace(kw, '', 1)  # 只替换第一次出现
        
        # 移除"一只"、"一个"等量词
        cleaned = re.sub(r'一只|一个|一张|一幅', '', cleaned)
        
        items = [item.strip() for item in cleaned.split('和') if item.strip()]
        
        # 如果有2-3个项目，且每个都有合理长度
        if 2 <= len(items) <= 3 and all(len(item) < 30 for item in items):  # 允许单字
            tasks = [{'prompt': item, 'index': i+1} for i, item in enumerate(items)]
            return {
                'is_multi': True,
                'tasks': tasks,
                'message': f'好的！我将为你生成{len(items)}张不同的图片，请稍等...'
            }
    
    return {'is_multi': False}

def test_multi_generation():
    """测试各种多图生成格式"""
    
    test_cases = [
        # 格式1: 数量 + 描述
        ("画3张可爱的小猫", True, 3),
        ("生成五个风景画", True, 5),
        ("创作二张中国风建筑", True, 2),
        
        # 格式2: 逗号分隔
        ("画一只猫，一只狗，一只兔子", True, 3),
        ("画樱花、枫叶、荷花", True, 3),
        ("生成山水画；卡通画；水彩画", True, 3),
        
        # 格式3: "和"连接
        ("画一只猫和一只狗", True, 2),
        ("生成春天的樱花和秋天的枫叶", True, 2),
        
        # 非多图格式
        ("画一只可爱的小猫", False, 0),
        ("生成一张风景画", False, 0),
    ]
    
    print("🧪 开始测试多图生成检测功能\n")
    
    success = 0
    failed = 0
    
    for prompt, expected_multi, expected_count in test_cases:
        result = detect_and_split_multi_generation(prompt)
        is_multi = result['is_multi']
        task_count = len(result.get('tasks', []))
        
        if is_multi == expected_multi and (not is_multi or task_count == expected_count):
            print(f"✅ 通过: {prompt}")
            if is_multi:
                print(f"   📊 检测到 {task_count} 个任务")
                for i, task in enumerate(result['tasks'], 1):
                    print(f"   {i}. {task['prompt']}")
            success += 1
        else:
            print(f"❌ 失败: {prompt}")
            print(f"   预期: multi={expected_multi}, count={expected_count}")
            print(f"   实际: multi={is_multi}, count={task_count}")
            failed += 1
        print()
    
    print(f"\n📈 测试结果: {success} 通过, {failed} 失败")
    return failed == 0

if __name__ == '__main__':
    success = test_multi_generation()
    exit(0 if success else 1)
