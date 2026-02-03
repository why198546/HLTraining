# 新课程体系快速参考

## 课程ID速查表

| 模块 | 课程ID | 中文名称 | 小时 | 反馈维度 |
|-----|-------|--------|------|--------|
| 一、人像 | formal_facial_features | 五官/比例 | 1h | 五官位置准确度、比例结构科学性、个性特征表现 |
| | formal_face | 表情 | 1h | 脸型比例准确性、脸部轮廓立体感、脸型特征个性体现 |
| | formal_hairstyle | 发型 | 1h | 线条精准度与蓬松感、层次感与空间表现、风格特征表现力 |
| | formal_skin_color | 肤色与光影 | 1h | 色彩冷暖搭配合理性、明暗层次与光影表现、肤色质感逼真度 |
| 二、体态 | formal_body_type | 体型 | 1h | 人体比例结构科学性、肢体姿态自然度、身体动态灵活性 |
| | formal_ai_animation | 动作 | 1h | 动作连贯性与自然度、节奏感与表现力、视觉吸引力 |
| | formal_clothing | 服装 | 1h | 服装褶皱与质感表现、色彩搭配审美水准、穿着效果逼真度 |
| 三、场景 | formal_location | 生活场景 | 1h | 环境细节丰富度与准确性、场景特征识别度、环境与人物融合度 |
| | formal_weather | 自然场景 | 1h | 气象特征视觉表现、光线变化对画面影响、氛围渲染感染力 |
| | formal_perspective | 气候与光影 | 1h | 天气氛围营造、光影变化表现力、整体意境传达 |
| 四、综合创作 | formal_composition1 | 生活组合 (上) | 1h | 场景布局合理性、前-中-后景层次、人物与环境互动 |
| | formal_composition2 | 生活组合 (下) | 1h | 多个人物关系表现、故事叙述性完整度、画面节奏感染力 |
| | formal_accessories | 科幻 x 玄幻主题 (上) | 1h | 科幻元素创意融合、奇幻氛围营造、想象力大胆表现 |
| | formal_composition3 | 科幻 x 玄幻主题 (下) | 1h | 奇幻元素创意融合、视觉冲击力表现、想象力大胆发挥 |
| | formal_final_work | 自由创意 | 1h | 创意主题独特表达、综合技法整体运用、个人艺术风格形成 |

## 关键代码位置

### 后端

**课程数据结构定义**
- 文件: `app/routes/formal_lesson.py`
- 函数: `get_formal_curriculum_structure()` (L654-810)
- 作用: 定义4个模块、15个课程的完整层级结构

**反馈模板定义**
- 文件: `app/routes/formal_lesson.py`
- 函数: `get_default_feedback_templates()` (L815-885)
- 作用: 为每个课程定义评价维度和鼓励语言

**课程API端点**
- 文件: `app/routes/formal_lesson.py`
- 路由: `/api/formal-lesson/curriculum` (L743-749)
- 方法: GET
- 返回: 完整课程体系JSON

### 前端

**课程名称映射**
- 文件: `templates/sunguo_formal_lesson.html`
- 函数: `getLessonName()` (L2133-2150)
- 作用: 将课程ID转换为显示名称

**提示词配置**
- 文件: `templates/sunguo_formal_lesson.html`
- 对象: `lessonDefaultPrompts` (L953-968)
- 对象: `lessonCompositionHints` (L971-987)
- 作用: 为每个课程提供默认提示词

**特征选项配置**
- 文件: `templates/sunguo_formal_lesson.html`
- 对象: `lessonFeatures` (L990+)
- 作用: 为每个课程定义可选择的特征

## 添加新课程的步骤

如果需要在未来添加新课程，请按以下步骤:

### 1. 后端更新

在 `get_formal_curriculum_structure()` 中添加:
```python
{
    'id': 'formal_new_lesson',
    'name': '新课程名称',
    'description': '课程描述',
    'hours': 1,
    'order': X  # 该模块内的顺序
}
```

在 `get_default_feedback_templates()` 中添加:
```python
'formal_new_lesson': {
    'aspects': ['维度1', '维度2', '维度3'],
    'encouragement': '鼓励语言'
}
```

在 `lesson_composition_hints` 中添加:
```python
'formal_new_lesson': '构图提示...'
```

### 2. 前端更新

在 `getLessonName()` 中添加:
```javascript
'formal_new_lesson': '新课程名称'
```

在 `lessonDefaultPrompts` 中添加:
```javascript
'formal_new_lesson': '默认提示词...'
```

在 `lessonCompositionHints` 中添加:
```javascript
'formal_new_lesson': '构图提示...'
```

在 `lessonFeatures` 中添加:
```javascript
'formal_new_lesson': [
    { label: '特征名', feature: 'feature_name', options: [...] }
]
```

### 3. 验证

运行验证脚本:
```bash
python test_curriculum.py
```

## 常见问题解答

### Q: 为什么课程ID和显示名称不同?
A: 课程ID是内部标识符，用于数据库和API。显示名称是对用户友好的中文名称。这样设计可以在不影响数据的情况下更改显示文本。

### Q: 如何修改某个课程的反馈模板?
A: 
1. 进入正式课程
2. 点击该课程的"修改模板"按钮
3. 编辑评价维度和鼓励语言
4. 点击保存

### Q: 前端特征配置和提示词有什么关系?
A: 特征配置用于生成UI选项让用户选择，这些选择会被组合成提示词。提示词则直接发送给AI模型。

### Q: 如果课程显示不正常怎么办?
A: 检查以下几点:
1. 课程ID是否在 `get_formal_curriculum_structure()` 中定义
2. 课程ID是否在 `get_default_feedback_templates()` 中有模板
3. 课程ID是否在 `getLessonName()` 中有映射
4. 前端浏览器控制台是否有错误信息

### Q: 新的课程体系是否向后兼容?
A: 基本兼容。所有旧的课程ID仍然保留，数据库中的现有数据不会丢失。只是显示结构和组织方式改变了。

## 版本信息

- **版本**: 2.0
- **发布日期**: 2024年
- **主要变更**: 4模块15课程的新层级架构
- **验证状态**: ✅ 通过
- **兼容性**: 完全向后兼容

## 联系方式

如有问题，请查看:
- 验证脚本: `test_curriculum.py`
- 完整报告: `CURRICULUM_REDESIGN_REPORT.md`
- 代码注释: `app/routes/formal_lesson.py`
