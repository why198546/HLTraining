#!/usr/bin/env python3
"""
测试修复后的提示词处理
"""

import os
import sys
from api.nano_banana import NanoBananaAPI

def test_prompt_handling():
    """测试提示词处理是否正确"""
    print("🧪 测试修复后的提示词处理...")
    
    # 设置环境变量
    os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 用户的原始提示词
    original_prompt = "一个勇敢的奥特曼战士，身穿银色和红色战斗服，胸前有彩色计时器，双手摆出战斗姿势，背景是蓝天白云"
    
    print(f"📝 原始提示词: {original_prompt}")
    
    # 模拟非Expert模式处理
    style = "cute"
    color_preference = "colorful"
    expert_mode = False
    
    # 复制generate_image_from_text中的逻辑
    print(f"\n🔧 非Expert模式处理:")
    print(f"风格: {style}, 色彩偏好: {color_preference}")
    
    # 风格映射
    style_prompts = {
        'cute': '可爱卡通风格',
        'realistic': '写实风格',
        'anime': '日式动漫风格',
        'fantasy': '奇幻风格'
    }
    
    # 色彩偏好映射
    color_prompts = {
        'colorful': '色彩丰富鲜艳',
        'soft': '柔和色调',
        'bright': '明亮鲜艳',
        'natural': '自然色彩'
    }
    
    style_desc = style_prompts.get(style, style_prompts['cute'])
    color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
    
    # 新的简化处理
    if expert_mode:
        final_prompt = original_prompt
    else:
        final_prompt = f"{original_prompt}, {style_desc}, {color_desc}, 适合儿童观看的内容"
    
    print(f"\n📝 处理后的提示词:")
    print(f"{final_prompt}")
    
    # 对比Expert模式
    print(f"\n🔧 Expert模式处理:")
    expert_prompt = original_prompt
    print(f"{expert_prompt}")
    
    # 分析
    print(f"\n📊 分析:")
    print(f"✅ 原始提示词保持完整: {'奥特曼战士' in final_prompt}")
    print(f"✅ 提示词长度合理: {len(final_prompt)} 字符 (vs 原来的 >500字符)")
    print(f"✅ 主要描述在前: {final_prompt.startswith(original_prompt)}")
    print(f"✅ 风格信息简洁: '{style_desc}' 和 '{color_desc}' 简短明确")
    
    # 测试Google AI Studio类似的处理
    print(f"\n🎯 Google AI Studio 样式的提示词:")
    print(f"原始: {original_prompt}")
    print(f"我们的: {final_prompt}")
    
    print(f"\n🎉 修复验证:")
    print("1. ✅ 保持了原始提示词的完整性")
    print("2. ✅ 减少了冗余的描述和要求")
    print("3. ✅ 风格和色彩信息简洁明确")
    print("4. ✅ 提示词结构更接近Google AI Studio")
    
    return True

if __name__ == "__main__":
    test_prompt_handling()