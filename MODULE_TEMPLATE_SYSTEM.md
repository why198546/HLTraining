"""
模块化模板系统测试文档

## 实现的功能

### 1. 前端功能
- ✅ 在模块一、二、三都添加了"修改模板"按钮
- ✅ 统一的模板编辑器界面
- ✅ 支持两种编辑模式：
  - 结构化模式（鼓励语 + 3个评价维度）
  - 纯文字模式（完整提示词）

### 2. 后端API
- ✅ 新增 GET /api/formal-lesson/module-template
  - 参数：lesson_key, module_key
  - 功能：获取指定课程的指定模块模板
  - 支持教师和学生（学生自动获取其教师的模板）

- ✅ 新增 POST /api/formal-lesson/module-template
  - 参数：lesson_key, module_key, encouragement, aspects, mode, raw_prompt
  - 功能：保存指定课程的指定模块模板
  - 仅教师可用

### 3. 数据库
- ✅ User模型新增字段：module_templates (JSON)
  - 存储结构：{lesson_key: {module_key: {...}}}
  - 例如：{'formal_body_type': {'module1': {...}, 'module2': {...}}}

### 4. 默认模板配置
```python
{
    'module1': {
        'name': '模块一：图片生成',
        'mode': 'text',
        'raw_prompt': '根据描述生成图片的提示词...'
    },
    'module2': {
        'name': '模块二：图像融合',
        'mode': 'text',
        'raw_prompt': '图像融合的提示词...'
    },
    'module3': {
        'name': '模块三：AI点评',
        'mode': 'structured',
        'encouragement': '很棒的作品！',
        'aspects': ['线条流畅度', '色彩运用', '创意表现']
    }
}
```

## 使用方法

### 教师端
1. 进入任意正式课程页面（如 formal_body_type）
2. 在模块一/二/三的标题栏看到"修改模板"按钮
3. 点击按钮打开编辑器
4. 切换编辑模式（结构化/纯文字）
5. 编辑提示词内容
6. 点击"保存修改"

### 学生端
- 学生看不到"修改模板"按钮（按钮只对教师可见）
- 学生使用的是其教师设置的模板
- 如果教师未设置，使用系统默认模板

## 调用示例

### 前端调用
```javascript
// 打开模块一的模板编辑器
openModuleTemplateEditor('module1');

// 打开模块二的模板编辑器
openModuleTemplateEditor('module2');

// 打开模块三的模板编辑器
openModuleTemplateEditor('module3');
```

### 后端集成
其他模块可以通过导入函数来获取模板：
```python
from app.routes.module_template_api import get_default_module_templates

# 获取所有默认模板
templates = get_default_module_templates()

# 获取特定模块的模板
module1_template = templates['module1']
```

## 文件清单
1. `/templates/sunguo_formal_lesson.html` - 前端界面和JavaScript
2. `/app/routes/module_template_api.py` - 模块级模板API（新文件）
3. `/auth/models.py` - User模型（添加module_templates字段）
4. `/app/__init__.py` - 注册新的Blueprint
5. `/migrations/add_module_templates_column.py` - 数据库迁移脚本

## 优势
1. **模块化设计** - 每个模块的提示词可以独立配置
2. **易于扩展** - 新增模块只需添加默认模板配置
3. **向后兼容** - 原有的课程级模板系统（module3）继续工作
4. **灵活性高** - 支持结构化和纯文字两种编辑模式
5. **权限清晰** - 教师编辑，学生使用
6. **可复用** - 其他页面可以调用相同的API获取模板

## 测试建议
1. 以教师身份登录
2. 进入 `/sunguo-formal/formal_body_type` 页面
3. 测试修改模块一的提示词（纯文字模式）
4. 测试修改模块二的提示词（纯文字模式）
5. 测试修改模块三的提示词（结构化或纯文字模式）
6. 切换到学生账号，验证学生能看到教师设置的模板内容
