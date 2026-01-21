#!/usr/bin/env python3
"""测试相机按钮功能是否正常"""

import requests
from bs4 import BeautifulSoup

# 测试页面加载
url = "http://localhost:8088/sunguo-class/character"
print(f"正在测试: {url}")

try:
    response = requests.get(url)
    print(f"✅ 页面状态码: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 检查相机按钮
    camera_buttons = soup.find_all('button', class_='camera-input-btn')
    print(f"\n📷 找到相机按钮数量: {len(camera_buttons)}")
    
    if camera_buttons:
        first_button = camera_buttons[0]
        print(f"   - onclick属性: {first_button.get('onclick')}")
        print(f"   - 按钮HTML: {first_button}")
    
    # 检查模态框
    modal = soup.find('div', id='camera-modal')
    if modal:
        print(f"\n✅ 找到模态框: id='camera-modal'")
        print(f"   - display样式: {modal.get('style')}")
    else:
        print("\n❌ 未找到模态框!")
    
    # 检查JavaScript文件引用
    scripts = soup.find_all('script', src=True)
    camera_script = None
    for script in scripts:
        src = script.get('src')
        if 'camera-input.js' in src:
            camera_script = src
            break
    
    if camera_script:
        print(f"\n✅ 找到JavaScript引用: {camera_script}")
        
        # 测试JavaScript文件是否可访问
        js_url = f"http://localhost:8088{camera_script}" if camera_script.startswith('/static') else camera_script
        js_response = requests.get(js_url)
        print(f"   - JS文件状态码: {js_response.status_code}")
        print(f"   - JS文件大小: {len(js_response.text)} 字节")
        
        # 检查关键函数
        js_content = js_response.text
        functions = ['openCameraModal', 'closeCameraModal', 'switchCameraTab', 'startCamera']
        for func in functions:
            if f"function {func}" in js_content:
                print(f"   - ✅ 找到函数: {func}")
            else:
                print(f"   - ❌ 未找到函数: {func}")
    else:
        print("\n❌ 未找到JavaScript文件引用!")
    
    print("\n" + "="*60)
    print("总结:")
    
    issues = []
    if len(camera_buttons) == 0:
        issues.append("❌ 页面中没有相机按钮")
    if not modal:
        issues.append("❌ 页面中没有模态框")
    if not camera_script:
        issues.append("❌ 页面中没有引用camera-input.js")
    
    if issues:
        print("发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ 所有必要元素都存在")
        print("\n如果点击按钮没有反应，可能是：")
        print("  1. 浏览器控制台有JavaScript错误")
        print("  2. JavaScript文件加载顺序问题")
        print("  3. 函数作用域问题")
        print("  4. CSS样式导致按钮不可点击")

except Exception as e:
    print(f"❌ 测试失败: {e}")
