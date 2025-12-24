# 参考图片处理流程文档

## 概述
创作页面 (https://training.hlylsj.com/create/) 支持用户上传参考图片，可以通过三种方式添加图片，并支持两种主要使用场景。

---

## 1. 图片上传方式

### 1.1 三种上传入口
用户可通过以下三种方式添加参考图片：

#### 方式一：图片上传
- **触发**: 点击 `+` 按钮 → 选择"图片上传"
- **实现**: `triggerImageUpload()` → 触发隐藏的 `<input type="file" id="reference-image">`
- **文件类型**: `accept="image/*"`

#### 方式二：图片拍摄
- **触发**: 点击 `+` 按钮 → 选择"图片拍摄"
- **实现**: `captureImage()` → 触发 `<input type="file" id="camera-capture" capture="environment">`
- **特点**: 移动设备直接调用相机

#### 方式三：图片链接
- **触发**: 点击 `+` 按钮 → 选择"图片链接"
- **实现**: `showImageUrlDialog()` → 弹出对话框输入URL

### 1.2 上传处理流程

```javascript
// 前端处理 (static/js/create.js)
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        // 1. 存储文件对象到全局变量
        uploadedImageFile = file;
        
        // 2. 使用FileReader预览图片
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('uploaded-image').src = e.target.result;
            document.getElementById('uploaded-image-preview').style.display = 'block';
            // 显示快捷操作按钮
            document.getElementById('reference-quick-actions').style.display = 'block';
        };
        reader.readAsDataURL(file);
        
        // 3. 提示用户
        showMessage('图片上传成功！可以直接生成视频或3D模型', 'success');
    }
}
```

**关键变量**:
- `uploadedImageFile`: 全局变量，存储用户上传的File对象
- 此时文件仅在前端预览，**未上传到服务器**

---

## 2. 参考图片的两种使用场景

### 场景A: 文字+图片混合生成
**用途**: 结合文字描述和参考图片生成新图片

#### 前端流程
```javascript
// static/js/create.js - generateImage()
async function generateImage() {
    const prompt = document.getElementById('creation-prompt').value.trim();
    
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('style', style);
    
    // 添加参考图片（如果有）
    if (uploadedImageFile) {
        formData.append('sketch', uploadedImageFile);  // 字段名: sketch
    }
    
    // 发送到图片生成接口
    const response = await fetch('/api/generate-image', {
        method: 'POST',
        body: formData
    });
}
```

#### 后端处理
```python
# app/routes/api/generation.py
@generation_api_bp.route('/generate-image', methods=['POST'])
def api_generate_image():
    prompt = request.form.get('prompt', '').strip()
    style = request.form.get('style', 'cute')
    uploaded_file = request.files.get('sketch')  # 接收参考图片
    
    # 1. 保存上传的图片
    if uploaded_file and allowed_file(uploaded_file.filename):
        filename = str(uuid.uuid4()) + '_' + secure_filename(uploaded_file.filename)
        sketch_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(sketch_path)
        
        # 2. 预处理手绘图片（增强线条、去噪等）
        processed_sketch = preprocess_sketch(sketch_path)
        if processed_sketch:
            sketch_path = processed_sketch
    
    # 3. 调用AI生成
    result = nano_banana.generate_with_sketch(
        prompt=prompt,
        sketch_path=sketch_path,
        style=style,
        ...
    )
    
    return jsonify(result)
```

**流程图**:
```
用户上传图片 → 前端预览(FileReader) → 点击"生成图片"
  → 与prompt一起提交到 /api/generate-image
  → 后端保存文件 → 预处理图片 → 调用Nano Banana API
  → 返回生成结果
```

---

### 场景B: 参考图快捷操作
**用途**: 直接从参考图生成视频或3D模型，跳过图片生成步骤

#### B1. 生成视频
```javascript
// static/js/create.js
async function generateVideoFromReference() {
    if (!uploadedImageFile) {
        showMessage('请先上传参考图片', 'error');
        return;
    }
    
    // 1. 先上传参考图到服务器
    const formData = new FormData();
    formData.append('reference_image', uploadedImageFile);  // 字段名: reference_image
    
    const response = await fetch('/upload-reference-image', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    // 2. 获取服务器返回的图片URL
    const imageUrl = result.image_url;
    
    // 3. 跳转到视频生成页面，携带图片URL参数
    window.location.href = `/video?image_url=${imageUrl}&from_reference=true`;
}
```

#### B2. 生成3D模型
```javascript
// static/js/create.js
async function generate3DFromReference() {
    if (!uploadedImageFile) {
        showMessage('请先上传参考图片', 'error');
        return;
    }
    
    // 1. 先上传图片
    const uploadFormData = new FormData();
    uploadFormData.append('reference_image', uploadedImageFile);
    
    const uploadResponse = await fetch('/upload-reference-image', {
        method: 'POST',
        body: uploadFormData
    });
    
    const uploadResult = await uploadResponse.json();
    const imagePath = uploadResult.image_url;
    
    // 2. 使用上传后的图片路径生成3D模型
    const formData = new FormData();
    formData.append('image_path', imagePath);
    
    const response = await fetch('/generate-3d-model', {
        method: 'POST',
        body: formData
    });
    
    // 3. 显示3D模型结果
    const result = await response.json();
    if (result.success) {
        load3DModel(result.model_url);
        showStage(3);
    }
}
```

#### 后端上传接口
```python
# app/routes/model3d.py
@model3d_bp.route('/upload-reference-image', methods=['POST'])
def upload_reference_image():
    """上传参考图片并返回URL，用于直接生成视频或3D模型"""
    if 'reference_image' not in request.files:
        return jsonify({'success': False, 'error': '未找到上传的文件'}), 400
    
    file = request.files['reference_image']
    
    # 创建临时会话目录
    session_id = str(uuid.uuid4())
    session_dir = os.path.join('creation_sessions', session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # 保存上传的文件
    file_ext = os.path.splitext(file.filename)[1]
    filename = f'reference_image{file_ext}'
    filepath = os.path.join(session_dir, filename)
    file.save(filepath)
    
    # 构建URL
    image_url = url_for('static', filename=f'../creation_sessions/{session_id}/{filename}', _external=True)
    
    return jsonify({
        'success': True,
        'image_url': image_url,
        'session_id': session_id
    })
```

**流程图**:
```
用户上传图片 → 前端预览 → 点击"生成视频"或"生成3D"
  → 先调用 /upload-reference-image 上传图片
  → 获取服务器返回的 image_url
  → 携带URL调用后续功能（生成视频/3D模型）
```

---

## 3. 关键区别对比

| 对比项 | 场景A: 混合生成 | 场景B: 快捷操作 |
|--------|----------------|----------------|
| **字段名** | `sketch` | `reference_image` |
| **上传时机** | 与prompt一起提交 | 先单独上传 |
| **接口** | `/api/generate-image` | `/upload-reference-image` |
| **后续操作** | 直接生成图片 | 跳转到视频/3D页面 |
| **会话管理** | 由生成接口创建 | 上传时创建临时会话 |

---

## 4. UI展示

### 4.1 图片预览区域
```html
<!-- templates/create.html -->
<div id="uploaded-image-preview" class="image-preview" style="display: none;">
    <div class="preview-header">
        <span><i class="fas fa-image"></i> 参考图片</span>
        <button class="remove-image-btn" onclick="removeUploadedImage()">
            <i class="fas fa-times"></i>
        </button>
    </div>
    <img id="uploaded-image" src="" alt="上传的参考图片">
</div>
```

### 4.2 快捷操作按钮
上传图片后显示：
- **生成视频**: 直接从参考图生成视频
- **生成3D模型**: 直接从参考图生成3D模型

```html
<div id="reference-quick-actions" style="display: none;">
    <button onclick="generateVideoFromReference()">
        <i class="fas fa-video"></i> 生成视频
    </button>
    <button onclick="generate3DFromReference()">
        <i class="fas fa-cube"></i> 生成3D
    </button>
</div>
```

### 4.3 移除功能
```javascript
function removeUploadedImage() {
    uploadedImageFile = null;  // 清空全局变量
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('reference-image').value = '';  // 重置文件input
    document.getElementById('reference-quick-actions').style.display = 'none';
    showMessage('已移除参考图片', 'info');
}
```

---

## 5. 数据流总结

### 流程A: 文字+图片混合
```
用户选择文件
  ↓
前端: uploadedImageFile = File对象
  ↓
前端: FileReader 预览
  ↓
用户点击"生成图片"
  ↓
前端: FormData.append('sketch', uploadedImageFile)
  ↓
后端: /api/generate-image 接收 'sketch'
  ↓
后端: 保存文件 → 预处理 → AI生成
  ↓
返回生成结果
```

### 流程B: 快捷操作
```
用户选择文件
  ↓
前端: uploadedImageFile = File对象
  ↓
前端: FileReader 预览 + 显示快捷按钮
  ↓
用户点击"生成视频"或"生成3D"
  ↓
前端: FormData.append('reference_image', uploadedImageFile)
  ↓
后端: /upload-reference-image 接收 'reference_image'
  ↓
后端: 创建session → 保存文件 → 返回URL
  ↓
前端: 获取image_url
  ↓
跳转到视频页面 或 调用3D生成接口
```

---

## 6. 相关文件清单

### 前端文件
- **模板**: `templates/create.html` (HTML结构)
- **脚本**: `static/js/create.js` (核心逻辑)
- **样式**: `static/css/style.css`, `static/css/toast.css`

### 后端文件
- **图片生成**: `app/routes/api/generation.py` (接收 'sketch')
- **快捷上传**: `app/routes/model3d.py` (接收 'reference_image')
- **3D模型**: `app/routes/model3d.py` (生成3D模型)
- **API集成**: `api/nano_banana.py` (Nano Banana API)

### 辅助工具
- **图片预处理**: `utils/image_processor.py` (增强线条、去噪)
- **文件验证**: `app/utils.py` (allowed_file)

---

## 7. 优化建议

### 7.1 当前问题
1. **命名不一致**: 同一功能使用了两个字段名 (`sketch` vs `reference_image`)
2. **上传重复**: 快捷操作需要先上传一次，然后再传递URL
3. **会话管理**: 两种场景的会话管理方式不统一

### 7.2 优化方案
1. **统一字段名**: 建议统一使用 `reference_image` 或 `sketch`
2. **统一上传流程**: 
   - 用户上传后立即调用 `/upload-reference-image` 保存到服务器
   - 所有后续操作都使用返回的 `image_url`
   - 避免多次上传相同文件
3. **简化快捷操作**: 
   - 上传时自动获取session_id
   - 快捷按钮直接使用已有的image_url，无需再次上传

### 7.3 建议的新流程
```
用户选择文件
  ↓
前端: 立即调用 /upload-reference-image
  ↓
后端: 保存文件 → 返回 {image_url, session_id}
  ↓
前端: 存储 uploadedImageUrl 和 sessionId
  ↓
所有操作（生成图片/视频/3D）都使用 image_url
```

---

## 8. 测试检查清单

- [ ] 图片上传功能正常
- [ ] 图片拍摄功能正常（移动设备）
- [ ] 图片链接功能正常
- [ ] 预览显示正确
- [ ] 移除功能工作
- [ ] 文字+图片混合生成
- [ ] 快捷生成视频
- [ ] 快捷生成3D模型
- [ ] 文件类型验证
- [ ] 文件大小限制
- [ ] 错误提示准确

---

*最后更新: 2025-12-23*
