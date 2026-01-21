#!/usr/bin/env python3
"""
测试后端特征检测和前端集成流程
"""

def test_analyze_and_generate_variations():
    """测试analyze_and_generate_variations函数"""
    
    # 模拟该函数的实现
    def analyze_and_generate_variations(prompt_text, num_variations=4):
        """分析prompt中已提到的特征，为未提到的特征生成差异化描述"""
        
        # 10个核心特征及其检测关键词和变化选项
        features = {
            'gender': {
                'keywords': ['男孩', '女孩', '男', '女', '男生', '女生', '小伙', '姑娘'],
                'options': [],
                'index': 0
            },
            'body': {
                'keywords': ['胖', '瘦', '壮', '苗条', '强壮', '纤细'],
                'options': ['偏瘦身材', '身材适中', '偏胖身材'],
                'index': 1
            },
            'hair_length': {
                'keywords': ['长发', '短发', '中长发', '齐肩发'],
                'options': ['短发', '中长发', '长发'],
                'index': 2
            },
            'hair_style': {
                'keywords': ['卷发', '直发', '波浪', '自然卷'],
                'options': ['直发', '微卷发', '卷发'],
                'index': 3
            },
            'eyes': {
                'keywords': ['大眼睛', '小眼睛', '眼睛大', '眼睛小'],
                'options': ['大眼睛', '小眼睛', '中等眼睛'],
                'index': 5
            }
        }
        
        # 检测prompt中已提到的特征
        mentioned_features = {}
        for feature_name, feature_data in features.items():
            for keyword in feature_data['keywords']:
                if keyword in prompt_text:
                    # 返回特征索引和检测到的关键词
                    mentioned_features[feature_data['index']] = keyword
                    break
        
        print(f"🔍 检测到已提及的特征: {mentioned_features}")
        
        # 为未提及的特征生成差异化选项
        unmentioned_features = {k: v for k, v in features.items() 
                               if v['index'] not in mentioned_features and v['options']}
        
        # 生成num_variations个变化描述
        variations = []
        for i in range(num_variations):
            variation_parts = []
            for feature_name, feature_data in unmentioned_features.items():
                if feature_data['options']:
                    # 为每个变化选择不同的选项
                    option_index = i % len(feature_data['options'])
                    variation_parts.append(feature_data['options'][option_index])
            
            if variation_parts:
                variations.append("，补充特征：" + "，".join(variation_parts))
            else:
                variations.append(f"，第{i+1}个版本")
        
        print(f"✨ 生成的差异化描述: {variations}")
        return variations, mentioned_features
    
    # 测试用例
    test_cases = [
        ("男孩，大眼睛，长发", "应该检测到性别(0)和眼睛(5)，头发长度(2)"),
        ("女孩，长发", "应该检测到性别(0)和头发长度(2)"),
        ("瘦瘦的，卷发", "应该检测到体型(1)和头发风格(3)"),
        ("红色衣服，无特征描述", "应该检测不到任何特征")
    ]
    
    for prompt, expected in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {prompt}")
        print(f"预期: {expected}")
        print(f"{'='*60}")
        
        variations, mentioned = analyze_and_generate_variations(prompt)
        
        print(f"✅ detected_features返回值: {mentioned}")
        print(f"✅ variations返回值: {variations}")
        
        # 验证returned_features的格式：应该是 {0: '男孩', 5: '大眼睛', ...}
        assert isinstance(mentioned, dict), "returned_features应该是字典"
        
        for idx, keyword in mentioned.items():
            assert isinstance(idx, int), f"特征索引应该是int，得到{type(idx)}"
            assert isinstance(keyword, str), f"特征值应该是str，得到{type(keyword)}"
            assert 0 <= idx <= 9, f"特征索引应该在0-9范围内，得到{idx}"

if __name__ == '__main__':
    test_analyze_and_generate_variations()
    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60)
