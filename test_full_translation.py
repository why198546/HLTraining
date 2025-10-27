#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_full_translation():
    """测试完整翻译流程"""
    from api.prompt_translator import translate_prompt
    
    # 测试提示词（和你遇到问题的提示词相似）
    test_prompt = '奥特曼发射捷德力姆光线，击败了怪兽。他转向镜头说道："无礼的怪兽，你拥抱光明吗？"'
    
    print(f"原始提示词: {test_prompt}")
    print("="*60)
    
    try:
        # 调用完整的翻译流程
        result = translate_prompt(test_prompt)
        
        print(f"翻译结果: {result}")
        print("="*60)
        
        # 检查结果是否保留了中文对话
        if "saying in Chinese" in result and "无礼的怪兽，你拥抱光明吗？" in result:
            print("✅ 对话保护功能正常工作")
        else:
            print("❌ 对话保护功能失效")
            print(f"期望包含: 'saying in Chinese' 和 '无礼的怪兽，你拥抱光明吗？'")
            
    except Exception as e:
        print(f"❌ 翻译失败: {e}")

if __name__ == "__main__":
    test_full_translation()