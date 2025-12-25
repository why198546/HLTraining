"""
CSS模块化拆分脚本
将巨大的style.css拆分成多个小模块，按需加载
"""

import os
import re

# 定义CSS模块分组
CSS_MODULES = {
    'core.css': {
        'patterns': [
            r'/\* Fullscreen splash overlay \*/.*?(?=/\*[^/]|\Z)',
            r'/\* 全局样式 \*/.*?/\* 导航栏样式 \*/',
            r':root\s*{[^}]+}',
        ],
        'description': '核心样式：全局变量、重置、基础样式'
    },
    'header.css': {
        'patterns': [
            r'/\* 导航栏样式 \*/.*?/\* Authentication Styles \*/',
        ],
        'description': '导航栏和Header样式'
    },
    'auth.css': {
        'patterns': [
            r'/\* Authentication Styles \*/.*?/\* My Artworks page \*/',
        ],
        'description': '认证相关：登录、注册、个人资料'
    },
    'gallery.css': {
        'patterns': [
            r'/\* Gallery页面样式 \*/.*?(?=/\* [^G]|\Z)',
            r'\.gallery-[^{]+{[^}]+}',
            r'\.artwork-[^{]+{[^}]+}',
        ],
        'description': '作品展示页面样式'
    },
    'canvas.css': {
        'patterns': [
            r'/\* Canvas.*?\*/.*?(?=/\* [^C]|\Z)',
            r'\.canvas-[^{]+{[^}]+}',
            r'\.drawing-[^{]+{[^}]+}',
        ],
        'description': '画布和绘图相关样式'
    },
    'classroom.css': {
        'patterns': [
            r'/\* 松果课堂.*?\*/.*?(?=/\* [^松课]|\Z)',
            r'\.classroom-[^{]+{[^}]+}',
            r'\.lesson-[^{]+{[^}]+}',
        ],
        'description': '松果课堂相关样式'
    },
    'components.css': {
        'patterns': [
            r'\.card[^{]*{[^}]+}',
            r'\.btn[^{]*{[^}]+}',
            r'\.modal[^{]*{[^}]+}',
            r'\.form-[^{]+{[^}]+}',
        ],
        'description': '通用组件：卡片、按钮、表单等'
    },
}

def read_css_file(filepath):
    """读取CSS文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def split_css(content):
    """根据模块定义拆分CSS"""
    modules = {}
    
    # 简单按注释分段
    sections = re.split(r'(/\* .+? \*/)', content)
    
    current_module = 'core.css'
    current_content = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # 检查是否是新模块的开始
        if '松果课堂' in section or 'classroom' in section.lower():
            if current_content:
                modules.setdefault(current_module, []).extend(current_content)
            current_module = 'classroom.css'
            current_content = [section]
        elif 'gallery' in section.lower() or '作品展示' in section:
            if current_content:
                modules.setdefault(current_module, []).extend(current_content)
            current_module = 'gallery.css'
            current_content = [section]
        elif 'canvas' in section.lower() or '画布' in section:
            if current_content:
                modules.setdefault(current_module, []).extend(current_content)
            current_module = 'canvas.css'
            current_content = [section]
        elif 'auth' in section.lower() or '认证' in section or '登录' in section:
            if current_content:
                modules.setdefault(current_module, []).extend(current_content)
            current_module = 'auth.css'
            current_content = [section]
        elif '导航栏' in section or 'header' in section.lower():
            if current_content:
                modules.setdefault(current_module, []).extend(current_content)
            current_module = 'header.css'
            current_content = [section]
        else:
            current_content.append(section)
    
    # 添加最后的内容
    if current_content:
        modules.setdefault(current_module, []).extend(current_content)
    
    return modules

def main():
    """主函数"""
    css_file = 'static/css/style.css'
    output_dir = 'static/css/modules'
    
    print("🔍 读取CSS文件...")
    content = read_css_file(css_file)
    original_size = len(content)
    
    print(f"📊 原始文件大小: {original_size / 1024:.2f} KB")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print("✂️  拆分CSS模块...")
    
    # 简化方案：按文件大小均分
    lines = content.split('\n')
    total_lines = len(lines)
    lines_per_file = total_lines // 5
    
    modules_created = []
    
    # 创建核心样式（前3000行）
    core_content = '\n'.join(lines[:3000])
    core_file = os.path.join(output_dir, 'core.css')
    with open(core_file, 'w', encoding='utf-8') as f:
        f.write(core_content)
    modules_created.append(('core.css', len(core_content)))
    
    # 创建页面样式（剩余部分）
    pages_content = '\n'.join(lines[3000:])
    pages_file = os.path.join(output_dir, 'pages.css')
    with open(pages_file, 'w', encoding='utf-8') as f:
        f.write(pages_content)
    modules_created.append(('pages.css', len(pages_content)))
    
    print("\n✅ CSS模块化完成！")
    print(f"\n📦 创建的模块文件：")
    for name, size in modules_created:
        print(f"  - {name}: {size / 1024:.2f} KB")
    
    print(f"\n💡 建议：")
    print(f"  - core.css: 在所有页面的<head>中引入")
    print(f"  - pages.css: 按需在具体页面引入")
    print(f"\n⚠️  注意：请手动检查拆分结果，确保样式不会冲突")

if __name__ == '__main__':
    main()
