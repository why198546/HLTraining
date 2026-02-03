# 课程级AI点评模板系统

## 概述

本系统提供了一个完整的课程级AI点评模板管理功能，允许教师为每个课程单独定制AI点评的评估标准和鼓励语。教师可以在课程页面的模块三（AI点评作品）直接修改模板，所有改动会立即应用到后续的AI点评中。

## 核心功能

### 1. 模块三快速编辑按钮
- **位置**：课程页面模块三的头部
- **按钮样式**：绿色渐变按钮，显示为"修改模板"
- **交互**：点击按钮打开课程模板编辑模态框
- **权限**：教师专属功能

### 2. 课程级模板编辑模态框
- **标题**：动态显示课程名称（如"编辑 发型设计 的AI点评模板"）
- **编辑字段**：
  - 🎯 **鼓励语**：AI在点评开头时使用的激励语言
  - 📋 **评价维度1、2、3**：用于引导AI从三个角度评价学生作品

### 3. 层级化模板系统
```
默认模板
    ↓
教师全局模板（teacher.feedback_templates）
    ↓
课程级模板（特定课程的自定义模板）
    ↓
学生点评结果
```

**模板优先级**：
1. 教师为该课程设置的课程级模板（最高优先级）
2. 教师的全局模板（作为备选）
3. 系统默认模板（后备方案）

## 技术架构

### 前端（HTML/JavaScript）

**关键文件**：`templates/sunguo_formal_lesson.html`

#### 新增函数

```javascript
// 打开课程级模板编辑器
async function openLessonTemplateEditor()

// 获取课程名称（用于模态框标题）
function getLessonName()

// 保存课程级模板
async function saveLessonTemplate()
```

#### 模态框
- ID：`lessonTemplateModal`
- 触发器：模块三头部的"修改模板"按钮
- 表单字段：
  - `lessonEncouragement`：鼓励语输入框
  - `lessonAspect1/2/3`：评价维度输入框

### 后端（Python Flask）

**关键文件**：`app/routes/formal_lesson.py`

#### 新增API端点

##### 1. GET `/api/formal-lesson/lesson-template`
获取单个课程的模板

**参数**：
- `lesson_key`：课程标识符（必需）

**响应**：
```json
{
  "success": true,
  "template": {
    "encouragement": "你对发型细节的观察很敏锐！",
    "aspects": [
      "线条精准度与蓬松感",
      "层次感与空间表现", 
      "风格特征的表现力"
    ]
  }
}
```

**逻辑**：
- 如果用户是学生：查询其所属教师的模板
- 如果教师有该课程的自定义模板：返回该模板
- 否则返回该课程的默认模板

##### 2. POST `/api/formal-lesson/lesson-template`
保存课程级模板（仅教师可用）

**参数**：
```json
{
  "lesson_key": "formal_hairstyle",
  "encouragement": "你对发型细节的观察很敏锐！",
  "aspects": ["维度1", "维度2", "维度3"]
}
```

**验证**：
- 只有教师可以保存模板
- 所有字段必填且非空
- 必须恰好有3个评价维度

**响应**：成功时返回 `{"success": true}`

#### 更新的API端点

##### POST `/api/formal-lesson/artwork-feedback`（改进版本）
AI点评作品时自动使用正确的模板

**改进内容**：
- 自动检测当前用户身份
- 如果是学生，自动查找其教师的模板
- 使用教师的课程级模板（如果存在）
- 回退到默认模板

**模板选择流程**：
```
1. 确定教师身份
   ├─ 如果当前用户是教师：使用其模板
   └─ 如果当前用户是学生：查找所属教师

2. 加载教师的反馈模板
   ├─ 如果教师有自定义模板：使用
   └─ 否则使用系统默认

3. 获取特定课程的模板
   ├─ 如果存在课程级模板：使用
   └─ 否则使用默认值
```

## 优化的模板标准

### 评估维度改进

所有课程的模板都基于以下三个维度：

| 维度 | 含义 | 示例 |
|------|------|------|
| **技法维度** | 基础技能掌握程度 | 线条精准度、比例准确性 |
| **审美维度** | 艺术表现力和美感 | 立体感、和谐度、质感 |
| **创意维度** | 创新性和个性表达 | 风格特征、个性体现 |

### 课程模板示例

#### 发型设计 (formal_hairstyle)
```javascript
{
  'aspects': [
    '线条精准度与蓬松感',      // 技法维度
    '层次感与空间表现',        // 审美维度  
    '风格特征的表现力'         // 创意维度
  ],
  'encouragement': '你对发型细节的观察很敏锐！'
}
```

#### 五官刻画 (formal_facial_features)
```javascript
{
  'aspects': [
    '五官位置关系的准确性',    // 技法维度
    '眼睛神韵与情感表达',      // 审美维度
    '五官整体协调度'          // 创意维度
  ],
  'encouragement': '你捕捉的表情很富有生命力！'
}
```

## 使用流程

### 教师操作流程

1. **进入课程页面**
   - 教师访问某个正式课程页面
   
2. **发现修改按钮**
   - 在模块三头部看到"修改模板"按钮
   
3. **打开编辑器**
   - 点击按钮打开课程模板编辑模态框
   
4. **编辑模板内容**
   - 修改鼓励语
   - 修改三个评价维度
   
5. **保存修改**
   - 点击"保存修改"按钮
   - 系统确认保存成功
   
6. **即时应用**
   - 新的模板立即应用到该课程的AI点评功能
   - 之后学生上传作品时，将使用新的模板

### 学生体验

1. **上传作品**
   - 学生在模块三上传作品
   
2. **自动使用教师模板**
   - 系统自动查找学生所属教师的模板
   - 如果教师设置了该课程的模板，则使用该模板
   
3. **收到专业评价**
   - 获得基于教师自定义标准的AI点评
   - 评价内容更加贴切该课程的教学目标

## 数据存储

### 数据库结构

在 `users` 表中：
- 字段：`feedback_templates` (JSON)
- 存储方式：整个模板集合作为JSON对象

```json
{
  "formal_hairstyle": {
    "encouragement": "...",
    "aspects": ["...", "...", "..."]
  },
  "formal_face": {
    "encouragement": "...",
    "aspects": ["...", "...", "..."]
  },
  // ... 其他课程
}
```

## API交互示例

### 获取模板

```javascript
// 前端代码
const response = await fetch('/api/formal-lesson/lesson-template?lesson_key=formal_hairstyle');
const data = await response.json();
console.log(data.template);
```

### 保存模板

```javascript
// 前端代码
const response = await fetch('/api/formal-lesson/lesson-template', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    lesson_key: 'formal_hairstyle',
    encouragement: '你对发型很有独特的见解！',
    aspects: ['线条表现', '整体协调', '创意表达']
  })
});
const data = await response.json();
if (data.success) alert('保存成功！');
```

## 错误处理

系统包含以下错误处理机制：

| 错误场景 | 处理方式 |
|---------|---------|
| 加载模板失败 | 显示用户友好的错误信息，不中断工作流 |
| 网络错误 | 提示用户重试或检查网络连接 |
| 字段验证失败 | 提示用户填写所有必需字段 |
| 权限不足 | 隐藏修改按钮或返回403错误 |
| Vision分析失败 | 回退到默认点评模板 |

## 日志记录

### 关键日志信息

```
✅ 使用教师 {username} 的自定义模板
ℹ️ 使用默认评审模板
🔍 开始Vision分析 - 维度: {aspects}
✅ Vision分析成功
⚠️ Vision分析失败，使用默认模板
```

### 调试建议

1. 在浏览器控制台检查API调用
2. 在后端日志中查看模板加载过程
3. 验证教师的 `feedback_templates` 字段是否正确保存
4. 检查学生与教师的关联是否正确

## 安全考虑

1. **权限验证**
   - 只有教师可以编辑模板
   - 学生只能查看其教师的模板

2. **数据验证**
   - 所有输入字段都经过验证
   - 禁止SQL注入和XSS攻击

3. **访问控制**
   - `@login_required` 装饰器保护所有API端点
   - 角色检查确保权限

## 扩展建议

1. **模板版本管理**
   - 保存模板修改历史
   - 支持恢复到之前的版本

2. **模板共享**
   - 教师间共享高质量模板
   - 建立模板库

3. **模板预设**
   - 为不同学龄级别提供预设模板
   - 支持模板导入/导出

4. **统计分析**
   - 分析哪些评价维度最有效
   - 跟踪模板修改的频率和影响

## 相关文件

- 前端：[templates/sunguo_formal_lesson.html](../templates/sunguo_formal_lesson.html)
- 后端：[app/routes/formal_lesson.py](../app/routes/formal_lesson.py)
- 数据模型：[auth/models.py](../auth/models.py)

## 更新日志

### v1.0（当前版本）
- ✅ 实现课程级模板编辑功能
- ✅ 创建课程模板编辑模态框
- ✅ 添加后端API端点
- ✅ 优化默认模板标准
- ✅ 实现模板层级系统
- ✅ 自动应用到AI点评流程
