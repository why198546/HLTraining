#!/usr/bin/env python3
"""列出可用的Gemini模型"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ 未找到GEMINI_API_KEY环境变量")
    exit(1)

print(f"🔑 API密钥: {api_key[:10]}...")
print("\n🔍 正在获取可用模型列表...\n")

try:
    client = genai.Client(api_key=api_key)
    models = list(client.models.list())
    
    print(f"✅ 找到 {len(models)} 个模型\n")
    print("=" * 80)
    print("Gemini 模型列表:")
    print("=" * 80)
    
    gemini_models = [m for m in models if 'gemini' in m.name.lower()]
    for model in gemini_models:
        print(f"\n📦 {model.name}")
        if hasattr(model, 'display_name'):
            print(f"   显示名称: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"   描述: {model.description[:100] if model.description else 'N/A'}...")
            
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
