"""
CSS按页面需求拆分 - 创建轻量级模块
策略：
1. core.css - 所有页面都需要的基础样式（< 50KB）
2. page-*.css - 每个页面特定的样式
"""

import os


def create_optimized_modules():
    """创建优化的CSS模块"""
    
    source_file = 'static/css/style.css'
    output_dir = 'static/css/modules'
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    print(f"📄 原始文件: {total_lines} 行 ({len(content)/1024:.1f} KB)\n")
    
    # 核心样式：前1500行（全局、变量、导航、基础组件）
    core_lines = lines[:1500]
    core_css = '\n'.join(core_lines)
    
    with open(os.path.join(output_dir, 'core.css'), 'w', encoding='utf-8') as f:
        f.write(core_css)
    print(f"✓ core.css: {len(core_lines)} 行 ({len(core_css)/1024:.1f} KB) - 基础样式")
    
    # 认证页面样式：行 1500-2500
    auth_lines = lines[1500:2500]
    auth_css = '\n'.join(auth_lines)
    
    with open(os.path.join(output_dir, 'page-auth.css'), 'w', encoding='utf-8') as f:
        f.write(auth_css)
    print(f"✓ page-auth.css: {len(auth_lines)} 行 ({len(auth_css)/1024:.1f} KB) - 登录注册")
    
    # 作品展示：行 2500-4500
    gallery_lines = lines[2500:4500]
    gallery_css = '\n'.join(gallery_lines)
    
    with open(os.path.join(output_dir, 'page-gallery.css'), 'w', encoding='utf-8') as f:
        f.write(gallery_css)
    print(f"✓ page-gallery.css: {len(gallery_lines)} 行 ({len(gallery_css)/1024:.1f} KB) - 作品展示")
    
    # 创作页面：行 4500-6500
    create_lines = lines[4500:6500]
    create_css = '\n'.join(create_lines)
    
    with open(os.path.join(output_dir, 'page-create.css'), 'w', encoding='utf-8') as f:
        f.write(create_css)
    print(f"✓ page-create.css: {len(create_lines)} 行 ({len(create_css)/1024:.1f} KB) - AI创作")
    
    # 画布相关：行 6500-8500
    canvas_lines = lines[6500:8500]
    canvas_css = '\n'.join(canvas_lines)
    
    with open(os.path.join(output_dir, 'page-canvas.css'), 'w', encoding='utf-8') as f:
        f.write(canvas_css)
    print(f"✓ page-canvas.css: {len(canvas_lines)} 行 ({len(canvas_css)/1024:.1f} KB) - 画布功能")
    
    # 课堂相关：行 8500-10000
    classroom_lines = lines[8500:10000]
    classroom_css = '\n'.join(classroom_lines)
    
    with open(os.path.join(output_dir, 'page-classroom.css'), 'w', encoding='utf-8') as f:
        f.write(classroom_css)
    print(f"✓ page-classroom.css: {len(classroom_lines)} 行 ({len(classroom_css)/1024:.1f} KB) - 松果课堂")
    
    # 管理后台：行 10000-结尾
    admin_lines = lines[10000:]
    admin_css = '\n'.join(admin_lines)
    
    with open(os.path.join(output_dir, 'page-admin.css'), 'w', encoding='utf-8') as f:
        f.write(admin_css)
    print(f"✓ page-admin.css: {len(admin_lines)} 行 ({len(admin_css)/1024:.1f} KB) - 管理后台")
    
    print(f"\n{'='*70}")
    print("✅ CSS模块化完成！")
    print(f"\n💡 使用建议：")
    print(f"  - 所有页面都引入: core.css")
    print(f"  - 登录注册页: + page-auth.css")
    print(f"  - 作品展示页: + page-gallery.css")
    print(f"  - AI创作页: + page-create.css")
    print(f"  - 画布功能: + page-canvas.css")
    print(f"  - 松果课堂: + page-classroom.css")
    print(f"  - 管理后台: + page-admin.css")

if __name__ == '__main__':
    create_optimized_modules()
