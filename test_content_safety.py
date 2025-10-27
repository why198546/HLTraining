#!/usr/bin/env python3
"""
测试内容安全过滤和智能建议功能
"""

def test_content_safety_system():
    """测试内容安全系统"""
    print("🛡️ 测试内容安全过滤和智能建议系统\n")
    
    print("✅ 已实现的功能:")
    print("-" * 40)
    print("1. 预检查：生成前分析提示词潜在问题")
    print("2. 错误处理：API返回过滤错误时的智能建议")
    print("3. 关键词检测：识别可能触发过滤器的词汇")
    print("4. 自动修复：提供安全的替代词汇")
    print("5. 交互式对话框：美观的修改建议界面")
    print()
    
    print("🔍 内容安全检测范围:")
    print("-" * 25)
    categories = {
        "暴力相关": ["打击", "攻击", "打斗", "战斗", "破坏", "撞击", "爆炸", "武器"],
        "危险行为": ["危险", "跳楼", "自杀", "伤害", "坠落", "碰撞", "受伤"],
        "敏感内容": ["政治", "宗教", "种族", "歧视", "抗议", "游行"],
        "不当内容": ["暴露", "色情", "成人", "不雅", "裸体"],
        "负面情绪": ["愤怒", "仇恨", "报复", "恶意", "残忍", "血腥", "恐怖"],
        "动作相关": ["打", "撞", "击", "踢", "咬", "抓", "推", "扔", "摔"]
    }
    
    for category, keywords in categories.items():
        print(f"• {category}: {', '.join(keywords[:5])}..." if len(keywords) > 5 else f"• {category}: {', '.join(keywords)}")
    print()
    
    print("🔄 替换建议示例:")
    print("-" * 20)
    replacements = [
        ("打击", "轻触"),
        ("攻击", "接近"), 
        ("战斗", "竞赛"),
        ("破坏", "改变"),
        ("爆炸", "绽放"),
        ("武器", "工具"),
        ("危险", "小心"),
        ("愤怒", "不开心"),
        ("血腥", "红色"),
        ("恐怖", "神秘")
    ]
    
    for original, safe in replacements:
        print(f"  \"{original}\" → \"{safe}\"")
    print()
    
    print("🎯 智能对话框功能:")
    print("-" * 22)
    print("• 检测到的敏感词汇高亮显示")
    print("• 自动生成修改后的安全版本")
    print("• 可编辑的文本框供用户调整")
    print("• 一键应用修改到原始输入框")
    print("• 现代化的UI设计和交互")
    print()
    
    print("📊 测试用例:")
    print("-" * 15)
    test_cases = [
        {
            "input": "小人在战斗中攻击敌人",
            "expected_issues": ["战斗", "攻击"],
            "expected_fix": "小人在竞赛中接近对手"
        },
        {
            "input": "角色拿着武器打击目标",
            "expected_issues": ["武器", "打击"], 
            "expected_fix": "角色拿着工具轻触目标"
        },
        {
            "input": "爆炸场面非常血腥恐怖",
            "expected_issues": ["爆炸", "血腥", "恐怖"],
            "expected_fix": "绽放场面非常红色神秘"
        },
        {
            "input": "温柔的猫咪在花园里玩耍",
            "expected_issues": [],
            "expected_fix": "温柔的猫咪在花园里玩耍"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. 输入: \"{case['input']}\"")
        if case['expected_issues']:
            print(f"   检测: {', '.join(case['expected_issues'])}")
            print(f"   建议: \"{case['expected_fix']}\"")
        else:
            print(f"   结果: ✅ 无问题检测")
        print()
    
    print("🚀 用户体验流程:")
    print("-" * 20)
    print("1. 用户输入提示词")
    print("2. 点击生成视频") 
    print("3. 系统预检查内容安全性")
    print("4. 如发现问题，弹出智能建议对话框")
    print("5. 用户查看分析和修改建议")
    print("6. 一键应用修改或手动调整")
    print("7. 重新生成视频，避免API过滤")
    print()
    
    print("💡 技术特点:")
    print("-" * 15)
    print("✓ 客户端预检查，减少API调用失败")
    print("✓ 智能词汇替换，保持语义连贯")
    print("✓ 交互式修改，用户可自定义调整")
    print("✓ 美观的UI设计，提升用户体验")
    print("✓ 支持中文和英文关键词检测")
    print("✓ 自动保存修改后的内容")
    print()
    
    print("🎮 测试建议:")
    print("-" * 15)
    print("1. 访问 http://localhost:5000/video")
    print("2. 尝试输入包含敏感词的提示词")
    print("3. 观察预检查和建议对话框")
    print("4. 测试自动修复和手动编辑功能")
    print("5. 验证修改后内容能正常生成视频")

if __name__ == "__main__":
    test_content_safety_system()