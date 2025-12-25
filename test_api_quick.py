"""快速测试API重构是否成功"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.nano_banana import NanoBananaAPI

def test_method_signature():
    """测试方法签名是否正确"""
    print("=" * 60)
    print("测试 1: 验证方法签名")
    print("=" * 60)
    
    api = NanoBananaAPI()
    
    # 检查方法是否存在
    if not hasattr(api, 'generate_image_from_reference'):
        print("❌ 错误: generate_image_from_reference 方法不存在")
        return False
    
    print("✅ generate_image_from_reference 方法存在")
    
    # 检查方法签名
    import inspect
    sig = inspect.signature(api.generate_image_from_reference)
    params = list(sig.parameters.keys())
    print(f"   参数列表: {params}")
    
    expected_params = ['sketch_path', 'description', 'style', 'aspect_ratio']
    if params == expected_params:
        print(f"✅ 参数签名正确: {expected_params}")
    else:
        print(f"❌ 参数签名不匹配")
        print(f"   期望: {expected_params}")
        print(f"   实际: {params}")
        return False
    
    # 检查默认值
    defaults = {
        'description': '',
        'style': 'cute',
        'aspect_ratio': '512x512'
    }
    
    for param_name, expected_default in defaults.items():
        param = sig.parameters[param_name]
        if param.default == expected_default:
            print(f"✅ {param_name} 默认值正确: {expected_default}")
        else:
            print(f"❌ {param_name} 默认值错误: 期望 {expected_default}, 实际 {param.default}")
            return False
    
    return True

def test_old_method_removed():
    """测试旧方法是否已移除"""
    print("\n" + "=" * 60)
    print("测试 2: 验证旧方法已移除")
    print("=" * 60)
    
    api = NanoBananaAPI()
    
    if hasattr(api, 'colorize_sketch'):
        print("❌ 警告: colorize_sketch 方法仍然存在！")
        return False
    else:
        print("✅ colorize_sketch 方法已移除")
        return True

def test_generate_image_from_text():
    """测试 generate_image_from_text 方法"""
    print("\n" + "=" * 60)
    print("测试 3: 验证 generate_image_from_text 签名")
    print("=" * 60)
    
    api = NanoBananaAPI()
    
    import inspect
    sig = inspect.signature(api.generate_image_from_text)
    params = list(sig.parameters.keys())
    print(f"   参数列表: {params}")
    
    expected_params = ['text_prompt', 'style', 'aspect_ratio']
    if params == expected_params:
        print(f"✅ 参数签名正确: {expected_params}")
    else:
        print(f"❌ 参数签名不匹配")
        print(f"   期望: {expected_params}")
        print(f"   实际: {params}")
        return False
    
    return True

def main():
    """运行所有测试"""
    print("\n🔍 API重构验证测试\n")
    
    tests = [
        ("方法签名验证", test_method_signature),
        ("旧方法移除验证", test_old_method_removed),
        ("文本生成方法验证", test_generate_image_from_text)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试出错: {test_name}")
            print(f"   错误: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！API重构成功！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == '__main__':
    exit(main())
