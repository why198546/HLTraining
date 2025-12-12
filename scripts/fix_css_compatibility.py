#!/usr/bin/env python3
"""
CSS兼容性修复脚本
自动为所有 backdrop-filter 添加 -webkit- 前缀以支持 Safari
"""

import re
import os

def fix_backdrop_filter(css_file_path):
    """修复 backdrop-filter 兼容性问题"""
    
    print(f"📝 正在处理: {css_file_path}")
    
    # 读取CSS文件
    with open(css_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = css_file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已备份到: {backup_path}")
    
    # 统计修复数量
    fixes_count = 0
    
    # 正则匹配: 找到没有 -webkit- 前缀的 backdrop-filter
    # 匹配模式: 行首空白 + backdrop-filter: 值; (但前面没有 -webkit-backdrop-filter)
    pattern = r'([ \t]*)(backdrop-filter:\s*[^;]+;)'
    
    def replacer(match):
        nonlocal fixes_count
        indent = match.group(1)
        backdrop_line = match.group(2)
        
        # 检查上一行是否已有 -webkit-backdrop-filter
        # 通过检查匹配前的内容
        before_match = content[:match.start()]
        lines_before = before_match.split('\n')
        
        if len(lines_before) > 0:
            prev_line = lines_before[-1].strip()
            # 如果上一行已经有 -webkit-backdrop-filter，跳过
            if '-webkit-backdrop-filter' in prev_line:
                return match.group(0)
        
        # 添加 -webkit- 前缀版本
        webkit_line = backdrop_line.replace('backdrop-filter:', '-webkit-backdrop-filter:')
        fixes_count += 1
        
        # 返回: -webkit版本 + 换行 + 原版本
        return f"{indent}{webkit_line}\n{indent}{backdrop_line}"
    
    # 执行替换
    new_content = re.sub(pattern, replacer, content)
    
    # 写回文件
    with open(css_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✨ 完成！共修复 {fixes_count} 处 backdrop-filter")
    return fixes_count

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # CSS文件路径
    css_file = os.path.join(project_root, 'static', 'css', 'style.css')
    
    if not os.path.exists(css_file):
        print(f"❌ 错误: CSS文件不存在: {css_file}")
        return
    
    print("🎨 CSS兼容性修复工具")
    print("=" * 50)
    
    total_fixes = fix_backdrop_filter(css_file)
    
    print("=" * 50)
    print(f"🎉 修复完成！总计修复 {total_fixes} 处")
    print(f"💾 原文件已备份为: {css_file}.backup")
    print("\n📋 修复内容:")
    print("   - 为所有 backdrop-filter 添加 -webkit-backdrop-filter")
    print("   - 支持 Safari 9+ 和 Safari on iOS 9+")

if __name__ == '__main__':
    main()
