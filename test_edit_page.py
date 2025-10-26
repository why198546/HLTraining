#!/usr/bin/env python3
"""
编辑页面功能测试脚本
测试编辑页面的各种功能是否正常工作
"""

import requests
import sys
from urllib.parse import urljoin

def test_edit_page():
    """测试编辑页面功能"""
    base_url = "http://localhost:8080"
    
    print("🔍 开始测试编辑页面功能...")
    
    # 1. 测试编辑页面是否可访问
    try:
        edit_url = urljoin(base_url, "/edit/1")
        response = requests.get(edit_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 编辑页面可正常访问")
        elif response.status_code == 302:
            print("⚠️  编辑页面重定向（可能需要登录）")
        else:
            print(f"❌ 编辑页面访问异常，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 编辑页面访问失败: {e}")
        return False
        
    # 2. 测试CSS文件是否可访问
    try:
        css_url = urljoin(base_url, "/static/css/style.css")
        response = requests.get(css_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ CSS样式文件可正常访问")
            
            # 检查编辑页面相关样式是否存在
            css_content = response.text
            if "edit-artwork-container" in css_content:
                print("✅ 编辑页面样式已正确加载")
            else:
                print("❌ 编辑页面样式缺失")
        else:
            print(f"❌ CSS文件访问异常，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CSS文件访问失败: {e}")
        
    # 3. 测试我的作品页面（编辑页面入口）
    try:
        my_artworks_url = urljoin(base_url, "/my_artworks")
        response = requests.get(my_artworks_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 我的作品页面可正常访问")
        elif response.status_code == 302:
            print("⚠️  我的作品页面重定向（可能需要登录）")
        else:
            print(f"❌ 我的作品页面访问异常，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 我的作品页面访问失败: {e}")
        
    # 4. 测试主页是否正常
    try:
        home_url = base_url
        response = requests.get(home_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 主页可正常访问")
        else:
            print(f"❌ 主页访问异常，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 主页访问失败: {e}")
        
    print("\n📊 测试完成！")
    return True

def check_css_structure():
    """检查CSS结构"""
    print("\n🎨 检查CSS样式结构...")
    
    try:
        with open('/Users/hongyuwang/code/HLTraining/static/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # 检查关键样式类
        required_classes = [
            'edit-artwork-container',
            'artwork-preview', 
            'edit-form',
            'preview-section',
            'artwork-type-badge',
            'artwork-image',
            'form-group',
            'btn-primary',
            'btn-secondary'
        ]
        
        missing_classes = []
        for class_name in required_classes:
            if f'.{class_name}' not in css_content:
                missing_classes.append(class_name)
                
        if not missing_classes:
            print("✅ 所有必需的CSS类都已定义")
        else:
            print(f"❌ 缺少CSS类: {', '.join(missing_classes)}")
            
        # 检查响应式设计
        if '@media (max-width: 768px)' in css_content:
            print("✅ 响应式设计已实现")
        else:
            print("❌ 缺少响应式设计")
            
    except FileNotFoundError:
        print("❌ CSS文件不存在")
    except Exception as e:
        print(f"❌ CSS检查失败: {e}")

def check_template_structure():
    """检查模板结构"""
    print("\n📄 检查模板结构...")
    
    try:
        with open('/Users/hongyuwang/code/HLTraining/templates/edit_artwork.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # 检查关键元素
        required_elements = [
            'edit-artwork-container',
            'artwork-preview',
            'edit-form', 
            'preview-section',
            'form method="POST"',
            'input.*name="title"',
            'textarea.*name="description"',
            'input.*name="is_public"',
            'button.*type="submit"'
        ]
        
        import re
        missing_elements = []
        for element in required_elements:
            if not re.search(element, template_content):
                missing_elements.append(element)
                
        if not missing_elements:
            print("✅ 所有必需的模板元素都已定义")
        else:
            print(f"❌ 缺少模板元素: {', '.join(missing_elements)}")
            
    except FileNotFoundError:
        print("❌ 模板文件不存在")
    except Exception as e:
        print(f"❌ 模板检查失败: {e}")

if __name__ == "__main__":
    print("🚀 编辑页面完整性检查")
    print("=" * 50)
    
    # 运行所有测试
    test_edit_page()
    check_css_structure()
    check_template_structure()
    
    print("\n✨ 检查完成！")