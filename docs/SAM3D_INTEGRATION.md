# SAM 3D 集成使用指南

## 概述

本项目已成功集成 Meta SAM 3D Objects 模型，用于从单张 2D 图片生成 3D 模型。SAM 3D 与现有的 Hunyuan3D 引擎并行部署，用户可以选择使用哪个引擎，或者对比两者的效果。

## 技术架构

### 部署方式

- **Hugging Face Spaces 集成**：通过 Hugging Face Inference API 调用 SAM 3D
- **自动降级**：如果 SAM 3D 失败，自动回退到 Hunyuan3D
- **并行部署**：两个引擎共存，互不影响

### 核心组件

1. **SAM 3D API 模块** (`api/sam3d_api.py`)
   - `SAM3DAPI` 类：封装所有 SAM 3D 相关功能
   - 自动图片预处理（RGBA 格式，mask 嵌入 alpha 通道）
   - 3D 格式转换（PLY → GLTF）
   - 自动降级机制

2. **Flask 路由** (`app.py`)
   - `/generate-3d-model-sam`: 使用 SAM 3D 生成 3D 模型
   - `/compare-3d-engines`: 对比 SAM 3D 和 Hunyuan3D
   - `/api/sam3d/info`: 获取 SAM 3D 模型信息

## API 使用说明

### 1. 使用 SAM 3D 生成 3D 模型

**端点**: `POST /generate-3d-model-sam`

**参数**:

```javascript
{
  image_path: string,      // 图片路径（必需）
  session_id: string,      // 会话ID（可选）
  version_note: string     // 版本备注（可选）
}
```

**响应**:

```javascript
{
  success: true,
  model_url: "/models/sam3d_model_xxx.gltf",
  version_id: "v_xxx",
  engine: "sam3d",  // 或 "hunyuan3d"（如果降级）
  message: "3D模型生成成功！(使用 sam3d)"
}
```

**示例**:

```javascript
const formData = new FormData();
formData.append('image_path', '/uploads/my_image.jpg');
formData.append('session_id', currentSessionId);

fetch('/generate-3d-model-sam', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('3D模型生成成功:', data.model_url);
    console.log('使用的引擎:', data.engine);
  }
});
```

### 2. 对比两个 3D 引擎

**端点**: `POST /compare-3d-engines`

**参数**:

```javascript
{
  image_path: string  // 图片路径（必需）
}
```

**响应**:

```javascript
{
  success: true,
  results: {
    sam3d: {
      success: true,
      model_url: "/models/sam3d_model_xxx.gltf",
      engine: "sam3d"
    },
    hunyuan3d: {
      success: true,
      model_url: "/uploads/hunyuan_model_xxx.gltf",
      engine: "hunyuan3d"
    }
  },
  message: "3D引擎对比完成"
}
```

### 3. 获取 SAM 3D 信息

**端点**: `GET /api/sam3d/info`

**响应**:

```javascript
{
  success: true,
  info: {
    name: "SAM 3D Objects",
    provider: "Meta AI",
    version: "1.0",
    method: "Hugging Face Spaces",
    input_format: "RGBA (mask in alpha channel)",
    output_format: "Gaussian Splat (.ply) -> GLTF",
    status: "experimental",
    note: "需要等待官方API支持或使用本地部署"
  }
}
```

## 前端集成建议

### 添加引擎选择器

在创作页面添加 3D 引擎选择：

```html
<div class="engine-selector">
  <label>选择 3D 引擎：</label>
  <select id="3d-engine-select">
    <option value="hunyuan3d">Hunyuan3D (当前)</option>
    <option value="sam3d">SAM 3D (Meta 最新)</option>
    <option value="compare">对比两者</option>
  </select>
</div>
```

### JavaScript 集成

```javascript
// 根据选择的引擎生成 3D 模型
async function generate3DModel(imagePath, engine) {
  let endpoint;
  
  switch(engine) {
    case 'sam3d':
      endpoint = '/generate-3d-model-sam';
      break;
    case 'hunyuan3d':
      endpoint = '/generate-3d-model';
      break;
    case 'compare':
      endpoint = '/compare-3d-engines';
      break;
    default:
      endpoint = '/generate-3d-model';
  }
  
  const formData = new FormData();
  formData.append('image_path', imagePath);
  
  const response = await fetch(endpoint, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

## 当前状态和限制

### ✅ 已实现

- SAM 3D API 模块完整实现
- 后端路由和自动降级机制
- 图片预处理和格式转换
- 与 Hunyuan3D 并行部署

### ⚠️ 重要提示

**SAM 3D 的 Hugging Face Inference API 可能还不可用**，因为模型刚刚发布。当前实现包含：

1. 完整的 API 调用框架
2. 自动降级到 Hunyuan3D 的机制
3. 错误处理和重试逻辑

如果 API 调用失败，系统会自动使用 Hunyuan3D 作为备用。

### 🔧 配置要求

1. **Hugging Face Token**（可选，提高速率限制）:

   ```bash
   export HUGGINGFACE_TOKEN="your-token-here"
   ```

2. **已安装依赖**:
   - huggingface-hub
   - gradio-client
   - trimesh
   - pygltflib

## 后续优化方向

1. **等待官方 API 支持**
   - 监控 Hugging Face 上 SAM 3D 的 Inference API 状态
   - 或者等待官方 Gradio Space 发布

2. **本地部署选项**（如果使用量大）
   - 需要 GPU 服务器
   - 安装 PyTorch 和 CUDA
   - 下载模型权重

3. **前端增强**
   - 添加引擎选择界面
   - 显示对比结果
   - 展示引擎性能指标

4. **智能引擎选择**
   - 根据图片内容自动选择最佳引擎
   - 基于历史数据优化选择

## 测试建议

1. **基础测试**:

   ```bash
   # 测试 SAM 3D API 信息
   curl http://localhost:5001/api/sam3d/info
   ```

2. **功能测试**:
   - 上传一张图片
   - 选择 SAM 3D 引擎
   - 观察是否自动降级到 Hunyuan3D
   - 检查生成的 3D 模型

3. **对比测试**:
   - 使用相同图片测试两个引擎
   - 比较生成速度和质量

## 故障排除

### 问题：SAM 3D 总是失败

**原因**: Hugging Face Inference API 可能还不支持 SAM 3D  
**解决**: 系统会自动降级到 Hunyuan3D，这是预期行为

### 问题：GLTF 转换失败

**原因**: PLY 文件格式不兼容  
**解决**: 检查 trimesh 库版本，确保 >= 4.0.0

### 问题：图片预处理错误

**原因**: 图片格式不支持或损坏  
**解决**: 确保图片是有效的 PNG/JPG 格式

## 联系和支持

如有问题或建议，请：

1. 查看日志输出（包含详细的调试信息）
2. 检查 Hugging Face 模型页面的最新状态
3. 参考 Meta SAM 3D 官方文档

---

**最后更新**: 2025-11-22  
**版本**: 1.0  
**状态**: 实验性功能，等待官方 API 支持
