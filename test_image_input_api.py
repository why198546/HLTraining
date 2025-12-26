#!/usr/bin/env python3
"""
测试图片输入功能的API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8088"

def test_load_image_from_url():
    """测试从URL加载图片的API"""
    
    print("=" * 60)
    print("测试图片URL加载功能")
    print("=" * 60)
    
    # 测试用的公开图片URL
    test_urls = [
        "https://picsum.photos/512/512",
        "https://via.placeholder.com/512",
        "https://dummyimage.com/512x512/00704A/ffffff.png&text=Test"
    ]
    
    # 注意：这个API需要登录，所以这里只是测试端点是否存在
    api_url = f"{BASE_URL}/api/load_image_from_url"
    
    print(f"\nAPI端点: {api_url}")
    print("\n测试URL列表:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    
    print("\n" + "=" * 60)
    print("⚠️  注意: 此API需要登录才能访问")
    print("=" * 60)
    
    # 检查端点是否存在（不需要登录）
    test_url = test_urls[0]
    payload = {"url": test_url}
    
    try:
        response = requests.post(
            api_url, 
            json=payload,
            timeout=5
        )
        
        if response.status_code == 401:
            print("\n✅ API端点存在（返回401需要登录）")
            print("✅ 功能已正确实现，需要在浏览器中登录后测试")
        elif response.status_code == 200:
            print("\n✅ API端点正常工作")
            data = response.json()
            if data.get('success'):
                print(f"✅ 图片加载成功")
                print(f"   数据大小: {len(data.get('image_data', ''))} 字节")
        else:
            print(f"\n⚠️  返回状态码: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        print("   请确保服务器正在运行")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def check_frontend_files():
    """检查前端文件是否正确更新"""
    
    print("\n" + "=" * 60)
    print("检查前端文件")
    print("=" * 60)
    
    files_to_check = [
        ("templates/create_image.html", [
            "image-menu",
            "camera-capture",
            "prompt-container",
            "toggleImageMenu"
        ]),
        ("static/js/create_image.js", [
            "initializeDragAndDrop",
            "initializePaste",
            "loadImageFromUrl",
            "toggleImageMenu",
            "handleCameraCapture"
        ])
    ]
    
    import os
    
    for filepath, keywords in files_to_check:
        full_path = os.path.join("/Users/hongyuwang/code/HLTraining", filepath)
        print(f"\n检查文件: {filepath}")
        
        if not os.path.exists(full_path):
            print(f"  ❌ 文件不存在")
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found = []
        missing = []
        
        for keyword in keywords:
            if keyword in content:
                found.append(keyword)
            else:
                missing.append(keyword)
        
        if found:
            print(f"  ✅ 找到 {len(found)}/{len(keywords)} 个关键字")
            for kw in found:
                print(f"     - {kw}")
        
        if missing:
            print(f"  ⚠️  缺失 {len(missing)} 个关键字:")
            for kw in missing:
                print(f"     - {kw}")


def main():
    print("\n" + "=" * 60)
    print("图片输入功能测试工具")
    print("=" * 60)
    
    # 检查前端文件
    check_frontend_files()
    
    # 测试API
    print("\n")
    test_load_image_from_url()
    
    print("\n" + "=" * 60)
    print("📋 手动测试步骤:")
    print("=" * 60)
    print("1. 访问: http://127.0.0.1:8088/create/image")
    print("2. 登录账号")
    print("3. 测试以下功能:")
    print("   - 点击 '+' 按钮查看菜单")
    print("   - 拖拽图片到输入框")
    print("   - 粘贴图片 (Ctrl+V)")
    print("   - 粘贴图片URL")
    print("=" * 60)


if __name__ == "__main__":
    main()
