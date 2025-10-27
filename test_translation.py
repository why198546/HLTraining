#!/usr/bin/env python3
"""
测试AI提示词翻译功能
验证中文到英文的翻译效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def test_translation_service():
    """测试翻译服务"""
    print("🌐 测试AI提示词翻译服务\n")
    
    # 测试用例
    test_cases = [
        {
            "chinese": "小人在花园里快乐地跳舞",
            "expected_type": "positive_activity"
        },
        {
            "chinese": "可爱的猫咪在草地上玩耍",
            "expected_type": "animal_activity"
        },
        {
            "chinese": "角色拿着武器攻击敌人",
            "expected_type": "action_scene"
        },
        {
            "chinese": "人物在战斗中击败对手",
            "expected_type": "combat_scene"
        },
        {
            "chinese": "温柔的女孩在阳光下微笑",
            "expected_type": "peaceful_scene"
        },
        {
            "chinese": "A character walking in the park",
            "expected_type": "english_text"
        }
    ]
    
    print("📊 翻译测试用例:")
    print("-" * 50)
    
    try:
        from api.prompt_translator import translate_prompt, get_translator
        
        translator = get_translator()
        if not translator:
            print("❌ 翻译器初始化失败")
            return
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. 原文: {case['chinese']}")
            
            # 检测语言
            is_chinese = translator.is_chinese_text(case['chinese'])
            print(f"   语言检测: {'中文' if is_chinese else '英文'}")
            
            # 执行翻译
            result = translate_prompt(case['chinese'])
            print(f"   翻译结果: {result}")
            
            # 分析结果
            if case['chinese'] == result and is_chinese:
                print("   ⚠️ 翻译失败，返回原文")
            elif not is_chinese and case['chinese'] == result:
                print("   ✅ 英文内容，无需翻译")
            else:
                print("   ✅ 翻译成功")
                
        print(f"\n{'='*50}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return
    
    print("\n💡 翻译服务特点:")
    print("-" * 20)
    print("• 自动检测中文内容")
    print("• 使用Gemini API进行智能翻译")
    print("• 专门优化视频生成描述")
    print("• 避免触发内容安全过滤器")
    print("• 备用翻译策略保证可用性")
    print("• 英文内容直接通过")
    
    print("\n🎯 优势对比:")
    print("-" * 15)
    print("旧方案：客户端替换敏感词 → '击败' → '点败'")
    print("新方案：服务器AI翻译 → '击败对手' → 'defeat the opponent'")
    print()
    print("✓ 保持语义完整性")
    print("✓ 英文更不容易被过滤")
    print("✓ 避免奇怪的中文替换")
    print("✓ 专业的视频生成描述")
    
    print("\n🚀 工作流程:")
    print("-" * 15)
    print("1. 用户输入中文提示词")
    print("2. 前端发送到后端API")
    print("3. 后端检测到中文内容")
    print("4. 调用Gemini API进行翻译")
    print("5. 使用英文提示词调用Veo API")
    print("6. 大大降低内容过滤概率")
    
    print("\n📈 预期效果:")
    print("-" * 15)
    print("• 内容过滤错误大幅减少")
    print("• 用户体验更流畅")
    print("• 无需学习英文描述")
    print("• 保持中文输入习惯")

def test_specific_cases():
    """测试特定的敏感词汇翻译"""
    print("\n🔍 敏感词汇翻译测试:")
    print("-" * 25)
    
    sensitive_cases = [
        "角色击败敌人",
        "人物攻击目标", 
        "战士拿着武器战斗",
        "爆炸场面很震撼",
        "血腥的战斗场面"
    ]
    
    try:
        from api.prompt_translator import translate_prompt
        
        for case in sensitive_cases:
            result = translate_prompt(case)
            print(f"'{case}' → '{result}'")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_translation_service()
    test_specific_cases()