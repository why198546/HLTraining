"""
测试标点符号优化功能
"""

from api.text_punctuation import add_punctuation_to_text, add_punctuation_simple

# 测试用例
test_cases = [
    "哇塞这个也太酷了吧",
    "好嘞让我再来测试一下语音录入功能看看效果如何",
    "这个我觉得还不错后面我也可以尝试一下",
    "你好吗我想问一下这个怎么用啊",
    "今天天气真好我们一起出去玩吧"
]

print("=" * 60)
print("标点符号优化测试")
print("=" * 60)

for i, text in enumerate(test_cases, 1):
    print(f"\n测试 {i}:")
    print(f"原文: {text}")
    
    # 测试简单规则
    simple_result = add_punctuation_simple(text)
    print(f"简单规则: {simple_result}")
    
    # 测试AI优化（如果配置了API key）
    try:
        ai_result = add_punctuation_to_text(text)
        print(f"AI优化: {ai_result}")
    except Exception as e:
        print(f"AI优化失败: {str(e)}")

print("\n" + "=" * 60)
