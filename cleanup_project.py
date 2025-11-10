#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本 - 清理无用的测试文件、报告文档和临时文件
"""

import os
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 定义要清理的内容
CLEANUP_PATTERNS = {
    "测试文件": [
        "test_*.py",
        "debug_*.py",
        "check_*.py",
        "comprehensive_dialogue_test.py",
        "final_privacy_test.py",
        "quick_test.py",
        "simple_test_privacy.py",
        "verify_*.py",
        "show_translation_result.py",
        "get_final_prompt.py",
    ],
    
    "测试HTML文件": [
        "test_*.html",
        "debug_*.html",
        "simple_test.html",
        "feature_verification.html",
        "email_template_preview.html",
    ],
    
    "报告文档": [
        "*_REPORT.md",
        "*_GUIDE.md",
        "*_SUMMARY.md",
        "*_IMPLEMENTATION*.md",
        "EXPERT_MODE_FEATURE.md",
        "PADDING_MODES_FEATURE.md",
        "PADDING_MODES_USER_GUIDE.md",
        "QUICK_GUIDE_16_9.md",
        "IMAGE_16_9_CONVERSION.md",
        "VIDEO_PADDING_UPDATE.md",
        "PORT_CONFIG_NOTICE.md",
        "RELEASE_v1.0.md",
    ],
    
    "数据库迁移脚本": [
        "add_role_migration.py",
        "add_user_details_migration.py",
        "migrate_json_to_db.py",
        "recreate_db.py",
    ],
    
    "备份文件": [
        "*.backup",
        "gallery_data.json.backup",
        "artwork_versions.json",
    ],
    
    "旧数据库文件": [
        "user_artworks.db",
        "artworks.db",
    ],
    
    "其他临时文件": [
        "make_public.py",
        "create_test_user.py",
        "fix_missing_files.py",
        "setup_ai_generation.py",
        "flask_app.pid",
        "build_windows.sh",
        "start_project.sh",
        "HLTraining.spec",
    ],
    
    "日志文件": [
        "app.log",
        "flask.log",
        # "flask_app.log",  # 保留当前日志
    ],
}

def find_files_to_cleanup():
    """查找需要清理的文件"""
    files_to_cleanup = {}
    
    for category, patterns in CLEANUP_PATTERNS.items():
        matched_files = []
        for pattern in patterns:
            # 使用glob匹配文件
            matches = list(PROJECT_ROOT.glob(pattern))
            matched_files.extend(matches)
        
        if matched_files:
            files_to_cleanup[category] = matched_files
    
    return files_to_cleanup

def display_cleanup_list(files_to_cleanup):
    """显示要清理的文件列表"""
    total_files = 0
    total_size = 0
    
    print("\n" + "="*80)
    print("📋 待清理内容列表")
    print("="*80)
    
    for category, files in files_to_cleanup.items():
        if not files:
            continue
            
        print(f"\n📁 {category} ({len(files)} 个文件):")
        category_size = 0
        
        for file_path in sorted(files):
            if file_path.is_file():
                size = file_path.stat().st_size
                category_size += size
                size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/1024/1024:.1f}MB"
                print(f"   - {file_path.name} ({size_str})")
            elif file_path.is_dir():
                print(f"   - {file_path.name}/ (目录)")
        
        if category_size > 0:
            total_size += category_size
            size_str = f"{category_size/1024:.1f}KB" if category_size < 1024*1024 else f"{category_size/1024/1024:.1f}MB"
            print(f"   小计: {size_str}")
        
        total_files += len(files)
    
    print("\n" + "="*80)
    print(f"📊 总计: {total_files} 个文件")
    if total_size > 0:
        size_str = f"{total_size/1024:.1f}KB" if total_size < 1024*1024 else f"{total_size/1024/1024:.1f}MB"
        print(f"💾 总大小: {size_str}")
    print("="*80 + "\n")

def cleanup_files(files_to_cleanup, confirm=True):
    """执行清理操作"""
    if not files_to_cleanup:
        print("✅ 没有需要清理的文件")
        return 0
    
    if confirm:
        response = input("⚠️  确认删除以上文件? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ 取消清理操作")
            return 0
    
    deleted_count = 0
    failed_count = 0
    
    print("\n🗑️  开始清理...")
    
    for category, files in files_to_cleanup.items():
        print(f"\n清理 {category}...")
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"  ✓ 删除文件: {file_path.name}")
                    deleted_count += 1
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"  ✓ 删除目录: {file_path.name}/")
                    deleted_count += 1
            except Exception as e:
                print(f"  ✗ 删除失败 {file_path.name}: {str(e)}")
                failed_count += 1
    
    print("\n" + "="*80)
    print(f"✅ 清理完成: 成功删除 {deleted_count} 个文件/目录")
    if failed_count > 0:
        print(f"⚠️  失败: {failed_count} 个")
    print("="*80 + "\n")
    
    return deleted_count

def cleanup_pycache():
    """清理__pycache__目录"""
    print("\n🗑️  清理 __pycache__ 目录...")
    count = 0
    
    for pycache_dir in PROJECT_ROOT.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            print(f"  ✓ 删除: {pycache_dir.relative_to(PROJECT_ROOT)}")
            count += 1
        except Exception as e:
            print(f"  ✗ 删除失败: {str(e)}")
    
    if count > 0:
        print(f"✅ 删除了 {count} 个 __pycache__ 目录")
    else:
        print("✅ 没有找到 __pycache__ 目录")

def cleanup_ds_store():
    """清理.DS_Store文件"""
    print("\n🗑️  清理 .DS_Store 文件...")
    count = 0
    
    for ds_file in PROJECT_ROOT.rglob(".DS_Store"):
        try:
            ds_file.unlink()
            print(f"  ✓ 删除: {ds_file.relative_to(PROJECT_ROOT)}")
            count += 1
        except Exception as e:
            print(f"  ✗ 删除失败: {str(e)}")
    
    if count > 0:
        print(f"✅ 删除了 {count} 个 .DS_Store 文件")
    else:
        print("✅ 没有找到 .DS_Store 文件")

def main():
    """主函数"""
    import sys
    
    print("\n🧹 项目清理工具")
    print("="*80)
    
    # 查找要清理的文件
    files_to_cleanup = find_files_to_cleanup()
    
    # 显示清理列表
    display_cleanup_list(files_to_cleanup)
    
    # 检查是否为自动模式
    auto_mode = '--auto' in sys.argv or '-y' in sys.argv
    
    # 执行清理
    if files_to_cleanup:
        deleted = cleanup_files(files_to_cleanup, confirm=not auto_mode)
    
    # 清理其他内容
    if auto_mode or input("\n清理 __pycache__ 目录? (yes/no): ").lower() == 'yes':
        cleanup_pycache()
    
    if auto_mode or input("\n清理 .DS_Store 文件? (yes/no): ").lower() == 'yes':
        cleanup_ds_store()
    
    print("\n🎉 清理完成！")

if __name__ == '__main__':
    main()
