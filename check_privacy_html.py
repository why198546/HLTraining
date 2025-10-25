#!/usr/bin/env python3
"""
检查隐私设置HTML结构
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from forms import PrivacySettingsForm
from flask import render_template_string

def check_privacy_html():
    """检查隐私设置HTML结构"""
    print("🔍 检查隐私设置HTML结构...")
    print("=" * 50)
    
    with app.app_context():
        # 创建表单实例
        privacy_form = PrivacySettingsForm()
        
        print("📋 表单字段信息:")
        for field_name in ['show_in_gallery', 'show_age', 'allow_parent_reports']:
            field = getattr(privacy_form, field_name)
            print(f"  {field_name}:")
            print(f"    ID: {field.id}")
            print(f"    名称: {field.name}")
            print(f"    标签: {field.label.text}")
            print(f"    默认值: {field.default}")
            print()
        
        # 生成HTML片段
        html_template = """
        <div class="privacy-item">
            <div class="privacy-info">
                <h4>作品展示</h4>
                <p>允许其他人在作品展示页面看到我的作品</p>
            </div>
            <div class="privacy-toggle">
                {{ privacy_form.show_in_gallery(style="display: none;") }}
                <label for="{{ privacy_form.show_in_gallery.id }}" class="toggle-switch">
                    <span class="toggle-slider"></span>
                </label>
            </div>
        </div>
        """
        
        try:
            rendered_html = render_template_string(html_template, privacy_form=privacy_form)
            print("🖥️  生成的HTML:")
            print(rendered_html)
            
            # 检查关键元素
            if 'input' in rendered_html and 'name="show_in_gallery"' in rendered_html:
                print("✅ 输入元素正确生成")
            else:
                print("❌ 输入元素生成失败")
                
            if 'label' in rendered_html and 'for=' in rendered_html:
                print("✅ 标签元素正确生成")
            else:
                print("❌ 标签元素生成失败")
                
            if 'toggle-switch' in rendered_html:
                print("✅ 切换开关类正确添加")
            else:
                print("❌ 切换开关类缺失")
            
        except Exception as e:
            print(f"❌ HTML生成失败: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    success = check_privacy_html()
    sys.exit(0 if success else 1)