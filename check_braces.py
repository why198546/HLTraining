#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查JS代码的括号匹配"""

with open('templates/auth/profile.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_script = False
brace_count = 0
script_start = 0

for i, line in enumerate(lines, 1):
    if '<script>' in line:
        in_script = True
        script_start = i
        print(f"行 {i}: <script> 标签开始")
    
    if in_script:
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += (open_braces - close_braces)
        
        if open_braces > 0 or close_braces > 0:
            print(f"行 {i}: 开={open_braces}, 闭={close_braces}, 累计={brace_count}")
            if brace_count < 0:
                print(f"  ⚠️ 警告: 闭括号过多！")
                print(f"  内容: {line.strip()[:100]}")
    
    if '</script>' in line:
        print(f"行 {i}: </script> 标签结束，最终括号计数: {brace_count}")
        if brace_count != 0:
            print(f"  ❌ 错误: 括号不匹配！")
        in_script = False
        brace_count = 0
