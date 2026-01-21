# 3D模型路径问题修复

## 问题描述
在"我的作品"页面查看3D模型时，提示"3D模型加载失败"。

## 根本原因
`Artwork.get_file_urls()` 方法在检查3D模型文件时，没有优先检查 `uploads/3d_models/` 子目录，导致返回的URL路径不正确。

### 文件存储结构：
- 图片文件：`uploads/{filename}` 
- 3D模型：`uploads/3d_models/{filename}` ✓ **新的统一路径**

### 问题流程：
1. 生成3D模型 → 保存到 `uploads/3d_models/model_xxx.glb`
2. 数据库保存：`artwork.model_3d = "model_xxx.glb"` （只存文件名）
3. 前端请求 → `get_file_urls()` 检查文件存在性
4. ❌ **问题**：先检查 `uploads/model_xxx.glb`（不存在）→ 返回错误的URL
5. 浏览器加载模型 → 404错误 → 显示"加载失败"

## 解决方案

### 修改文件：`auth/models.py`

在 `get_file_url()` 函数中添加3D模型文件的特殊处理：

```python
def get_file_url(filename):
    if not filename:
        return None
    
    # 如果文件名已经包含路径，直接使用
    if filename.startswith('/') or filename.startswith('http'):
        return filename
    
    # 优先检查 uploads/3d_models 目录（3D模型专用）
    if filename.endswith('.glb') or filename.endswith('.stl'):
        models_path = f"uploads/3d_models/{filename}"
        if os.path.exists(models_path):
            return f"/uploads/3d_models/{filename}"
    
    # 检查 uploads 目录（图片等其他文件）
    uploads_path = f"uploads/{filename}"
    if os.path.exists(uploads_path):
        return f"/uploads/{filename}"
    
    # ... 其他路径检查 ...
    
    # 如果都不存在，根据文件类型返回默认路径
    if filename.endswith('.glb') or filename.endswith('.stl'):
        return f"/uploads/3d_models/{filename}"
    else:
        return f"/uploads/{filename}"
```

### 修改文件：`static/js/artwork-modal.js`

增强错误提示，显示具体的路径和错误信息：

```javascript
onLoadError: (error) => {
    console.error('3D模型加载失败详情:', error);
    console.error('尝试加载的模型URL:', modelSrc);
    modelContainer.innerHTML = `
        <div style="...">
            <i class="fas fa-exclamation-triangle"></i>
            <p>3D模型加载失败</p>
            <p style="font-size: 0.9rem;">模型路径: ${modelSrc}</p>
            <p style="font-size: 0.9rem; color: #ff6b6b;">${error.message || error}</p>
            <p><a href="${modelSrc}" target="_blank">尝试下载模型文件</a></p>
        </div>
    `;
}
```

## 修复效果

### 修复前：
```
数据库: artwork.model_3d = "model_session123_v1.glb"
get_file_urls() 返回: "/uploads/model_session123_v1.glb" ❌ 错误路径
浏览器请求: GET /uploads/model_session123_v1.glb → 404
```

### 修复后：
```
数据库: artwork.model_3d = "model_session123_v1.glb"
get_file_urls() 检查: uploads/3d_models/model_session123_v1.glb ✓ 存在
get_file_urls() 返回: "/uploads/3d_models/model_session123_v1.glb" ✓ 正确路径
浏览器请求: GET /uploads/3d_models/model_session123_v1.glb → 200 OK
```

## 测试方法

1. 生成一个新的3D模型
2. 进入"我的作品"页面
3. 点击该作品，查看3D模型预览
4. 应该能正常加载并显示3D模型
5. 如果失败，查看浏览器控制台的错误信息（包含路径和具体错误）

## 相关文件

- `auth/models.py` - Artwork模型，get_file_urls()方法
- `api/hunyuan3d.py` - 3D模型生成，保存到uploads/3d_models/
- `app/routes/api_create.py` - API路由，设置artwork.model_3d
- `static/js/artwork-modal.js` - 前端模态框，加载3D模型
