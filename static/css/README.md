# CSS 文件结构说明

## 核心样式文件

### modules/core.css
**用途**: 全局通用组件样式
- 导航栏、页脚等全局UI组件
- 通用按钮样式（voice-input-btn, ai-optimize-btn, camera-input-btn）
- 表单元素通用样式
- 通用动画和过渡效果

**使用页面**: 几乎所有页面都会加载此文件

### modules/page-classroom.css  
**用途**: 松果课堂(sunguo-class)专用样式
- 课程页面布局
- 作品展示卡片
- 图片查看器
- **相机拍照模态框（camera-modal及相关）**

**使用页面**: 
- templates/sunguo_lesson.html
- 所有松果课堂相关页面

### modules/page-create.css
**用途**: AI画布创作页面专用样式
- 创作表单
- 参数调整面板
- 实时预览区域

**使用页面**: templates/index.html (AI画布页面)

## 功能模块样式

### modules/image-viewer.css
**用途**: 图片查看器组件
- 全屏图片浏览
- 缩略图导航
- 左右切换按钮

**使用页面**: 需要图片浏览功能的页面

### gpu-acceleration.css
**用途**: GPU加速优化
- 使用transform和will-change优化动画性能
- 减少页面重绘和回流

### toast.css
**用途**: Toast提示组件
- 全局消息提示样式

## 重要规则

### 1. 样式优先级
当多个CSS文件都定义了同一个类时，按HTML中的加载顺序，**后加载的会覆盖先加载的**。

例如 sunguo_lesson.html 的加载顺序：
```html
<link rel="stylesheet" href="css/modules/core.css">           <!-- 1. 全局样式 -->
<link rel="stylesheet" href="css/modules/page-classroom.css"> <!-- 2. 页面专用 -->
<link rel="stylesheet" href="css/modules/image-viewer.css">   <!-- 3. 功能组件 -->
```

### 2. 修改原则

#### 修改通用样式
- 如果要修改**所有页面**都用的组件（如按钮、导航栏）→ 修改 `core.css`
- 使用场景：修改全站按钮颜色、字体、间距等

#### 修改页面专用样式  
- 如果只在**特定页面**使用的样式 → 修改对应的 `page-*.css`
- 使用场景：松果课堂的布局、作品卡片样式 → `page-classroom.css`

#### 添加新功能样式
- 独立功能组件 → 创建新的CSS文件
- 特定页面功能 → 添加到对应的 `page-*.css`

### 3. 相机功能样式位置

**相机拍照功能的所有样式都在 `page-classroom.css` 中**，包括：
- `.camera-modal` - 模态框容器
- `.camera-modal-overlay` - 遮罩层
- `.camera-modal-content` - 模态框内容
- `.camera-tabs` - 标签页容器
- `.camera-tab-btn` - 标签页按钮
- `.camera-tab-content` - 标签页内容
- `.camera-preview-area` - 摄像头预览区
- `.camera-controls` - 控制按钮区
- `.camera-btn-*` - 各种按钮样式
- `.upload-area` - 上传区域
- 等等...

**为什么放在这里**？因为相机功能只在松果课堂页面使用，属于页面专用功能。

### 4. 避免重复定义

❌ **错误做法**：
```css
/* core.css */
.camera-modal { ... }

/* page-classroom.css */  
.camera-modal { ... }  /* 重复定义！会覆盖core.css */
```

✅ **正确做法**：
- 相机功能只在松果课堂使用 → 只在 `page-classroom.css` 定义
- 多个页面都要用的组件 → 只在 `core.css` 定义

### 5. 使用 !important 的时机

只在以下情况使用：
- 样式被其他更高优先级的CSS覆盖，且无法通过选择器优先级解决
- 需要强制覆盖第三方库的样式

**不要滥用 !important**，这会让后续维护变困难。

## 已归档文件

### archived/static/css/modules/classroom.css
- **状态**: 已废弃，不再使用
- **原因**: 被拆分到 core.css 和 page-classroom.css
- **迁移日期**: 2025-12-26

## 常见问题

### Q: 样式没生效怎么办？
1. 检查浏览器是否缓存了旧CSS → 强制刷新 (Cmd+Shift+R)
2. 检查是否修改了正确的CSS文件
3. 检查HTML是否加载了该CSS文件
4. 检查选择器优先级是否被覆盖

### Q: 如何确定应该修改哪个CSS文件？
1. 查看页面HTML的 `<link>` 标签，确认加载了哪些CSS
2. 如果是页面特有功能 → 修改 `page-*.css`
3. 如果是全站通用组件 → 修改 `core.css`

### Q: 新增功能应该放在哪个CSS文件？
- 全站通用 → `core.css`
- 特定页面专用 → 对应的 `page-*.css`
- 独立复杂组件 → 新建独立CSS文件

## 最后更新
- 日期: 2025-12-26
- 更新人: GitHub Copilot
- 更新内容: 整理CSS文件结构，归档废弃文件，添加使用说明
