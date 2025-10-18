#!/usr/bin/env python3
"""
简单测试Gemini API是否工作
"""
import os
import google.generativeai as genai

def test_gemini_api():
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API Key found")
    
    if not api_key:
        return False
    
    try:
        genai.configure(api_key=api_key)
        
        # 测试文本生成
        text_model = genai.GenerativeModel('gemini-2.5-flash')
        response = text_model.generate_content("Hello, are you working?")
        print(f"✅ 文本模型测试成功: {response.text[:50]}...")
        
        # 测试图像生成模型 - 尝试Nano Banana模型
        image_model = genai.GenerativeModel('gemini-2.5-flash-image')
        print("🔥 尝试Nano Banana图像生成...")
        image_response = image_model.generate_content("Create a cheerful cartoon cat playing in a sunny garden, colorful and child-friendly style")
        
        print(f"🔍 图像响应: {bool(image_response)}")
        if image_response and hasattr(image_response, 'candidates'):
            print(f"🔍 候选项: {len(image_response.candidates)}")
            if image_response.candidates and image_response.candidates[0].content:
                parts = image_response.candidates[0].content.parts
                print(f"🔍 内容部分: {len(parts)}")
                for i, part in enumerate(parts):
                    if hasattr(part, 'text') and part.text:
                        print(f"   Part {i}: 文本 = {part.text[:50]}...")
                    if hasattr(part, 'inline_data') and part.inline_data:
                        print(f"   Part {i}: 图像数据 = {len(part.inline_data.data)} bytes")
                        return True
        
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    print(f"\n{'✅ 成功' if success else '❌ 失败'}")