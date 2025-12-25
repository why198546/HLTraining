# 课程配置扩展指南

## 概述

所有课程配置统一管理在 `app/config/courses.py` 文件中，添加新课程只需修改此文件即可。

## 课程结构

每个课程包含以下字段：

```python
'course_key': {
    'title': '课程标题',           # 显示名称
    'desc': '课程描述',            # 详细说明
    'section': 'section_key',     # 章节标识（用于前端）
    'type': 'trial',              # 类型：trial=体验课, formal=正式课
    'order': 1                     # 排序顺序
}
```

## 添加新课程步骤

### 1. 编辑课程配置文件

打开 `app/config/courses.py`，在 `COURSES` 字典中添加新课程：

```python
COURSES = {
    # ... 现有课程 ...
    
    # 新增正式课程示例
    'advanced_character': {
        'title': '进阶课 1：高级人物设计',
        'desc': '深入学习人物细节刻画、光影效果和情绪表达。',
        'section': 'advanced_character',
        'type': 'formal',  # 正式课程
        'order': 5
    },
    'composition': {
        'title': '进阶课 2：构图与色彩',
        'desc': '掌握画面构图原理和色彩搭配技巧。',
        'section': 'composition',
        'type': 'formal',
        'order': 6
    },
}
```

### 2. 创建课程模板（如果需要）

如果新课程需要特殊的页面布局，在 `templates/` 目录创建对应模板：

```
templates/
  sunguo_lesson.html  # 通用课程模板（大部分课程用这个）
  advanced_lesson.html  # 如需特殊布局，创建新模板
```

### 3. 无需修改其他代码

✅ **二维码生成页面** - 自动显示新课程
✅ **课程导航** - 自动更新
✅ **课程页面路由** - 自动支持

## 课程类型说明

### 体验课 (trial)
- 用户扫码后获得50个token
- 成为体验学生
- 体验期1周

### 正式课 (formal)
- 用户扫码后升级为正式学生
- 每天赠送30个token
- 永久会员，不会降级

## 自动化功能

配置文件提供的辅助函数：

- `get_all_courses()` - 获取所有课程
- `get_course(key)` - 获取单个课程
- `get_courses_by_type('trial')` - 按类型获取
- `get_trial_courses()` - 获取所有体验课
- `get_formal_courses()` - 获取所有正式课
- `get_courses_for_qr()` - 获取用于二维码的课程列表
- `get_course_display_name(key)` - 获取课程显示名称

## 示例：添加一系列进阶课程

```python
COURSES = {
    # ... 现有体验课 ...
    
    # 进阶系列课程
    'advanced_1': {
        'title': '进阶课 1：高级人物设计',
        'desc': '深入学习人物细节刻画、光影效果和情绪表达。',
        'section': 'advanced_character',
        'type': 'formal',
        'order': 5
    },
    'advanced_2': {
        'title': '进阶课 2：构图与色彩',
        'desc': '掌握画面构图原理和色彩搭配技巧。',
        'section': 'composition',
        'type': 'formal',
        'order': 6
    },
    'advanced_3': {
        'title': '进阶课 3：风格与创意',
        'desc': '探索不同艺术风格，创作独特的AI艺术作品。',
        'section': 'style',
        'type': 'formal',
        'order': 7
    },
    
    # 专题课程
    'special_fantasy': {
        'title': '专题：魔幻世界',
        'desc': '创作奇幻生物、魔法场景和史诗级画面。',
        'section': 'fantasy',
        'type': 'formal',
        'order': 8
    },
}
```

## 注意事项

1. **course_key 必须唯一** - 不能与现有课程重复
2. **order 决定显示顺序** - 数字越小越靠前
3. **section 用于前端逻辑** - 建议与 key 保持一致
4. **type 影响二维码功能** - trial/formal 决定升级逻辑
5. **修改后重启应用** - 配置更改需要重启 Flask 应用

## 扩展性优势

✨ **集中管理** - 所有课程信息在一个文件
✨ **零代码添加** - 添加课程无需修改路由代码
✨ **类型安全** - 辅助函数提供类型过滤
✨ **易于维护** - 课程信息修改只需改配置
✨ **自动同步** - 所有使用课程的地方自动更新
