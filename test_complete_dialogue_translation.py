#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的对话保护翻译功能（包含Gemini API）
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_complete_dialogue_translation():
    """测试完整的对话保护翻译功能"""
    
    try:
        from api.prompt_translator import translate_prompt
        
        test_cases = [
            {
                "prompt": '小人在花园里跳舞，他说道："今天天气真好！"',
                "description": "包含对话的中文prompt"
            },
            {
                "prompt": '角色击败敌人后，喊道："我赢了！"然后开心地跳舞',
                "description": "包含对话和敏感词的prompt"
            },
            {
                "prompt": "小人在花园里跳舞",
                "description": "不包含对话的普通prompt"
            },
            {
                "prompt": 'A character dancing in the garden',
                "description": "英文prompt（不需要翻译）"
            }
        ]
        
        print("完整对话保护翻译功能测试")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            original = test_case["prompt"]
            
            print(f"\n测试用例 {i}: {test_case['description']}")
            print(f"原文: {original}")
            
            # 使用完整的翻译功能
            translated = translate_prompt(original)
            
            print(f"翻译结果: {translated}")
            
            # 检查对话是否被保护
            if '："' in original or ':"' in original:
                # 提取原文中的对话内容
                import re
                dialogue_matches = re.findall(r'["""\'\'](.*?)["""\'\'"]', original)
                
                if dialogue_matches:
                    all_preserved = True
                    for dialogue in dialogue_matches:
                        if dialogue not in translated:
                            all_preserved = False
                            print(f"❌ 对话内容丢失: \"{dialogue}\"")
                    
                    if all_preserved:
                        print("✅ 所有对话内容都被正确保护")
                    else:
                        print("❌ 部分对话内容丢失")
                else:
                    print("ℹ️ 未检测到对话内容")
            else:
                print("ℹ️ 无对话内容需要保护")
            
            print("-" * 50)
            
    except ImportError as e:
        print(f"❌ 导入翻译模块失败: {str(e)}")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_complete_dialogue_translation()