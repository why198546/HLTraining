#!/usr/bin/env python3
"""
测试奥特曼角色生成问题
"""

import os
import sys
from api.nano_banana import NanoBananaAPI

def test_ultraman_generation():
    """测试奥特曼角色生成"""
    print("🧪 开始测试奥特曼角色生成问题...")
    
    # 检查环境变量（使用假密钥测试提示词处理逻辑）
    os.environ['GEMINI_API_KEY'] = 'fake_key_for_testing'
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 原始用户提示词
    original_prompt = "一个勇敢的奥特曼战士，身穿银色和红色战斗服，胸前有彩色计时器，双手摆出战斗姿势，背景是蓝天白云"
    
    print(f"📝 原始提示词: {original_prompt}")
    
    # 模拟非Expert模式的提示词构建过程
    try:
        # 复制generate_image_from_text中的逻辑
        style = "cute"
        color_preference = "colorful"
        
        style_prompts = {
            'cute': '可爱卡通风格，圆润的线条，柔和的造型，Q版比例',
            'realistic': '写实风格，真实的光影效果，细腻的质感',
            'anime': '日式动漫风格，清晰的线条，大眼睛，高对比度',
            'fantasy': '奇幻风格，魔法光效，梦幻色彩，炫目的视觉效果'
        }
        
        color_prompts = {
            'colorful': '色彩丰富鲜艳，饱和度高，充满活力',
            'soft': '柔和色调，低饱和度，温柔的粉色系或米色系',
            'bright': '明亮鲜艳的颜色，高亮度，高对比度',
            'natural': '自然色彩，大地色系，贴近真实物体的颜色'
        }
        
        style_desc = style_prompts.get(style, style_prompts['cute'])
        color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
        
        # 构建最终提示词
        final_prompt = f"""创建一幅适合10-14岁儿童的插画：{original_prompt}

风格要求：{style_desc}
色彩要求：{color_desc}

基本要求：
- 适合儿童观看，健康正面的内容
- 富有创意和想象力
- 简洁清晰的构图
- 背景简洁干净，避免杂乱元素
- 主体突出，背景纯色或简单渐变
- 整体风格统一，色彩和谐"""
        
        print(f"\n📝 处理后的提示词:")
        print(final_prompt)
        
        # 分析问题
        print(f"\n🔍 问题分析:")
        
        # 检查是否包含可能被过滤的词汇
        potentially_filtered = ["奥特曼", "战士", "战斗"]
        found_filtered = [word for word in potentially_filtered if word in original_prompt]
        
        if found_filtered:
            print(f"⚠️  发现可能被内容过滤的词汇: {found_filtered}")
            print("💡 建议: 这些词汇可能触发Imagen模型的内容安全过滤器")
        
        # 检查提示词复杂度
        if len(final_prompt) > 500:
            print(f"⚠️  提示词过长: {len(final_prompt)} 字符")
            print("💡 建议: 简化提示词可能有助于更好的生成效果")
        
        # 提供解决方案
        print(f"\n🔧 建议的解决方案:")
        
        # 方案1：Expert模式简化版
        expert_prompt = original_prompt
        print(f"1. Expert模式(直接使用原提示词):")
        print(f"   {expert_prompt}")
        
        # 方案2：替换敏感词汇
        safe_prompt = original_prompt.replace("奥特曼", "超级英雄").replace("战士", "英雄").replace("战斗", "行动")
        safe_final = f"""创建一幅适合10-14岁儿童的插画：{safe_prompt}

风格要求：{style_desc}
色彩要求：{color_desc}

基本要求：
- 适合儿童观看，健康正面的内容
- 富有创意和想象力
- 简洁清晰的构图"""
        
        print(f"\n2. 安全词汇替换版:")
        print(f"   {safe_final}")
        
        # 方案3：完全重新设计
        redesigned_prompt = f"""创建一幅可爱的超级英雄插画：
一个身穿银红色制服的友善英雄角色，胸前有发光的圆形装置，双手做出欢迎手势，站在蓝天白云背景前

风格：{style_desc}
色彩：{color_desc}"""
        
        print(f"\n3. 重新设计版:")
        print(f"   {redesigned_prompt}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        return False

if __name__ == "__main__":
    test_ultraman_generation()