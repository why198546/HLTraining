#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的材质文件提取功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.hunyuan3d import Hunyuan3DGenerator

def test_material_extraction():
    """测试材质文件提取功能"""
    print("🧪 测试完整的材质文件提取...")
    
    # 使用已下载的ZIP文件
    zip_path = "models/hunyuan3d_boy_model.zip"
    
    if not os.path.exists(zip_path):
        print(f"❌ 测试文件不存在: {zip_path}")
        return
        
    print(f"📦 测试ZIP文件: {zip_path}")
    
    try:
        # 初始化3D生成器
        generator = Hunyuan3DGenerator()
        
        # 测试完整解压功能（包含材质）
        extracted_model = generator._extract_model_from_zip(
            zip_path, 
            "test_with_materials", 
            "87654321"
        )
        
        if extracted_model:
            print(f"✅ 解压测试成功: {extracted_model}")
            
            # 检查相关文件是否都存在
            base_path = os.path.splitext(extracted_model)[0]
            mtl_path = base_path + ".mtl"
            texture_path = base_path + "_texture.png"
            
            print(f"\n📁 检查提取的文件:")
            print(f"OBJ文件: {extracted_model} - {'✅存在' if os.path.exists(extracted_model) else '❌不存在'}")
            print(f"MTL文件: {mtl_path} - {'✅存在' if os.path.exists(mtl_path) else '❌不存在'}")
            print(f"贴图文件: {texture_path} - {'✅存在' if os.path.exists(texture_path) else '❌不存在'}")
            
            # 显示文件大小
            if os.path.exists(extracted_model):
                obj_size = os.path.getsize(extracted_model)
                print(f"📏 OBJ文件大小: {obj_size} 字节")
                
            if os.path.exists(mtl_path):
                mtl_size = os.path.getsize(mtl_path)
                print(f"📏 MTL文件大小: {mtl_size} 字节")
                
            if os.path.exists(texture_path):
                tex_size = os.path.getsize(texture_path)
                print(f"📏 贴图文件大小: {tex_size} 字节")
                
            # 查看MTL文件内容
            if os.path.exists(mtl_path):
                print(f"\n📄 MTL文件内容:")
                with open(mtl_path, 'r') as f:
                    content = f.read()
                    print(content[:500] + "..." if len(content) > 500 else content)
                    
        else:
            print("❌ 解压测试失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_material_extraction()