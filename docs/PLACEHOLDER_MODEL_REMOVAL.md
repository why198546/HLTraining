# 3D模型占位符移除说明

## 问题描述

用户反馈在查看生成的3D作品时，显示的是占位的自行车模型，而不是实际生成的GLB文件。

## 根本原因

1. `model-viewer-3d.js` 中的 `createPlaceholderModel()` 函数在模型加载失败时会创建一个自行车形状的占位符模型
2. 当3D模型文件不存在或加载失败时，会自动显示占位模型，而不是提示用户错误

## 解决方案

### 1. 移除占位符模型生成逻辑

#### 文件：`static/js/model-viewer-3d.js`

**变更1：不支持的格式时返回错误**
```javascript
// 之前：显示占位模型
this.createPlaceholderModel();

// 现在：触发错误回调
if (this.onLoadError) {
    this.onLoadError(new Error('不支持的模型格式: ' + format));
}
```

**变更2：GLB解析失败时返回错误**
```javascript
// 之前：显示占位模型
this.createPlaceholderModel();

// 现在：触发错误回调
if (this.onLoadError) {
    this.onLoadError(error);
}
```

**变更3：完全删除 createPlaceholderModel 函数**
- 删除了约50行创建自行车占位符模型的代码
- 该函数不再被任何地方调用

### 2. 加强前端验证

#### 文件：`static/js/artwork-modal.js`

**变更1：只在有真实模型时显示3D模型预览**
```javascript
// 之前
if (artworkData.modelFile) {
    // 显示3D模型预览
}

// 现在
if (artworkData.modelFile && artworkData.modelFile.trim() !== '' && artworkData.modelFile !== 'null') {
    // 显示3D模型预览
}
```

**变更2：showModelModal函数添加空值检查**
```javascript
function showModelModal(modelSrc, title) {
    // 检查模型URL是否有效
    if (!modelSrc || modelSrc.trim() === '' || modelSrc === 'null') {
        alert('该作品没有3D模型文件');
        return;
    }
    // ... 继续加载模型
}
```

## 效果

1. **没有就没有**：如果作品没有3D模型，不会显示占位模型，也不会显示"查看3D模型"按钮
2. **错误提示**：如果尝试查看不存在的模型，会弹出友好的提示信息
3. **只显示真实内容**：只有真正生成的GLB文件才会在查看器中显示

## 测试建议

1. 查看没有3D模型的作品 → 不应该看到3D模型预览按钮
2. 查看有3D模型但文件丢失的作品 → 应该看到错误提示而不是占位模型
3. 查看正常的3D模型作品 → 应该正常加载并显示GLB模型

## 相关文件

- `static/js/model-viewer-3d.js` - 3D查看器核心逻辑
- `static/js/artwork-modal.js` - 作品详情模态框
- `templates/components/artwork_card.html` - 作品卡片模板（使用 model_3d 字段）
- `auth/models.py` - Artwork 模型的 get_file_urls() 方法

## 注意事项

- 占位符模型机制已完全移除，不会再自动创建假模型
- 所有模型加载失败都会通过 onLoadError 回调通知
- 前端会友好地处理空模型和加载失败的情况
