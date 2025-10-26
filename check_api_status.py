#!/usr/bin/env python3
"""
检查API密钥和客户端状态
"""

import os
from dotenv import load_dotenv
from api.nano_banana import NanoBananaAPI

def check_api_status():
    """检查API状态"""
    print("🔍 检查API状态...")
    
    # 加载环境变量
    load_dotenv()
    print("✅ 环境变量已加载")
    
    # 检查环境变量
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY已设置 (长度: {len(api_key)})")
        if api_key.startswith('fake_'):
            print("⚠️  使用的是测试API密钥")
        elif api_key.startswith('AIzaSy'):
            print("✅ 使用真实Google API密钥")
        else:
            print(f"🔍 API密钥格式: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY未设置")
    
    # 创建API实例
    try:
        api = NanoBananaAPI()
        print(f"✅ API实例创建成功")
        print(f"🔍 客户端类型: {type(api.client)}")
        
        # 测试简单的提示词
        test_prompt = "一个勇敢的奥特曼战士"
        print(f"\n📝 测试提示词: {test_prompt}")
        
        # 只是测试提示词处理，不实际调用API
        print("🔧 测试提示词处理...")
        
        # 模拟non-expert模式处理
        style = "cute"
        color_preference = "colorful"
        
        style_prompts = {
            'cute': '可爱卡通风格',
            'realistic': '写实风格',
            'anime': '日式动漫风格',
            'fantasy': '奇幻风格'
        }
        
        color_prompts = {
            'colorful': '色彩丰富鲜艳',
            'soft': '柔和色调',
            'bright': '明亮鲜艳',
            'natural': '自然色彩'
        }
        
        style_desc = style_prompts.get(style, style_prompts['cute'])
        color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
        
        final_prompt = f"{test_prompt}, {style_desc}, {color_desc}, 适合儿童观看的内容"
        
        print(f"📝 处理后的提示词: {final_prompt}")
        print(f"✅ 提示词处理正常")
        
    except Exception as e:
        print(f"❌ API初始化失败: {str(e)}")

if __name__ == "__main__":
    check_api_status()