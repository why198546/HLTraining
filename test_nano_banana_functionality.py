#!/usr/bin/env python3
"""
测试 Nano Banana 图像生成功能完整性
"""

import os
import sys

def test_imports():
    """测试所有必需的导入"""
    print("=" * 60)
    print("测试 1: 检查导入")
    print("=" * 60)
    
    try:
        import flask
        print("✅ Flask 已安装")
    except ImportError as e:
        print(f"❌ Flask 未安装: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai 已安装")
    except ImportError as e:
        print(f"❌ google-generativeai 未安装: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow 已安装")
    except ImportError as e:
        print(f"❌ Pillow 未安装: {e}")
        return False
    
    try:
        import cv2
        print("✅ opencv-python 已安装")
    except ImportError as e:
        print(f"❌ opencv-python 未安装: {e}")
        return False
    
    print()
    return True


def test_api_structure():
    """测试 NanoBananaAPI 类结构"""
    print("=" * 60)
    print("测试 2: 检查 API 类结构")
    print("=" * 60)
    
    try:
        from api.nano_banana import NanoBananaAPI
        print("✅ NanoBananaAPI 类导入成功")
        
        # 检查必需的方法
        required_methods = [
            'colorize_sketch',
            'generate_figurine_style',
            'check_api_status',
            'generate_image_from_text'
        ]
        
        for method in required_methods:
            if hasattr(NanoBananaAPI, method):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 不存在")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_initialization():
    """测试 API 初始化"""
    print("=" * 60)
    print("测试 3: 测试 API 初始化")
    print("=" * 60)
    
    try:
        from api.nano_banana import NanoBananaAPI
        
        api = NanoBananaAPI()
        print("✅ API 初始化成功")
        
        # 检查属性
        if hasattr(api, 'client'):
            print(f"✅ client 属性存在: {api.client is not None}")
        else:
            print("❌ client 属性不存在")
            return False
        
        if hasattr(api, 'api_key'):
            print(f"✅ api_key 属性存在")
        else:
            print("❌ api_key 属性不存在")
            return False
        
        if hasattr(api, 'upload_folder'):
            print(f"✅ upload_folder 属性存在: {api.upload_folder}")
        else:
            print("❌ upload_folder 属性不存在")
            return False
        
        # 检查 API 状态
        status = api.check_api_status()
        print(f"✅ API 状态检查方法工作正常: status={status}")
        
        if not status:
            print("⚠️  注意: API 密钥未配置或无效（这是正常的，如果没有设置 GEMINI_API_KEY）")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_app():
    """测试 Flask 应用"""
    print("=" * 60)
    print("测试 4: 测试 Flask 应用")
    print("=" * 60)
    
    try:
        from app import app
        print("✅ Flask app 导入成功")
        
        # 检查配置
        print(f"✅ UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
        print(f"✅ MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
        
        # 检查关键路由
        with app.test_client() as client:
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            
            critical_routes = [
                '/generate-from-text',
                '/upload',
                '/colorize',
                '/uploads/<filename>'
            ]
            
            for route in critical_routes:
                if route in routes:
                    print(f"✅ 路由 {route} 已注册")
                else:
                    print(f"❌ 路由 {route} 未注册")
                    return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Flask 应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_directories():
    """测试必需的目录"""
    print("=" * 60)
    print("测试 5: 测试目录结构")
    print("=" * 60)
    
    required_dirs = ['uploads', 'static', 'templates', 'api']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ 目录 {dir_name} 存在")
        else:
            print(f"❌ 目录 {dir_name} 不存在")
            return False
    
    print()
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Nano Banana 功能完整性测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("导入测试", test_imports),
        ("API 结构测试", test_api_structure),
        ("API 初始化测试", test_api_initialization),
        ("Flask 应用测试", test_flask_app),
        ("目录结构测试", test_directories)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试 {name} 执行失败: {e}")
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Nano Banana 功能已正确实现。")
        print("\n📝 注意事项:")
        print("   1. 需要设置 GEMINI_API_KEY 环境变量才能使用 AI 图像生成")
        print("   2. 没有 API 密钥时，系统会自动使用备用方案")
        print("   3. 运行 'export GEMINI_API_KEY=your-key' 来配置 API 密钥")
        return True
    else:
        print(f"\n❌ {total - passed} 个测试失败。请检查上述错误信息。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
