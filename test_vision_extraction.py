#!/usr/bin/env python3
"""
测试Vision提取功能 - 直接测试图片特征提取
"""
import sys
import os
from PIL import Image

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.nano_banana import NanoBananaAPI

def test_vision_extraction(image1_path, image2_path):
    """测试Vision提取"""
    print("="*80)
    print("🧪 开始测试Vision提取功能")
    print("="*80)
    
    # 检查图片是否存在
    if not os.path.exists(image1_path):
        print(f"❌ 图片1不存在: {image1_path}")
        return
    if not os.path.exists(image2_path):
        print(f"❌ 图片2不存在: {image2_path}")
        return
    
    print(f"\n📁 图片1 (人物照片): {image1_path}")
    img1 = Image.open(image1_path)
    print(f"   尺寸: {img1.size}")
    
    print(f"\n📁 图片2 (手绘作品): {image2_path}")
    img2 = Image.open(image2_path)
    print(f"   尺寸: {img2.size}")
    
    # 初始化API
    print("\n🔧 初始化Nano Banana API...")
    api = NanoBananaAPI()
    
    # 测试人物特征提取
    print("\n" + "="*80)
    print("【测试1】提取人物面部特征 (图片1)")
    print("="*80)
    person_desc = api.extract_person_features(image1_path)
    print(f"\n✅ 提取完成")
    print(f"📝 人物描述:\n{person_desc}")
    print(f"📏 描述长度: {len(person_desc)} 字符")
    
    # 测试服饰特征提取
    print("\n" + "="*80)
    print("【测试2】提取服饰/体态特征 (图片2)")
    print("="*80)
    outfit_desc = api.extract_artwork_features(image2_path)
    print(f"\n✅ 提取完成")
    print(f"📝 服饰描述:\n{outfit_desc}")
    print(f"📏 描述长度: {len(outfit_desc)} 字符")
    
    # 测试Prompt构建
    print("\n" + "="*80)
    print("【测试3】构建结构化Prompt")
    print("="*80)
    
    for style in ['realistic', 'cute', 'anime']:
        print(f"\n🎨 风格: {style}")
        prompt = api.build_structured_prompt(
            person_desc,
            outfit_desc,
            'color_mix',  # 课程类型
            style
        )
        print(f"📝 Prompt预览 (前200字):\n{prompt[:200]}...")
        print(f"📏 完整Prompt长度: {len(prompt)} 字符")
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80)

if __name__ == '__main__':
    # 如果命令行提供了图片路径
    if len(sys.argv) >= 3:
        image1 = sys.argv[1]
        image2 = sys.argv[2]
    else:
        # 使用默认测试图片（需要用户提供）
        print("使用方法:")
        print("  python test_vision_extraction.py <人物照片路径> <手绘作品路径>")
        print("\n示例:")
        print("  python test_vision_extraction.py uploads/photo.jpg uploads/artwork.png")
        
        # 尝试查找最近上传的图片
        temp_uploads = 'uploads'
        if os.path.exists(temp_uploads):
            files = sorted(
                [f for f in os.listdir(temp_uploads) if f.endswith(('.jpg', '.png', '.jpeg'))],
                key=lambda x: os.path.getmtime(os.path.join(temp_uploads, x)),
                reverse=True
            )
            if len(files) >= 2:
                print(f"\n💡 找到最近上传的图片，将使用它们进行测试:")
                image1 = os.path.join(temp_uploads, files[0])
                image2 = os.path.join(temp_uploads, files[1])
                print(f"   图片1: {files[0]}")
                print(f"   图片2: {files[1]}")
            else:
                print(f"\n❌ 在 {temp_uploads} 目录下找不到足够的测试图片")
                sys.exit(1)
        else:
            print(f"\n❌ uploads 目录不存在")
            sys.exit(1)
    
    test_vision_extraction(image1, image2)
