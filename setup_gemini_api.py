#!/usr/bin/env python3
"""
设置和测试真实Gemini API的演示脚本
"""

import os
import sys
sys.path.append('/Users/hongyuwang/code/HLTraining')

def setup_gemini_api():
    """设置Gemini API"""
    print("=== Gemini API 设置指南 ===\n")
    
    print("📋 步骤 1: 获取API密钥")
    print("1. 访问 https://aistudio.google.com/app/apikey")
    print("2. 登录您的Google账户")
    print("3. 点击 'Create API Key' 创建新的API密钥")
    print("4. 复制生成的API密钥")
    
    print("\n🔧 步骤 2: 设置API密钥")
    print("方法 1 - 使用环境变量（推荐）:")
    print("   export GEMINI_API_KEY='your-actual-api-key-here'")
    
    print("\n方法 2 - 直接在代码中设置:")
    print("   编辑 api/nano_banana.py 文件")
    print("   将 self.api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')")
    print("   改为 self.api_key = 'your-actual-api-key-here'")
    
    print("\n🧪 步骤 3: 测试API")
    print("设置完成后运行: python test_gemini_integration.py")
    
    # 交互式设置
    print("\n" + "="*50)
    api_key = input("请输入您的Gemini API密钥（或按Enter跳过）: ").strip()
    
    if api_key:
        # 临时测试API
        print("\n🔍 测试API密钥...")
        try:
            from google import genai
            
            # 创建临时客户端测试
            test_client = genai.Client(api_key=api_key)
            print("✅ API密钥格式正确，客户端创建成功")
            
            # 保存到环境变量（仅当前会话）
            os.environ['GEMINI_API_KEY'] = api_key
            print("✅ API密钥已设置到当前会话的环境变量")
            
            # 运行完整测试
            print("\n🚀 运行完整功能测试...")
            from api.nano_banana import NanoBananaAPI
            
            api = NanoBananaAPI()
            test_image = '/Users/hongyuwang/code/HLTraining/uploads/test_sketch.png'
            
            if os.path.exists(test_image):
                print("🎨 测试Gemini图像上色...")
                result = api.colorize_sketch(test_image)
                if result:
                    print(f"🎉 Gemini上色测试成功! 结果: {result}")
                else:
                    print("❌ 上色失败，可能是API配额或其他问题")
            else:
                print("⚠️  测试图像不存在，请先创建测试图像")
                
        except Exception as e:
            print(f"❌ API测试失败: {str(e)}")
            print("请检查您的API密钥是否正确")
    else:
        print("⏭️  跳过API密钥设置")
    
    print("\n📚 更多信息请查看:")
    print("   - GEMINI_API_SETUP.md 文件")
    print("   - https://ai.google.dev/gemini-api/docs")

if __name__ == "__main__":
    setup_gemini_api()