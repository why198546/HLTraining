#!/usr/bin/env python3
"""
测试 Gemini API 集成的脚本
"""

import os
import sys
sys.path.append('/Users/hongyuwang/code/HLTraining')

from api.nano_banana import NanoBananaAPI

def test_api_integration():
    """测试API集成"""
    print("=== Gemini API 集成测试 ===\n")
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 检查API状态
    if api.client:
        print("✅ Gemini API 客户端初始化成功")
        print(f"📱 API密钥状态: {'已设置' if api.api_key != 'your-api-key-here' else '需要设置'}")
    else:
        print("❌ Gemini API 客户端初始化失败")
        print("⚠️  将使用OpenCV备用方案")
    
    print("\n=== 开始测试图像处理 ===\n")
    
    # 测试图像路径
    test_image = '/Users/hongyuwang/code/HLTraining/uploads/test_sketch.png'
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        print("请先运行以下命令创建测试图像：")
        print("python -c \"import cv2; import numpy as np; img = np.ones((300, 300, 3), dtype=np.uint8) * 255; cv2.circle(img, (150, 150), 80, (0, 0, 0), 3); cv2.circle(img, (130, 130), 10, (0, 0, 0), -1); cv2.circle(img, (170, 130), 10, (0, 0, 0), -1); cv2.ellipse(img, (150, 170), (30, 15), 0, 0, 180, (0, 0, 0), 3); cv2.imwrite('uploads/test_sketch.png', img)\"")
        return
    
    # 测试图像上色
    print("🎨 测试图像上色功能...")
    colored_result = api.colorize_sketch(test_image)
    
    if colored_result:
        print(f"✅ 图像上色成功: {colored_result}")
        
        # 测试手办风格生成
        print("\n🏺 测试手办风格生成...")
        figurine_result = api.generate_figurine_style(colored_result)
        
        if figurine_result:
            print(f"✅ 手办风格生成成功: {figurine_result}")
        else:
            print("❌ 手办风格生成失败")
    else:
        print("❌ 图像上色失败")
    
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