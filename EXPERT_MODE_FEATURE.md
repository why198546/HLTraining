# Expert模式功能实现

## 功能概述

为AI创作工坊添加了"Expert模式"功能，允许高级用户直接使用原始prompt进行图像生成，不添加任何系统预设的提示词增强。

## 功能特点

### 1. 灵活的Prompt控制
- **普通模式**：系统会自动添加风格、色彩偏好和儿童友好的提示词增强
- **Expert模式**：完全使用用户输入的原始prompt，不添加任何额外内容

### 2. 适用场景
Expert模式支持所有图像生成场景：
- 纯文字生成图片
- 图片+文字混合生成
- 纯图片上色
- 图片调整和修改

### 3. UI集成
- 在生成选项区域添加了直观的复选框开关
- 包含简洁的说明文字，帮助用户理解功能
- 开关状态会应用到所有生成操作（生成新图片、调整图片）

## 技术实现

### 后端修改 (Python)

#### 1. `api/nano_banana.py`
修改了以下方法，添加 `expert_mode` 参数：
- `colorize_sketch()` - 图片上色
- `generate_image_from_text()` - 文字生成图片
- `generate_image_from_sketch()` - 图片生成
- `generate_image_from_sketch_and_text()` - 混合生成
- `adjust_image()` - 图片调整

当 `expert_mode=True` 时，这些方法会跳过所有系统提示词的构建，直接使用用户输入的原始prompt。

#### 2. `app.py`
修改了路由处理函数：
- `/generate-image` - 接收 `expert_mode` 参数并传递给API
- `/adjust-image` - 接收 `expert_mode` 参数并传递给API

### 前端修改 (HTML/JavaScript/CSS)

#### 1. `templates/create.html`
在生成选项区域添加了Expert模式复选框：
```html
<div class="option-group">
    <label style="display: flex; align-items: center; gap: 8px;">
        <input type="checkbox" id="expert-mode" style="width: auto; margin: 0;">
        <span>⚡ Expert模式</span>
    </label>
    <small>启用后将直接使用你的原始prompt，不添加任何系统提示</small>
</div>
```

#### 2. `static/js/create.js`
修改了JavaScript函数：
- `generateImage()` - 获取expert模式状态并包含在FormData中
- `applyAdjustment()` - 获取expert模式状态并包含在FormData中

#### 3. `static/css/style.css`
添加了样式规则：
- Expert模式选项占据整行，提供更好的视觉效果
- 修复了已存在的CSS语法错误

## 使用方法

### 普通用户
保持Expert模式复选框未选中，系统会自动优化prompt以获得最佳效果。

### 高级用户
1. 勾选"⚡ Expert模式"复选框
2. 在prompt输入框中输入精确的提示词
3. 系统将完全按照你的提示词生成图片，不做任何修改或增强

## 示例对比

### 普通模式
用户输入：`一只猫`

实际发送给AI的prompt：
```
创建一幅适合10-14岁儿童的插画：一只猫

风格要求：可爱卡通风格，圆润的线条，柔和的造型，Q版比例
色彩要求：色彩丰富鲜艳，饱和度高，充满活力

基本要求：
- 适合儿童观看，健康正面的内容
- 富有创意和想象力
- 简洁清晰的构图
- 背景简洁干净，避免杂乱元素
- 主体突出，背景纯色或简单渐变
- 整体风格统一，色彩和谐
```

### Expert模式
用户输入：`一只猫`

实际发送给AI的prompt：
```
一只猫
```

## 日志输出

在控制台中可以看到明确的Expert模式标识：
```
🎨 开始使用真正的Nano Banana (gemini-2.5-flash-image)生成图片...
📝 提示词: 一只猫
🎨 风格: cute, 色彩偏好: colorful, Expert模式: True
⚡ Expert模式 - 原始prompt: 一只猫
```

## 兼容性

- 完全向后兼容：未勾选Expert模式时，系统行为与之前完全一致
- 不影响现有会话和版本管理功能
- 所有生成操作都支持Expert模式

## 测试建议

1. **基础测试**：勾选Expert模式，输入简单prompt，验证是否真的没有添加额外内容
2. **混合测试**：上传图片+文字描述，验证Expert模式在混合场景下的表现
3. **调整测试**：生成图片后，勾选Expert模式进行调整，验证调整功能
4. **切换测试**：在生成过程中切换Expert模式开关，确保每次都正确应用

## 注意事项

⚠️ **使用Expert模式时需要注意**：
- prompt需要足够详细和准确，因为不会有系统增强
- 可能需要多次调整prompt才能获得理想效果
- 不会自动过滤不适合儿童的内容（虽然AI本身有安全过滤）
- 风格和色彩偏好选项在Expert模式下会被忽略
