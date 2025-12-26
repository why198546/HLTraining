#!/usr/bin/env python3
"""
最终检查清单 - 验证所有改动已正确实施
"""

import os
import json
import subprocess

def check_file_exists(filepath):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def check_string_in_file(filepath, search_string):
    """检查文件中是否包含特定字符串"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_string in content
            status = "✅" if found else "❌"
            print(f"  {status} 包含: '{search_string[:50]}...'")
            return found
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def run_syntax_check(filepath, is_python=True):
    """运行语法检查"""
    try:
        if is_python:
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
        else:
            result = subprocess.run(
                ["node", "-c", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
        
        if result.returncode == 0:
            print(f"  ✅ 语法正确")
            return True
        else:
            print(f"  ❌ 语法错误: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def main():
    print("=" * 80)
    print("🔍 松果课堂人物生成特征系统 - 最终检查清单")
    print("=" * 80)
    
    all_passed = True
    
    # 1. 检查后端改动
    print("\n📝 [1] 后端改动检查")
    print("-" * 80)
    
    gen_file = "/Users/hongyuwang/code/HLTraining/app/routes/api/generation.py"
    print(f"检查文件: {gen_file}")
    if check_file_exists(gen_file):
        print("\n  检查返回值修改:")
        all_passed &= check_string_in_file(gen_file, "return variations, mentioned_features")
        
        print("\n  检查detected_features在API响应中:")
        all_passed &= check_string_in_file(gen_file, "'detected_features': mentioned_features")
        
        print("\n  检查mentioned_features初始化:")
        all_passed &= check_string_in_file(gen_file, "mentioned_features = {}")
        
        print("\n  语法检查:")
        all_passed &= run_syntax_check(gen_file, is_python=True)
    else:
        all_passed = False
    
    # 2. 检查前端改动
    print("\n📝 [2] 前端改动检查")
    print("-" * 80)
    
    js_file = "/Users/hongyuwang/code/HLTraining/static/js/Sunguo_class.js"
    print(f"检查文件: {js_file}")
    if check_file_exists(js_file):
        print("\n  检查applyCommonSenseRules函数:")
        all_passed &= check_string_in_file(js_file, "function applyCommonSenseRules")
        
        print("\n  检查从API响应获取detected_features:")
        all_passed &= check_string_in_file(js_file, "data.detected_features")
        
        print("\n  检查第一张图不添加随机特征:")
        all_passed &= check_string_in_file(js_file, "if (i === 0) {")
        
        print("\n  检查getRandomVariations调用applyCommonSenseRules:")
        all_passed &= check_string_in_file(js_file, "applyCommonSenseRules(detectedFeatures, variations)")
        
        print("\n  语法检查:")
        all_passed &= run_syntax_check(js_file, is_python=False)
    else:
        all_passed = False
    
    # 3. 检查测试文件
    print("\n📝 [3] 测试文件检查")
    print("-" * 80)
    
    test_files = [
        "/Users/hongyuwang/code/HLTraining/test_feature_detection.py",
        "/Users/hongyuwang/code/HLTraining/test_api_response_format.py",
        "/Users/hongyuwang/code/HLTraining/test_common_sense_rules.js"
    ]
    
    for test_file in test_files:
        print(f"\n检查: {os.path.basename(test_file)}")
        if check_file_exists(test_file):
            is_python = test_file.endswith('.py')
            all_passed &= run_syntax_check(test_file, is_python=is_python)
        else:
            all_passed = False
    
    # 4. 检查文档
    print("\n📝 [4] 文档检查")
    print("-" * 80)
    
    doc_files = [
        "/Users/hongyuwang/code/HLTraining/FEATURE_SYSTEM_V3.md",
        "/Users/hongyuwang/code/HLTraining/CHANGES_SUMMARY.md"
    ]
    
    for doc_file in doc_files:
        print(f"\n检查: {os.path.basename(doc_file)}")
        all_passed &= check_file_exists(doc_file)
    
    # 5. 最终总结
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有检查通过！系统准备就绪。")
        print("\n下一步:")
        print("  1. 重启Flask服务器: python run.py")
        print("  2. 访问网站进行功能测试")
        print("  3. 在人物生成页面进行完整的特征测试")
        return 0
    else:
        print("❌ 有检查项未通过，请查看上面的错误信息。")
        return 1

if __name__ == '__main__':
    exit(main())
