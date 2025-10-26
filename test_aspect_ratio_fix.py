#!/usr/bin/env python3
"""
测试修复后的高宽比功能 - 使用新的Google Gen AI SDK
"""

import os
import sys
from api.nano_banana import NanoBananaAPI

def test_aspect_ratio_functionality():
    """测试高宽比功能是否正常工作"""
    print("🧪 开始测试修复后的高宽比功能...")
    
    # 检查环境变量
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ 环境变量GEMINI_API_KEY未设置")
        return False
    
    # 创建API实例
    api = NanoBananaAPI()
    
    # 测试不同的高宽比
    test_cases = [
        {"ratio": "1:1", "prompt": "一只可爱的小猫"},
        {"ratio": "16:9", "prompt": "一片美丽的海景"},
        {"ratio": "9:16", "prompt": "一座高高的塔"}
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n📐 测试高宽比: {case['ratio']}")
        print(f"📝 提示词: {case['prompt']}")
        
        try:
            result = api.generate_image_from_text(
                text_prompt=case['prompt'],
                style="cute",
                color_preference="colorful",
                expert_mode=False,
                aspect_ratio=case['ratio']
            )
            
            if result:
                print(f"✅ 成功生成图片: {result}")
                results.append({"ratio": case['ratio'], "success": True, "path": result})
            else:
                print(f"❌ 生成失败: {case['ratio']}")
                results.append({"ratio": case['ratio'], "success": False, "path": None})
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            results.append({"ratio": case['ratio'], "success": False, "error": str(e)})
    
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    for result in results:
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"  {result['ratio']}: {status}")
        if result.get('path'):
            print(f"    文件: {result['path']}")
        if result.get('error'):
            print(f"    错误: {result['error']}")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 测试通过")
    
    if success_count == total_count:
        print("🎉 所有高宽比测试都成功！高宽比功能已经修复！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查具体错误信息")
        return False

if __name__ == "__main__":
    test_aspect_ratio_functionality()