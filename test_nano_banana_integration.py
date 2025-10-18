#!/usr/bin/env python3
"""
测试 Nano Banana (Gemini) API 集成
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

from api.nano_banana import NanoBananaAPI

def test_nano_banana_api():
    """测试Nano Banana API"""
    print("=== Nano Banana (Gemini) API 测试 ===\n")
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 检查API状态
    if not api.check_api_status():
        print("❌ Nano Banana API 未正确配置")
        return
    
    print("✅ Nano Banana API 已准备就绪")
    
    # 测试图像路径
    test_image = '/Users/hongyuwang/code/HLTraining/uploads/test_sketch.png'
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        return
    
    try:
        # 测试上色功能（带描述）
        print("\n🎨 测试带描述的图像上色功能...")
        description = "把这个笑脸涂成黄色，眼睛涂成黑色，嘴巴涂成红色，背景加上蓝色"
        colored_result = api.colorize_sketch(test_image, description)
        print(f"✅ 上色成功: {colored_result}")
        
        # 测试手办风格生成（带描述）
        print("\n🏺 测试带描述的手办风格生成...")
        figurine_description = "增加金属光泽效果，让它看起来像高档收藏品"
        figurine_result = api.generate_figurine_style(colored_result, figurine_description)
        print(f"✅ 手办风格生成成功: {figurine_result}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        if "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️  Gemini API配额已用完，请等待配额重置或升级付费版本")
        elif "API未配置" in str(e):
            print("⚠️  请检查GEMINI_API_KEY配置")
    
    print("\n=== 测试完成 ===")
    
    # 显示生成的文件
    uploads_dir = '/Users/hongyuwang/code/HLTraining/uploads'
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            print(f"\n📁 生成的文件 ({uploads_dir}):")
            for file in sorted(files):
                print(f"   - {file}")

if __name__ == "__main__":
    test_nano_banana_api()