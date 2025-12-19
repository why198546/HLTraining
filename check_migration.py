#!/usr/bin/env python3
"""检查app.py迁移状态"""
import re
from collections import defaultdict

def analyze_routes():
    # 读取app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # 提取所有@app.route路由
    app_routes = re.findall(r"@app\.route\('([^']+)'(?:,\s*methods=\[([^\]]+)\])?\)", app_content)
    
    # 按功能分组
    groups = {
        '✅ Canvas功能 (已迁移到app/routes/canvas.py和api.py)': [],
        '✅ 创作相关 (已迁移到app/routes/create.py和api.py)': [],
        '✅ 画廊相关 (已迁移到app/routes/gallery.py和api.py)': [],
        '✅ 视频功能 (已迁移到app/routes/video.py和api.py)': [],
        '✅ 静态文件 (已迁移到app/routes/static_files.py)': [],
        '✅ API接口 (已迁移到app/routes/api.py)': [],
        '✅ 主页和测试页 (已迁移到app/routes/main.py)': [],
        '❌ 3D模型功能 (需要迁移到app/routes/model3d.py)': [],
        '❌ Session管理 (需要迁移到app/routes/api.py)': [],
    }
    
    for route_info in app_routes:
        route = route_info[0]
        methods = route_info[1] if route_info[1] else 'GET'
        
        if '/canvas' in route:
            groups['✅ Canvas功能 (已迁移到app/routes/canvas.py和api.py)'].append(f"{route} [{methods}]")
        elif '/edit' in route:
            groups['✅ 创作相关 (已迁移到app/routes/create.py和api.py)'].append(f"{route} [{methods}]")
        elif '/gallery' in route or '/feature' in route or '/vote' in route or '/unfeature' in route or '/increment-view' in route:
            groups['✅ 画廊相关 (已迁移到app/routes/gallery.py和api.py)'].append(f"{route} [{methods}]")
        elif '/video' in route:
            groups['✅ 视频功能 (已迁移到app/routes/video.py和api.py)'].append(f"{route} [{methods}]")
        elif '/uploads/' in route or '/models/' in route or '/creation_sessions/' in route or route.startswith('/static/'):
            groups['✅ 静态文件 (已迁移到app/routes/static_files.py)'].append(f"{route} [{methods}]")
        elif route.startswith('/api/'):
            groups['✅ API接口 (已迁移到app/routes/api.py)'].append(f"{route} [{methods}]")
        elif route in ['/', '/sunguo-class', '/tutorial', '/test', '/debug', '/test-controls', '/simple-test', '/test-3d', '/test-model', '/test-privacy-toggles', '/test-content-indicators'] or route.startswith('/sunguo-class/'):
            groups['✅ 主页和测试页 (已迁移到app/routes/main.py)'].append(f"{route} [{methods}]")
        elif '3d' in route.lower() or '/generate-multi-view' in route or '/compare-3d-engines' in route:
            groups['❌ 3D模型功能 (需要迁移到app/routes/model3d.py)'].append(f"{route} [{methods}]")
        elif '/session' in route or 'session' in route:
            groups['❌ Session管理 (需要迁移到app/routes/api.py)'].append(f"{route} [{methods}]")
        elif '/create' in route:
            groups['✅ 创作相关 (已迁移到app/routes/create.py和api.py)'].append(f"{route} [{methods}]")
        elif '/artwork' in route:
            groups['✅ 创作相关 (已迁移到app/routes/create.py和api.py)'].append(f"{route} [{methods}]")
        elif '/generate-image' in route or '/adjust-image' in route or '/upload-reference-image' in route:
            groups['❌ 3D模型功能 (需要迁移到app/routes/model3d.py)'].append(f"{route} [{methods}]")
        else:
            # 其他未分类的
            pass
    
    # 输出结果
    print("=" * 80)
    print("app.py 迁移状态检查报告")
    print("=" * 80)
    print()
    
    total = 0
    migrated = 0
    needs_migration = 0
    
    for group, routes in groups.items():
        if routes:
            count = len(routes)
            total += count
            
            if group.startswith('✅'):
                migrated += count
                print(f"{group}")
                print(f"  数量: {count} 个")
            else:
                needs_migration += count
                print(f"\n{group}")
                print(f"  数量: {count} 个")
                print(f"  详细列表:")
                for route in sorted(set(routes)):
                    print(f"    • {route}")
            print()
    
    print("=" * 80)
    print(f"总计: {total} 个路由")
    print(f"✅ 已迁移: {migrated} 个 ({migrated/total*100:.1f}%)")
    print(f"❌ 待迁移: {needs_migration} 个 ({needs_migration/total*100:.1f}%)")
    print("=" * 80)
    
    # 检查工具函数
    print("\n\n检查工具函数...")
    funcs = re.findall(r'^def ([a-z_]+)\(', app_content, re.MULTILINE)
    app_funcs = [f for f in funcs if not f.startswith('_') and f not in ['load_user']]
    
    print(f"\napp.py中定义的工具函数 ({len(app_funcs)}个):")
    for func in app_funcs:
        print(f"  • {func}()")
    
    print("\n建议:")
    print("  1. 工具函数应该迁移到 app/utils.py 或相关的 managers/")
    print("  2. 3D相关函数可以迁移到 managers/model3d_manager.py")
    print("  3. 路由处理函数应该在各自的蓝图中定义")

if __name__ == '__main__':
    analyze_routes()
