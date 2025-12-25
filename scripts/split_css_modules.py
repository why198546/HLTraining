"""
CSS智能拆分工具 - 根据注释和实际使用模式拆分
"""

import os
import re


def split_css_by_sections():
    """根据CSS中的注释标记智能拆分"""
    
    source_file = 'static/css/style.css'
    output_dir = 'static/css/modules'
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取原始CSS
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义模块边界（基于注释）
    modules = {
        'base.css': {
            'start': 0,
            'end_marker': '/* 导航栏样式 */',
            'description': '基础样式：变量、全局、重置'
        },
        'navigation.css': {
            'start_marker': '/* 导航栏样式 */',
            'end_marker': '/* Authentication Styles */',
            'description': '导航栏和Header'
        },
        'auth.css': {
            'start_marker': '/* Authentication Styles */',
            'end_marker': '/* My Artworks page */',
            'description': '认证和用户相关'
        },
        'gallery.css': {
            'start_marker': '/* Gallery页面样式 */',
            'end_marker': '/* Canvas',
            'description': '作品展示和画廊'
        },
        'classroom.css': {
            'start_marker': '/* 松果课堂',
            'end_marker': '/* 导航栏样式 */',
            'description': '松果课堂相关'
        },
    }
    
    # 执行拆分
    print("📦 开始拆分CSS文件...")
    print(f"📄 原始文件: {source_file} ({len(content)/1024:.1f} KB)")
    print()
    
    created_files = []
    
    # 1. 基础样式 (前3000行)
    lines = content.split('\n')
    base_css = '\n'.join(lines[:3000])
    base_file = os.path.join(output_dir, 'base.css')
    with open(base_file, 'w', encoding='utf-8') as f:
        f.write(base_css)
    created_files.append(('base.css', len(base_css), '基础样式：全局变量、重置、通用组件'))
    
    # 2. 导航栏样式
    nav_match = re.search(r'/\* 导航栏样式 \*/(.*?)(?=/\* Authentication Styles \*/|$)', content, re.DOTALL)
    if nav_match:
        nav_css = nav_match.group(0)
        nav_file = os.path.join(output_dir, 'navigation.css')
        with open(nav_file, 'w', encoding='utf-8') as f:
            f.write(nav_css)
        created_files.append(('navigation.css', len(nav_css), '导航栏和Header组件'))
    
    # 3. 认证样式
    auth_match = re.search(r'/\* Authentication Styles \*/(.*?)(?=/\* My Artworks page \*/|$)', content, re.DOTALL)
    if auth_match:
        auth_css = auth_match.group(0)
        auth_file = os.path.join(output_dir, 'auth.css')
        with open(auth_file, 'w', encoding='utf-8') as f:
            f.write(auth_css)
        created_files.append(('auth.css', len(auth_css), '登录注册和用户管理'))
    
    # 4. 作品展示
    gallery_match = re.search(r'/\* Gallery页面样式 \*/(.*?)(?=/\* Canvas|$)', content, re.DOTALL)
    if gallery_match:
        gallery_css = gallery_match.group(0)
        gallery_file = os.path.join(output_dir, 'gallery.css')
        with open(gallery_file, 'w', encoding='utf-8') as f:
            f.write(gallery_css)
        created_files.append(('gallery.css', len(gallery_css), '作品展示页面'))
    
    # 5. 松果课堂
    classroom_match = re.search(r'/\* 松果课堂.*?\*/(.*?)(?=/\* 导航栏样式 \*/|$)', content, re.DOTALL)
    if classroom_match:
        classroom_css = classroom_match.group(0)
        classroom_file = os.path.join(output_dir, 'classroom.css')
        with open(classroom_file, 'w', encoding='utf-8') as f:
            f.write(classroom_css)
        created_files.append(('classroom.css', len(classroom_css), '松果课堂相关'))
    
    # 6. 剩余部分作为pages.css
    pages_css = '\n'.join(lines[3000:])
    pages_file = os.path.join(output_dir, 'pages.css')
    with open(pages_file, 'w', encoding='utf-8') as f:
        f.write(pages_css)
    created_files.append(('pages.css', len(pages_css), '其他页面样式'))
    
    print("✅ CSS拆分完成！\n")
    print("📊 创建的模块文件：\n")
    
    total_size = 0
    for filename, size, desc in created_files:
        size_kb = size / 1024
        total_size += size
        print(f"  ✓ {filename:20} {size_kb:6.1f} KB  - {desc}")
    
    print(f"\n📈 总大小: {total_size/1024:.1f} KB")
    print(f"📉 原始大小: {len(content)/1024:.1f} KB")
    print(f"{'='*60}\n")
    
    return created_files

if __name__ == '__main__':
    split_css_by_sections()
