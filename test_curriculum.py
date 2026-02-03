#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证新课程体系的完整性和一致性
"""

import json
from app.routes.formal_lesson import (
    get_formal_curriculum_structure,
    get_default_feedback_templates
)

def test_curriculum():
    """测试课程结构的完整性"""
    print("=" * 60)
    print("正式课程体系验证")
    print("=" * 60)
    
    # 获取课程结构
    curriculum = get_formal_curriculum_structure()
    
    # 获取反馈模板
    templates = get_default_feedback_templates()
    
    # 收集所有课程ID
    all_lesson_ids = []
    
    print("\n课程模块结构：\n")
    for module in curriculum['modules']:
        print(f"模块：{module['name']} ({module['hours']}小时)")
        for lesson in module['lessons']:
            lesson_id = lesson['id']
            all_lesson_ids.append(lesson_id)
            print(f"  ✓ {lesson['id']:30} - {lesson['name']:20} ({lesson['hours']}小时)")
    
    print(f"\n总课程数：{len(all_lesson_ids)}")
    print(f"课程IDs: {all_lesson_ids}\n")
    
    # 验证每个课程都有模板
    print("=" * 60)
    print("模板完整性验证")
    print("=" * 60 + "\n")
    
    missing_templates = []
    extra_templates = []
    
    # 检查每个课程是否有模板
    for lesson_id in all_lesson_ids:
        if lesson_id not in templates:
            missing_templates.append(lesson_id)
            print(f"✗ 缺少模板: {lesson_id}")
        else:
            template = templates[lesson_id]
            print(f"✓ {lesson_id:30} - {len(template.get('aspects', []))} 个评价维度")
    
    # 检查是否有多余的模板
    for template_id in templates:
        if template_id not in all_lesson_ids:
            extra_templates.append(template_id)
            print(f"⚠ 多余的模板: {template_id}")
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    print(f"课程总数: {len(all_lesson_ids)}")
    print(f"模板总数: {len(templates)}")
    print(f"缺失模板: {len(missing_templates)}")
    print(f"多余模板: {len(extra_templates)}")
    
    if not missing_templates and not extra_templates and len(all_lesson_ids) == 15:
        print("\n✓ 验证通过！课程体系完整且一致。")
        return True
    else:
        print("\n✗ 验证失败！存在不匹配的地方。")
        return False

def test_frontend_mappings():
    """测试前端课程名称映射"""
    print("\n\n" + "=" * 60)
    print("前端课程名称映射")
    print("=" * 60 + "\n")
    
    curriculum = get_formal_curriculum_structure()
    all_lesson_ids = []
    
    for module in curriculum['modules']:
        for lesson in module['lessons']:
            all_lesson_ids.append((lesson['id'], lesson['name']))
    
    # 前端映射（应该在HTML中更新）
    frontend_mappings = {
        'formal_facial_features': '五官/比例',
        'formal_face': '表情',
        'formal_hairstyle': '发型',
        'formal_skin_color': '肤色与光影',
        'formal_body_type': '体型',
        'formal_ai_animation': '动作',
        'formal_clothing': '服装',
        'formal_location': '生活场景',
        'formal_weather': '自然场景',
        'formal_perspective': '气候与光影',
        'formal_composition1': '生活组合 (上)',
        'formal_composition2': '生活组合 (下)',
        'formal_accessories': '科幻 x 玄幻主题 (上)',
        'formal_composition3': '科幻 x 玄幻主题 (下)',
        'formal_final_work': '自由创意'
    }
    
    print("课程ID → 后端名称 → 前端映射名称\n")
    all_match = True
    for lesson_id, backend_name in all_lesson_ids:
        frontend_name = frontend_mappings.get(lesson_id, "❌ 未定义")
        match = "✓" if frontend_name != "❌ 未定义" else "✗"
        print(f"{match} {lesson_id:30} → {backend_name:20} → {frontend_name}")
        if frontend_name == "❌ 未定义":
            all_match = False
    
    if all_match:
        print("\n✓ 所有前端映射都已定义！")
    else:
        print("\n✗ 存在未定义的前端映射！")
    
    return all_match

if __name__ == '__main__':
    success1 = test_curriculum()
    success2 = test_frontend_mappings()
    
    if success1 and success2:
        print("\n\n✓✓✓ 所有验证都通过！课程体系已成功重构。✓✓✓\n")
    else:
        print("\n\n✗✗✗ 存在验证失败的项目。请检查上面的日志。✗✗✗\n")
