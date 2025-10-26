#!/usr/bin/env python3
"""
获取并显示最终的prompt
"""

import os
from dotenv import load_dotenv
from api.nano_banana import NanoBananaAPI

def get_final_prompt():
    """获取最终的prompt"""
    print("📝 获取最终的prompt...")
    
    # 加载环境变量
    load_dotenv()
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 用户的原始提示词
    original_prompt = "一个勇敢的奥特曼战士，身穿银色和红色战斗服，胸前有彩色计时器，双手摆出战斗姿势，背景是蓝天白云"
    
    # 测试参数
    style = "cute"
    color_preference = "colorful"
    expert_mode = False
    aspect_ratio = "9:16"
    
    print(f"📝 原始用户输入: {original_prompt}")
    print(f"🎨 风格: {style}")
    print(f"🌈 色彩偏好: {color_preference}")
    print(f"⚡ Expert模式: {expert_mode}")
    print(f"📐 高宽比: {aspect_ratio}")
    print("\n" + "="*80)
    
    # 模拟generate_image_from_text中的提示词处理逻辑
    if expert_mode:
        final_prompt = original_prompt
        print(f"🔥 Expert模式 - 最终prompt:")
        print(f"{final_prompt}")
    else:
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
        
        # 构建最终提示词
        final_prompt = f"{original_prompt}, {style_desc}, {color_desc}, 适合儿童观看的内容"
        
        print(f"🎯 非Expert模式 - 最终prompt:")
        print(f"{final_prompt}")
        
        print(f"\n📊 提示词分析:")
        print(f"  • 原始内容: {original_prompt}")
        print(f"  • 风格描述: {style_desc}")
        print(f"  • 色彩描述: {color_desc}")
        print(f"  • 安全标识: 适合儿童观看的内容")
        print(f"  • 总长度: {len(final_prompt)} 字符")
    
    print("\n" + "="*80)
    print(f"🚀 这个prompt将被发送给: imagen-3.0-generate-002")
    print(f"📐 配置的高宽比: {aspect_ratio}")
    print(f"🔧 输出格式: image/jpeg")
    
    # 对比Expert模式
    if not expert_mode:
        print(f"\n💡 如果启用Expert模式，prompt将是:")
        print(f"{original_prompt}")
        print(f"  • 长度: {len(original_prompt)} 字符 (vs {len(final_prompt)} 字符)")
    
    return final_prompt

if __name__ == "__main__":
    get_final_prompt()