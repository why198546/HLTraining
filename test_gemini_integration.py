#!/usr/bin/env python3
"""
测试 Gemini API 集成的脚本 - 纯Gemini模式
"""

import os
import sys
sys.path.append('/Users/hongyuwang/code/HLTraining')

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量文件 (.env) 加载成功")
except ImportError:
    print("⚠️  python-dotenv 未安装，无法自动加载 .env 文件")
    
# 检查API密钥
api_key = os.getenv('GEMINI_API_KEY')
if not api_key or api_key == 'your-api-key-here':
    print("❌ 未检测到有效的GEMINI_API_KEY环境变量")
    print("💡 请确保已正确配置.env文件")
    sys.exit(1)

from api.nano_banana import NanoBananaAPI

def test_api_integration():
    """测试Gemini API集成"""
    print("=== 纯Gemini API 集成测试 ===\n")
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 检查API状态
    if not api.client:
        print("❌ Gemini API 客户端初始化失败")
        return
    
    print("✅ Gemini API 客户端初始化成功")
    print(f"📱 API密钥状态: 已配置")
    
    print("\n=== 开始测试图像处理 ===\n")
    
    # 测试图像路径
    test_image = '/Users/hongyuwang/code/HLTraining/uploads/test_sketch.png'
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        print("💡 请先在网站上传一张测试图片，或手动创建测试图像")
        return
    
    try:
        # 测试图像上色
        print("🎨 测试图像上色功能...")
        colored_result = api.colorize_sketch(test_image)
        print(f"✅ 图像上色成功: {colored_result}")
        
        # 测试手办风格生成
        print("\n🏺 测试手办风格生成...")
        figurine_result = api.generate_figurine_style(colored_result)
        print(f"✅ 手办风格生成成功: {figurine_result}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        if "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️  Gemini API配额已用完，请等待配额重置")
        elif "API未配置" in str(e):
            print("⚠️  请检查Gemini API密钥配置")
    
    print("\n=== 测试完成 ===")
    
    # 显示文件列表
    uploads_dir = '/Users/hongyuwang/code/HLTraining/uploads'
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            print(f"\n📁 生成的文件 ({uploads_dir}):")
            for file in sorted(files):
                print(f"   - {file}")

if __name__ == "__main__":
    # 如果没有设置API密钥，提供说明
    if 'GEMINI_API_KEY' not in os.environ:
        print("⚠️  未检测到 GEMINI_API_KEY 环境变量")
        print("💡 如果您有Gemini API密钥，请设置环境变量：")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        print("💡 或者直接编辑 api/nano_banana.py 文件")
        print("\n🔄 将使用OpenCV备用方案进行测试...\n")
    
    test_api_integration()