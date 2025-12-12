#!/usr/bin/env python3
"""
SAM 3D 集成测试脚本

测试 SAM 3D API 的基本功能和集成状态
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.sam3d_api import SAM3DAPI

def test_sam3d_initialization():
    """测试 SAM 3D API 初始化"""
    print("=" * 60)
    print("测试 1: SAM 3D API 初始化")
    print("=" * 60)
    
    try:
        sam3d = SAM3DAPI()
        print("✅ SAM 3D API 初始化成功")
        return True
    except Exception as e:
        print(f"❌ SAM 3D API 初始化失败: {str(e)}")
        return False

def test_sam3d_info():
    """测试获取 SAM 3D 模型信息"""
    print("\n" + "=" * 60)
    print("测试 2: 获取 SAM 3D 模型信息")
    print("=" * 60)
    
    try:
        sam3d = SAM3DAPI()
        info = sam3d.get_model_info()
        
        print("\n📊 SAM 3D 模型信息:")
        print(f"  名称: {info['name']}")
        print(f"  提供商: {info['provider']}")
        print(f"  版本: {info['version']}")
        print(f"  方法: {info['method']}")
        print(f"  输入格式: {info['input_format']}")
        print(f"  输出格式: {info['output_format']}")
        print(f"  状态: {info['status']}")
        print(f"  备注: {info['note']}")
        
        print("\n✅ 模型信息获取成功")
        return True
    except Exception as e:
        print(f"❌ 获取模型信息失败: {str(e)}")
        return False

def test_dependencies():
    """测试依赖包安装"""
    print("\n" + "=" * 60)
    print("测试 3: 检查依赖包")
    print("=" * 60)
    
    dependencies = {
        'huggingface_hub': 'Hugging Face Hub',
        'gradio_client': 'Gradio Client',
        'trimesh': 'Trimesh',
        'pygltflib': 'PyGLTFLib'
    }
    
    all_installed = True
    
    for package, name in dependencies.items():
        try:
            __import__(package)
            print(f"✅ {name} 已安装")
        except ImportError:
            print(f"❌ {name} 未安装")
            all_installed = False
    
    return all_installed

def test_directory_structure():
    """测试目录结构"""
    print("\n" + "=" * 60)
    print("测试 4: 检查目录结构")
    print("=" * 60)
    
    required_dirs = ['uploads', 'models']
    all_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            all_exist = False
    
    return all_exist

def test_api_routes():
    """测试 API 路由是否已添加"""
    print("\n" + "=" * 60)
    print("测试 5: 检查 API 路由")
    print("=" * 60)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        routes = [
            '/generate-3d-model-sam',
            '/compare-3d-engines',
            '/api/sam3d/info'
        ]
        
        all_found = True
        for route in routes:
            if route in content:
                print(f"✅ 路由 {route} 已添加")
            else:
                print(f"❌ 路由 {route} 未找到")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ 检查路由失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "🧪 SAM 3D 集成测试" + "\n")
    
    results = []
    
    # 运行所有测试
    results.append(("初始化测试", test_sam3d_initialization()))
    results.append(("模型信息测试", test_sam3d_info()))
    results.append(("依赖包测试", test_dependencies()))
    results.append(("目录结构测试", test_directory_structure()))
    results.append(("API路由测试", test_api_routes()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！SAM 3D 集成成功！")
        print("\n📝 下一步:")
        print("  1. 配置 Hugging Face Token (可选): export HUGGINGFACE_TOKEN='your-token'")
        print("  2. 启动应用: python app.py")
        print("  3. 访问 /api/sam3d/info 查看模型信息")
        print("  4. 等待 SAM 3D 官方 API 支持，或考虑本地部署")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())
