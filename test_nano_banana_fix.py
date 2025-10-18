#!/usr/bin/env python3
"""
测试修复后的Nano Banana图像生成功能
"""

import sys
import os
sys.path.append('.')

from api.nano_banana import NanoBananaAPI

def test_nano_banana_text_generation():
    """测试文字生成图片功能"""
    print("🧪 开始测试修复后的Nano Banana图像生成...")
    
    # 初始化API
    nano_api = NanoBananaAPI()
    
    # 检查API状态
    if not nano_api.check_api_status():
        print("❌ API状态检查失败，请检查GEMINI_API_KEY")
        return False
    
    # 测试文字生成图片
    test_prompt = "一只可爱的小猫咪在花园里玩耍，卡通风格，色彩明亮"
    print(f"📝 测试提示词: {test_prompt}")
    
    try:
        result_path = nano_api.generate_image_from_text(test_prompt)
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ 测试成功！图片已生成: {result_path}")
            print(f"📊 文件大小: {file_size} bytes")
            return True
        else:
            print(f"❌ 测试失败！文件不存在: {result_path}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_nano_banana_text_generation()
    
    if success:
        print("\n🎉 Nano Banana修复成功！现在可以正常生成图片了！")
    else:
        print("\n⚠️ 还有问题需要进一步调试...")
    
    sys.exit(0 if success else 1)